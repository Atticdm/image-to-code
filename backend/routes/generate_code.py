from fastapi import APIRouter, WebSocket

from pipeline.core import Pipeline
from pipeline.codegen.context import PipelineContext
from pipeline.codegen.middlewares import (
    CodeGenerationMiddleware,
    ParameterExtractionMiddleware,
    PostProcessingMiddleware,
    PromptCreationMiddleware,
    StatusBroadcastMiddleware,
    WebSocketSetupMiddleware,
)

router = APIRouter()


@router.websocket("/generate-code")
async def stream_code(websocket: WebSocket):
    """Handle WebSocket code generation requests using the codegen pipeline."""
    pipeline: Pipeline[PipelineContext] = Pipeline(lambda ws: PipelineContext(websocket=ws))

    pipeline.use(WebSocketSetupMiddleware())
    pipeline.use(ParameterExtractionMiddleware())
    pipeline.use(StatusBroadcastMiddleware())
    pipeline.use(PromptCreationMiddleware())
    pipeline.use(CodeGenerationMiddleware())
    pipeline.use(PostProcessingMiddleware())

    await pipeline.execute(websocket)
