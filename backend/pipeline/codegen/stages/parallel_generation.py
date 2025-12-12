from __future__ import annotations

import asyncio
import traceback
from typing import Any, Callable, Coroutine, Dict, List

import openai
from openai.types.chat import ChatCompletionMessageParam

from codegen.utils import extract_html_content
from config import IS_PROD, REPLICATE_API_KEY
from image_generation.core import apply_image_cache, generate_images
from llm import Completion, Llm, OPENAI_MODELS, ANTHROPIC_MODELS, GEMINI_MODELS
from models import stream_claude_response, stream_gemini_response, stream_openai_response
from pipeline.codegen.context import VariantErrorAlreadySent
from pipeline.types import MessageType


class ParallelGenerationStage:
    """Parallel variant generation with independent processing per variant."""

    def __init__(
        self,
        send_message: Callable[[MessageType, str, int], Coroutine[Any, Any, None]],
        openai_api_key: str | None,
        openai_base_url: str | None,
        anthropic_api_key: str | None,
        gemini_api_key: str | None,
        should_generate_images: bool,
    ):
        self.send_message = send_message
        self.openai_api_key = openai_api_key
        self.openai_base_url = openai_base_url
        self.anthropic_api_key = anthropic_api_key
        self.gemini_api_key = gemini_api_key
        self.should_generate_images = should_generate_images

    async def process_variants(
        self,
        variant_models: List[Llm],
        prompt_messages: List[ChatCompletionMessageParam],
        image_cache: Dict[str, str],
        params: Dict[str, Any],
    ) -> Dict[int, str]:
        tasks = self._create_generation_tasks(variant_models, prompt_messages, params)

        variant_tasks: Dict[int, asyncio.Task[Completion]] = {}
        variant_completions: Dict[int, str] = {}

        for index, task in enumerate(tasks):
            variant_tasks[index] = asyncio.create_task(task)

        variant_processors = [
            self._process_variant_completion(
                index,
                task,
                variant_models[index],
                image_cache,
                variant_completions,
            )
            for index, task in variant_tasks.items()
        ]

        await asyncio.gather(*variant_processors, return_exceptions=True)
        return variant_completions

    def _create_generation_tasks(
        self,
        variant_models: List[Llm],
        prompt_messages: List[ChatCompletionMessageParam],
        params: Dict[str, Any],
    ) -> List[Coroutine[Any, Any, Completion]]:
        tasks: List[Coroutine[Any, Any, Completion]] = []

        for index, model in enumerate(variant_models):
            if model in OPENAI_MODELS:
                if self.openai_api_key is None:
                    raise Exception("OpenAI API key is missing.")
                tasks.append(
                    self._stream_openai_with_error_handling(
                        prompt_messages, model_name=model.value, index=index
                    )
                )
            elif self.gemini_api_key and model in GEMINI_MODELS:
                tasks.append(
                    stream_gemini_response(
                        prompt_messages,
                        api_key=self.gemini_api_key,
                        callback=lambda x, i=index: self._process_chunk(x, i),
                        model_name=model.value,
                    )
                )
            elif model in ANTHROPIC_MODELS:
                if self.anthropic_api_key is None:
                    raise Exception("Anthropic API key is missing.")
                tasks.append(
                    stream_claude_response(
                        prompt_messages,
                        api_key=self.anthropic_api_key,
                        callback=lambda x, i=index: self._process_chunk(x, i),
                        model_name=model.value,
                    )
                )

        return tasks

    async def _process_chunk(self, content: str, variant_index: int):
        await self.send_message("chunk", content, variant_index)

    async def _stream_openai_with_error_handling(
        self,
        prompt_messages: List[ChatCompletionMessageParam],
        model_name: str,
        index: int,
    ) -> Completion:
        try:
            assert self.openai_api_key is not None
            return await stream_openai_response(
                prompt_messages,
                api_key=self.openai_api_key,
                base_url=self.openai_base_url,
                callback=lambda x: self._process_chunk(x, index),
                model_name=model_name,
            )
        except openai.AuthenticationError as e:
            print(f"[VARIANT {index + 1}] OpenAI Authentication failed", e)
            error_message = (
                "Incorrect OpenAI key. Please make sure your OpenAI API key is correct, "
                "or create a new OpenAI API key on your OpenAI dashboard."
                + (
                    " Alternatively, you can purchase code generation credits directly on this website."
                    if IS_PROD
                    else ""
                )
            )
            await self.send_message("variantError", error_message, index)
            raise VariantErrorAlreadySent(e)
        except openai.NotFoundError as e:
            print(f"[VARIANT {index + 1}] OpenAI Model not found", e)
            error_message = (
                e.message
                + ". Please make sure you have followed the instructions correctly to obtain "
                "an OpenAI key with GPT vision access: "
                "https://github.com/abi/screenshot-to-code/blob/main/Troubleshooting.md"
                + (
                    " Alternatively, you can purchase code generation credits directly on this website."
                    if IS_PROD
                    else ""
                )
            )
            await self.send_message("variantError", error_message, index)
            raise VariantErrorAlreadySent(e)
        except openai.RateLimitError as e:
            print(f"[VARIANT {index + 1}] OpenAI Rate limit exceeded", e)
            error_message = (
                "OpenAI error - 'You exceeded your current quota, please check your plan and billing details.'"
                + (
                    " Alternatively, you can purchase code generation credits directly on this website."
                    if IS_PROD
                    else ""
                )
            )
            await self.send_message("variantError", error_message, index)
            raise VariantErrorAlreadySent(e)

    async def _perform_image_generation(
        self,
        completion: str,
        image_cache: dict[str, str],
    ):
        completion = apply_image_cache(completion, image_cache)
        if not self.should_generate_images:
            return completion

        replicate_api_key = REPLICATE_API_KEY

        if self.gemini_api_key:
            image_generation_model = "gemini-3-pro-nano"
            api_key = self.gemini_api_key
            gemini_key = self.gemini_api_key
        elif replicate_api_key:
            image_generation_model = "flux"
            api_key = replicate_api_key
            gemini_key = None
        else:
            if not self.openai_api_key:
                print(
                    "No Gemini, OpenAI, or Replicate API key found. Skipping image generation."
                )
                return completion
            image_generation_model = "dalle3"
            api_key = self.openai_api_key
            gemini_key = None

        print("Generating images with model: ", image_generation_model)

        return await generate_images(
            completion,
            api_key=api_key,
            base_url=self.openai_base_url,
            image_cache=image_cache,
            model=image_generation_model,
            gemini_api_key=gemini_key,
        )

    async def _process_variant_completion(
        self,
        index: int,
        task: asyncio.Task[Completion],
        model: Llm,
        image_cache: Dict[str, str],
        variant_completions: Dict[int, str],
    ):
        try:
            completion = await task
            print(f"{model.value} completion took {completion['duration']:.2f} seconds")
            variant_completions[index] = completion["code"]

            try:
                processed_html = await self._perform_image_generation(
                    completion["code"], image_cache
                )
                processed_html = extract_html_content(processed_html)
                await self.send_message("setCode", processed_html, index)
                await self.send_message(
                    "variantComplete", "Variant generation complete", index
                )
            except Exception as inner_e:
                print(f"Post-processing error for variant {index + 1}: {inner_e}")
        except Exception as e:
            print(f"Error in variant {index + 1}: {e}")
            traceback.print_exception(type(e), e, e.__traceback__)
            if not isinstance(e, VariantErrorAlreadySent):
                await self.send_message("variantError", str(e), index)
