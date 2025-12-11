"""
SVG extraction using Gemini 3 Pro Image.
Extracts design elements from original image and saves them as SVG.
"""
import base64
import json
from typing import Dict, Any
from google import genai
from google.genai import types


GEMINI_3_PRO_IMAGE_MODEL = "gemini-3-pro-nano-preview"  # Using Gemini 3 Pro Nano for image processing


async def extract_elements_as_svg(
    original_image_data_url: str,
    elements_data: Dict[str, Any],
    gemini_api_key: str,
) -> Dict[str, str]:
    """
    Extract each design element from original image as SVG using Gemini 3 Pro Image.
    
    Args:
        original_image_data_url: Base64 data URL of original image
        elements_data: Dictionary with elements and coordinates from extract_elements()
        gemini_api_key: Gemini API key
    
    Returns:
        Dictionary mapping element_id to SVG data URL
    """
    client = genai.Client(api_key=gemini_api_key)
    
    # Extract base64 data from data URL
    if original_image_data_url.startswith("data:"):
        base64_data = original_image_data_url.split(",")[1]
        mime_type = original_image_data_url.split(";")[0].split(":")[1]
    else:
        raise ValueError("Image must be provided as data URL")
    
    elements = elements_data.get("elements", [])
    svg_elements: Dict[str, str] = {}
    
    # Create a single prompt to extract all elements at once
    elements_list = []
    for element in elements:
        coords = element.get("coordinates", {})
        elements_list.append({
            "id": element.get("id"),
            "x": coords.get("x"),
            "y": coords.get("y"),
            "width": coords.get("width"),
            "height": coords.get("height"),
            "type": element.get("type"),
        })
    
    # Create prompt for batch extraction
    prompt_text = f"""
Extract all design elements from this image and convert each to SVG format.

Elements to extract:
{json.dumps(elements_list, indent=2)}

For each element:
1. Extract the exact visual content from the specified coordinates
2. Convert to SVG format preserving all visual properties (colors, gradients, shadows, etc.)
3. Return as a JSON object mapping element_id to SVG data URL

Return format:
{{
  "element_id_1": "data:image/svg+xml;base64,<base64_svg_data>",
  "element_id_2": "data:image/svg+xml;base64,<base64_svg_data>",
  ...
}}
"""
    
    try:
        # Use Gemini 3 Pro Image to extract elements
        response = await client.aio.models.generate_content(
            model=GEMINI_3_PRO_IMAGE_MODEL,
            contents=[
                {
                    "parts": [
                        types.Part.from_bytes(
                            data=base64.b64decode(base64_data),
                            mime_type=mime_type,
                        ),
                        {"text": prompt_text},
                    ]
                }
            ],
        )
        
        # Parse response
        if hasattr(response, 'candidates') and len(response.candidates) > 0:
            candidate = response.candidates[0]
            if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                for part in candidate.content.parts:
                    if hasattr(part, 'text'):
                        # Parse JSON response
                        json_text = part.text.strip()
                        if json_text.startswith("```"):
                            json_text = json_text.split("```")[1]
                            if json_text.startswith("json"):
                                json_text = json_text[4:]
                            json_text = json_text.strip().rstrip("```").strip()
                        
                        svg_elements = json.loads(json_text)
                        break
        
        return svg_elements
    except Exception as e:
        print(f"Error extracting SVG elements: {e}")
        # Fallback: return empty dict, will use placeholder images
        return {}

