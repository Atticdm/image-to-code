from __future__ import annotations

import traceback
from typing import Awaitable, Callable

from pipeline.core import Middleware
from pipeline.ws import WebSocketCommunicator
from config import NUM_VARIANTS, SHOULD_MOCK_AI_RESPONSE

from pipeline.codegen.context import PipelineContext
from pipeline.codegen.stages.image_analysis import ImageAnalysisStage
from pipeline.codegen.stages.mock_response import MockResponseStage
from pipeline.codegen.stages.model_selection import ModelSelectionStage
from pipeline.codegen.stages.parallel_generation import ParallelGenerationStage
from pipeline.codegen.stages.parameter_extraction import ParameterExtractionStage
from pipeline.codegen.stages.post_processing import PostProcessingStage
from pipeline.codegen.stages.prompt_creation import PromptCreationStage
from pipeline.codegen.stages.video_generation import VideoGenerationStage


class WebSocketSetupMiddleware(Middleware[PipelineContext]):
    """Handles WebSocket setup and teardown."""

    async def process(
        self, context: PipelineContext, next_func: Callable[[], Awaitable[None]]
    ) -> None:
        context.ws_comm = WebSocketCommunicator(context.websocket)
        await context.ws_comm.accept()
        try:
            await next_func()
        finally:
            await context.ws_comm.close()


class ParameterExtractionMiddleware(Middleware[PipelineContext]):
    """Handles parameter extraction and validation."""

    async def process(
        self, context: PipelineContext, next_func: Callable[[], Awaitable[None]]
    ) -> None:
        assert context.ws_comm is not None
        context.params = await context.ws_comm.receive_params()

        param_extractor = ParameterExtractionStage(context.throw_error)
        context.extracted_params = await param_extractor.extract_and_validate(
            context.params
        )

        print(
            f"Generating {context.extracted_params.stack} code in {context.extracted_params.input_mode} mode"
        )

        await next_func()


class StatusBroadcastMiddleware(Middleware[PipelineContext]):
    """Sends initial status messages to all variants."""

    async def process(
        self, context: PipelineContext, next_func: Callable[[], Awaitable[None]]
    ) -> None:
        await context.send_message("variantCount", str(NUM_VARIANTS), 0)
        for i in range(NUM_VARIANTS):
            await context.send_message("status", "Generating code...", i)
        await next_func()


class PromptCreationMiddleware(Middleware[PipelineContext]):
    """Handles prompt creation."""

    async def process(
        self, context: PipelineContext, next_func: Callable[[], Awaitable[None]]
    ) -> None:
        assert context.extracted_params is not None

        if context.extracted_params.use_element_extraction:
            image_analysis_stage = ImageAnalysisStage(
                send_message=context.send_message,
                throw_error=context.throw_error,
            )

            image_url = context.extracted_params.prompt["images"][0]
            elements_data, element_assets = await image_analysis_stage.analyze_image(
                image_data_url=image_url,
                analysis_model=context.extracted_params.analysis_model or "",
                openai_api_key=context.extracted_params.openai_api_key,
                anthropic_api_key=context.extracted_params.anthropic_api_key,
                gemini_api_key=context.extracted_params.gemini_api_key,
            )

            context.extracted_elements = elements_data
            context.element_assets = element_assets

            prompt_creator = PromptCreationStage(context.throw_error)
            context.prompt_messages, context.image_cache = (
                await prompt_creator.create_prompt(
                    context.extracted_params,
                    elements_data=elements_data,
                    element_assets=element_assets,
                )
            )
        else:
            prompt_creator = PromptCreationStage(context.throw_error)
            context.prompt_messages, context.image_cache = (
                await prompt_creator.create_prompt(context.extracted_params)
            )

        await next_func()


class CodeGenerationMiddleware(Middleware[PipelineContext]):
    """Handles the main code generation logic."""

    async def process(
        self, context: PipelineContext, next_func: Callable[[], Awaitable[None]]
    ) -> None:
        if SHOULD_MOCK_AI_RESPONSE:
            mock_stage = MockResponseStage(context.send_message)
            assert context.extracted_params is not None
            context.completions = await mock_stage.generate_mock_response(
                context.extracted_params.input_mode
            )
        else:
            try:
                assert context.extracted_params is not None
                if context.extracted_params.input_mode == "video":
                    video_stage = VideoGenerationStage(
                        context.send_message, context.throw_error
                    )
                    context.completions = await video_stage.generate_video_code(
                        context.prompt_messages,
                        context.extracted_params.anthropic_api_key,
                    )
                else:
                    model_selector = ModelSelectionStage(context.throw_error)
                    context.variant_models = await model_selector.select_models(
                        generation_type=context.extracted_params.generation_type,
                        input_mode=context.extracted_params.input_mode,
                        openai_api_key=context.extracted_params.openai_api_key,
                        anthropic_api_key=context.extracted_params.anthropic_api_key,
                        gemini_api_key=context.extracted_params.gemini_api_key,
                        preferred_model=context.extracted_params.code_generation_model,
                    )

                    generation_stage = ParallelGenerationStage(
                        send_message=context.send_message,
                        openai_api_key=context.extracted_params.openai_api_key,
                        openai_base_url=context.extracted_params.openai_base_url,
                        anthropic_api_key=context.extracted_params.anthropic_api_key,
                        gemini_api_key=context.extracted_params.gemini_api_key,
                        should_generate_images=context.extracted_params.should_generate_images,
                    )

                    context.variant_completions = (
                        await generation_stage.process_variants(
                            variant_models=context.variant_models,
                            prompt_messages=context.prompt_messages,
                            image_cache=context.image_cache,
                            params=context.params,
                        )
                    )

                    if len(context.variant_completions) == 0:
                        await context.throw_error(
                            "Error generating code. Please contact support."
                        )
                        return

                    context.completions = []
                    for i in range(len(context.variant_models)):
                        context.completions.append(
                            context.variant_completions.get(i, "")
                        )
            except Exception as e:
                print(f"[GENERATE_CODE] Unexpected error: {e}")
                traceback.print_exception(type(e), e, e.__traceback__)
                await context.throw_error(f"An unexpected error occurred: {str(e)}")
                return

        await next_func()


class PostProcessingMiddleware(Middleware[PipelineContext]):
    """Handles post-processing and logging."""

    async def process(
        self, context: PipelineContext, next_func: Callable[[], Awaitable[None]]
    ) -> None:
        post_processor = PostProcessingStage()
        await post_processor.process_completions(
            context.completions, context.prompt_messages, context.websocket
        )
        await next_func()
