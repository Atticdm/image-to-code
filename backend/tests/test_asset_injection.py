import base64

import pytest
from bs4 import BeautifulSoup

from image_generation.core import apply_image_cache, generate_images
from image_analysis.asset_extraction import extract_elements_as_assets


def _data_url_from_png_bytes(png_bytes: bytes) -> str:
    return f"data:image/png;base64,{base64.b64encode(png_bytes).decode('utf-8')}"


def test_apply_image_cache_replaces_placeholders_by_alt() -> None:
    html = '<html><body><img src="https://placehold.co/120x80" alt="el1"/></body></html>'
    out = apply_image_cache(html, {"el1": "data:image/png;base64,abc"})

    soup = BeautifulSoup(out, "html.parser")
    img = soup.find("img")
    assert img is not None
    assert img.get("src") == "data:image/png;base64,abc"
    assert img.get("width") == "120"
    assert img.get("height") == "80"


@pytest.mark.asyncio
async def test_generate_images_prefers_data_prompt(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    async def fake_process_tasks(prompts, api_key, base_url, model, gemini_api_key=None):
        captured["prompts"] = prompts
        return [f"https://example.com/{i}.png" for i in range(len(prompts))]

    import image_generation.core as core

    monkeypatch.setattr(core, "process_tasks", fake_process_tasks)

    html = (
        '<img src="https://placehold.co/10x10" alt="el1" data-prompt="a blue icon"/>'
        '<img src="https://placehold.co/20x30" alt="el2"/>'
    )
    out = await generate_images(
        html, api_key="k", base_url=None, image_cache={}, model="flux"
    )

    assert captured["prompts"] == ["a blue icon", "el2"]

    soup = BeautifulSoup(out, "html.parser")
    imgs = soup.find_all("img")
    assert imgs[0].get("src") == "https://example.com/0.png"
    assert imgs[0].get("width") == "10"
    assert imgs[0].get("height") == "10"
    assert imgs[1].get("src") == "https://example.com/1.png"
    assert imgs[1].get("width") == "20"
    assert imgs[1].get("height") == "30"


@pytest.mark.asyncio
async def test_extract_elements_as_assets_produces_transparency() -> None:
    import cv2  # type: ignore
    import numpy as np  # type: ignore

    bgr = np.full((100, 100, 3), 255, dtype=np.uint8)
    cv2.rectangle(bgr, (40, 40), (60, 60), (0, 0, 255), thickness=-1)
    ok, buf = cv2.imencode(".png", bgr)
    assert ok
    screenshot_data_url = _data_url_from_png_bytes(buf.tobytes())

    elements_data = {
        "image_dimensions": {"width": 100, "height": 100},
        "elements": [
            {
                "id": "rect1",
                "type": "image",
                "coordinates": {"x": 30, "y": 30, "width": 40, "height": 40},
            }
        ],
    }

    assets = await extract_elements_as_assets(screenshot_data_url, elements_data)
    assert "rect1" in assets
    asset_url = assets["rect1"]
    assert asset_url.startswith("data:image/png;base64,")

    _, b64 = asset_url.split(",", 1)
    out_bytes = base64.b64decode(b64)
    arr = np.frombuffer(out_bytes, dtype=np.uint8)
    rgba = cv2.imdecode(arr, cv2.IMREAD_UNCHANGED)
    assert rgba is not None
    assert rgba.ndim == 3 and rgba.shape[2] == 4

    alpha = rgba[:, :, 3]
    assert bool((alpha < 10).any())
    assert bool((alpha > 200).any())

