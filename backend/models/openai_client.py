import time
from typing import Awaitable, Callable, List
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam, ChatCompletionChunk
from llm import Completion
from models.registry import ModelRegistry


async def stream_openai_response(
    messages: List[ChatCompletionMessageParam],
    api_key: str,
    base_url: str | None,
    callback: Callable[[str], Awaitable[None]],
    model_name: str,
) -> Completion:
    start_time = time.time()
    client = AsyncOpenAI(api_key=api_key, base_url=base_url)

    # Base parameters
    params = {"model": model_name, "messages": messages, "timeout": 600}

    llm = ModelRegistry.from_name(model_name)
    cfg = ModelRegistry.openai_params(llm)

    if cfg.supports_streaming:
        params["stream"] = True
    if cfg.supports_temperature and cfg.temperature is not None:
        params["temperature"] = cfg.temperature
    if cfg.max_tokens is not None:
        params["max_tokens"] = cfg.max_tokens
    if cfg.max_completion_tokens is not None:
        params["max_completion_tokens"] = cfg.max_completion_tokens
    if cfg.reasoning_effort is not None:
        params["reasoning_effort"] = cfg.reasoning_effort

    if not cfg.supports_streaming:
        response = await client.chat.completions.create(**params)  # type: ignore
        full_response = response.choices[0].message.content  # type: ignore
    else:
        stream = await client.chat.completions.create(**params)  # type: ignore
        full_response = ""
        async for chunk in stream:  # type: ignore
            assert isinstance(chunk, ChatCompletionChunk)
            if (
                chunk.choices
                and len(chunk.choices) > 0
                and chunk.choices[0].delta
                and chunk.choices[0].delta.content
            ):
                content = chunk.choices[0].delta.content or ""
                full_response += content
                await callback(content)

    await client.close()

    completion_time = time.time() - start_time
    return {"duration": completion_time, "code": full_response}
