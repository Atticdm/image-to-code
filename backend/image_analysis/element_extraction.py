"""
Element extraction from images using AI models.
Analyzes image and extracts design elements with coordinates.
"""
import json
from typing import Dict, List, Any, Optional
from openai.types.chat import ChatCompletionMessageParam
from llm import Llm
from models import stream_openai_response, stream_claude_response, stream_gemini_response
from config import OPENAI_API_KEY, ANTHROPIC_API_KEY, GEMINI_API_KEY


ELEMENT_EXTRACTION_SYSTEM_PROMPT = """
You are an expert at analyzing web design screenshots and identifying all design elements.

Analyze the provided screenshot and create a JSON structure listing all design elements with their:
- Element type (background, text, image, button, menu, header, footer, card, icon, etc.)
- Exact coordinates (x, y, width, height) in pixels
- Visual properties (colors, fonts, sizes)
- Text content (if applicable)
- Layer/position information

Return ONLY valid JSON in this format:
{
  "image_dimensions": {"width": number, "height": number},
  "elements": [
    {
      "id": "unique_id",
      "type": "element_type",
      "coordinates": {"x": number, "y": number, "width": number, "height": number},
      "properties": {
        "background_color": "hex_color",
        "text_color": "hex_color",
        "font_size": number,
        "font_family": "font_name",
        "border_radius": number,
        "opacity": number
      },
      "text_content": "text if applicable",
      "z_index": number
    }
  ]
}

Be extremely precise with coordinates. Every visible element should be included.
"""


async def extract_elements(
    image_data_url: str,
    analysis_model: Llm,
    openai_api_key: Optional[str] = None,
    anthropic_api_key: Optional[str] = None,
    gemini_api_key: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Extract design elements from image using specified model.
    
    Returns:
        Dictionary with image dimensions and list of elements with coordinates
    """
    # Create prompt messages
    prompt_messages: List[ChatCompletionMessageParam] = [
        {
            "role": "system",
            "content": ELEMENT_EXTRACTION_SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {"url": image_data_url, "detail": "high"},
                },
                {
                    "type": "text",
                    "text": "Analyze this screenshot and extract all design elements with their exact coordinates.",
                },
            ],
        },
    ]
    
    # Call appropriate model
    full_response = ""
    
    async def collect_chunk(chunk: str):
        nonlocal full_response
        full_response += chunk
    
    if analysis_model in OPENAI_MODELS and openai_api_key:
        completion = await stream_openai_response(
            prompt_messages,
            api_key=openai_api_key,
            base_url=None,
            callback=collect_chunk,
            model_name=analysis_model.value,
        )
    elif analysis_model in ANTHROPIC_MODELS and anthropic_api_key:
        completion = await stream_claude_response(
            prompt_messages,
            api_key=anthropic_api_key,
            callback=collect_chunk,
            model_name=analysis_model.value,
        )
    elif analysis_model in GEMINI_MODELS and gemini_api_key:
        completion = await stream_gemini_response(
            prompt_messages,
            api_key=gemini_api_key,
            callback=collect_chunk,
            model_name=analysis_model.value,
        )
    else:
        raise ValueError(f"Model {analysis_model.value} not supported or API key missing")
    
    # Parse JSON response
    try:
        # Extract JSON from response (might have markdown code blocks)
        json_text = full_response.strip()
        if json_text.startswith("```"):
            # Remove markdown code blocks
            json_text = json_text.split("```")[1]
            if json_text.startswith("json"):
                json_text = json_text[4:]
            json_text = json_text.strip()
        elif json_text.startswith("```json"):
            json_text = json_text[7:].strip().rstrip("```").strip()
        
        elements_data = json.loads(json_text)
        return elements_data
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON response: {e}")
        print(f"Response was: {full_response[:500]}")
        raise ValueError(f"Invalid JSON response from model: {e}")

