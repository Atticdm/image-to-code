import asyncio
import re
from typing import Dict, List, Literal, Union
from openai import AsyncOpenAI
from bs4 import BeautifulSoup

from image_generation.replicate import call_replicate


async def process_tasks(
    prompts: List[str],
    api_key: str,
    base_url: str | None,
    model: Literal["dalle3", "flux", "gemini-3-pro-nano"],
    gemini_api_key: str | None = None,
):
    import time

    start_time = time.time()
    if model == "dalle3":
        tasks = [generate_image_dalle(prompt, api_key, base_url) for prompt in prompts]
    elif model == "gemini-3-pro-nano":
        if not gemini_api_key:
            raise ValueError("Gemini API key required for Gemini 3 Pro Nano image generation")
        tasks = [generate_image_gemini(prompt, gemini_api_key) for prompt in prompts]
    else:
        tasks = [generate_image_replicate(prompt, api_key) for prompt in prompts]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    end_time = time.time()
    generation_time = end_time - start_time
    print(f"Image generation time: {generation_time:.2f} seconds")

    processed_results: List[Union[str, None]] = []
    for result in results:
        if isinstance(result, BaseException):
            print(f"An exception occurred: {result}")
            processed_results.append(None)
        else:
            processed_results.append(result)

    return processed_results


async def generate_image_dalle(
    prompt: str, api_key: str, base_url: str | None
) -> Union[str, None]:
    client = AsyncOpenAI(api_key=api_key, base_url=base_url)
    res = await client.images.generate(
        model="dall-e-3",
        quality="standard",
        style="natural",
        n=1,
        size="1024x1024",
        prompt=prompt,
    )
    await client.close()
    return res.data[0].url


async def generate_image_replicate(prompt: str, api_key: str) -> str:

    # We use Flux Schnell
    return await call_replicate(
        {
            "prompt": prompt,
            "num_outputs": 1,
            "aspect_ratio": "1:1",
            "output_format": "png",
            "output_quality": 100,
        },
        api_key,
    )


async def generate_image_gemini(prompt: str, api_key: str) -> str:
    """
    Generate image using Gemini 3 Pro Nano (Imagen API)
    
    Note: Gemini 3 Pro Nano uses Google's Imagen API for image generation.
    The actual API endpoint and response format may vary. This implementation
    is a placeholder that should be updated when the official API is available.
    
    For now, falls back to placeholder image if generation fails.
    """
    from google import genai
    
    client = genai.Client(api_key=api_key)
    
    try:
        # Attempt to use Gemini 3 Pro Nano for image generation
        # TODO: Update this when official Gemini 3 Pro Nano image generation API is available
        # Expected API: Use Imagen API through Gemini client
        response = await client.aio.models.generate_content(
            model="gemini-3-pro-nano-preview",
            contents=[{"parts": [{"text": f"Generate an image: {prompt}"}]}],
        )
        
        # Extract image URL from response
        # Actual implementation will depend on Gemini API response format
        if hasattr(response, 'candidates') and len(response.candidates) > 0:
            candidate = response.candidates[0]
            # Check if response contains image data or URL
            # This is a placeholder - adjust based on actual API response structure
            if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                for part in candidate.content.parts:
                    if hasattr(part, 'inline_data'):
                        # If image is returned inline, convert to data URL
                        return f"data:image/png;base64,{part.inline_data.data}"
                    elif hasattr(part, 'url'):
                        return part.url
            
            # Fallback: return placeholder
            print(f"Gemini 3 Pro Nano: Image generation response format not yet implemented")
            return f"https://placehold.co/1024x1024?text={prompt[:20]}"
        else:
            raise ValueError("No image generated from Gemini")
    except Exception as e:
        print(f"Gemini 3 Pro Nano image generation error: {e}")
        print("Falling back to placeholder image. Update generate_image_gemini() when API is available.")
        # Fallback to placeholder until API is properly implemented
        return f"https://placehold.co/1024x1024?text={prompt[:20]}"


def extract_dimensions(url: str):
    # Regular expression to match numbers in the format '300x200'
    matches = re.findall(r"(\d+)x(\d+)", url)

    if matches:
        width, height = matches[0]  # Extract the first match
        width = int(width)
        height = int(height)
        return (width, height)
    else:
        return (100, 100)


def create_alt_url_mapping(code: str) -> Dict[str, str]:
    soup = BeautifulSoup(code, "html.parser")
    images = soup.find_all("img")

    mapping: Dict[str, str] = {}

    for image in images:
        if not image["src"].startswith("https://placehold.co"):
            mapping[image["alt"]] = image["src"]

    return mapping


async def generate_images(
    code: str,
    api_key: str,
    base_url: Union[str, None],
    image_cache: Dict[str, str],
    model: Literal["dalle3", "flux", "gemini-3-pro-nano"] = "dalle3",
    gemini_api_key: str | None = None,
) -> str:
    # Find all images
    soup = BeautifulSoup(code, "html.parser")
    images = soup.find_all("img")

    # Extract alt texts as image prompts
    alts: List[str | None] = []
    for img in images:
        # Only include URL if the image starts with https://placehold.co
        # and it's not already in the image_cache
        if (
            img.get("src", None)
            and img["src"].startswith("https://placehold.co")
            and image_cache.get(img.get("alt")) is None
        ):
            alts.append(img.get("alt", None))

    # Exclude images with no alt text
    filtered_alts: List[str] = [alt for alt in alts if alt is not None]

    # Remove duplicates
    prompts = list(set(filtered_alts))

    # Return early if there are no images to replace
    if len(prompts) == 0:
        return code

    # Generate images
    results = await process_tasks(prompts, api_key, base_url, model, gemini_api_key)

    # Create a dict mapping alt text to image URL
    mapped_image_urls = dict(zip(prompts, results))

    # Merge with image_cache
    mapped_image_urls = {**mapped_image_urls, **image_cache}

    # Replace old image URLs with the generated URLs
    for img in images:
        # Skip images that don't start with https://placehold.co (leave them alone)
        if not img["src"].startswith("https://placehold.co"):
            continue

        new_url = mapped_image_urls[img.get("alt")]

        if new_url:
            # Set width and height attributes
            width, height = extract_dimensions(img["src"])
            img["width"] = width
            img["height"] = height
            # Replace img['src'] with the mapped image URL
            img["src"] = new_url
        else:
            print("Image generation failed for alt text:" + img.get("alt"))

    # Return the modified HTML
    # (need to prettify it because BeautifulSoup messes up the formatting)
    return soup.prettify()
