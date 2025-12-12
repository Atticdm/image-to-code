"""
Deterministic asset extraction from screenshots.

This is the "cheap scissors" implementation:
  - Uses element bounding boxes from `extract_elements()`
  - Uses OpenCV GrabCut (no ML weights) to estimate a foreground mask
  - Produces PNG data URLs with transparency (non-rectangular alpha)

This avoids relying on Gemini for "SVG extraction", and it guarantees that the
foreground pixels come from the original screenshot (within the estimated mask).
"""

from __future__ import annotations

import base64
from typing import Any, Dict, Tuple

import cv2  # type: ignore
import numpy as np  # type: ignore


def _decode_image_data_url(image_data_url: str) -> Tuple[np.ndarray, str]:
    if not image_data_url.startswith("data:"):
        raise ValueError("Image must be provided as data URL")
    header, b64 = image_data_url.split(",", 1)
    mime_type = header.split(";")[0].split(":")[1]
    image_bytes = base64.b64decode(b64)
    arr = np.frombuffer(image_bytes, dtype=np.uint8)
    bgr = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if bgr is None:
        raise ValueError("Failed to decode image")
    return bgr, mime_type


def _encode_png_data_url(rgba: np.ndarray) -> str:
    ok, buf = cv2.imencode(".png", rgba)
    if not ok:
        raise ValueError("Failed to encode PNG")
    b64 = base64.b64encode(buf.tobytes()).decode("utf-8")
    return f"data:image/png;base64,{b64}"


def _clamp_bbox(
    x: int, y: int, w: int, h: int, img_w: int, img_h: int
) -> Tuple[int, int, int, int]:
    x = max(0, min(x, img_w - 1))
    y = max(0, min(y, img_h - 1))
    w = max(1, min(w, img_w - x))
    h = max(1, min(h, img_h - y))
    return x, y, w, h


def _grabcut_alpha(roi_bgr: np.ndarray) -> np.ndarray:
    h, w = roi_bgr.shape[:2]

    # Initialize mask with "probably background".
    mask = np.full((h, w), cv2.GC_PR_BGD, dtype=np.uint8)

    # Mark a thin border as definite background.
    border = max(2, int(min(h, w) * 0.06))
    mask[:border, :] = cv2.GC_BGD
    mask[-border:, :] = cv2.GC_BGD
    mask[:, :border] = cv2.GC_BGD
    mask[:, -border:] = cv2.GC_BGD

    # Mark the center as probable foreground.
    inset = max(3, int(min(h, w) * 0.18))
    if inset * 2 < h and inset * 2 < w:
        mask[inset : h - inset, inset : w - inset] = cv2.GC_PR_FGD

    bg_model = np.zeros((1, 65), np.float64)
    fg_model = np.zeros((1, 65), np.float64)

    # Run a small number of iterations for speed; can be increased if needed.
    cv2.grabCut(roi_bgr, mask, None, bg_model, fg_model, 2, cv2.GC_INIT_WITH_MASK)

    alpha = np.where(
        (mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD),
        255,
        0,
    ).astype(np.uint8)

    # Light morphological smoothing to reduce jagged edges.
    k = max(1, int(min(h, w) * 0.02))
    if k % 2 == 0:
        k += 1
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k))
    alpha = cv2.morphologyEx(alpha, cv2.MORPH_OPEN, kernel)
    alpha = cv2.GaussianBlur(alpha, (k, k), 0)

    return alpha


async def extract_elements_as_assets(
    original_image_data_url: str,
    elements_data: Dict[str, Any],
) -> Dict[str, str]:
    """
    Extract each design element as a transparent PNG data URL.

    Returns:
        Dict mapping element_id -> data:image/png;base64,...
    """
    bgr, _ = _decode_image_data_url(original_image_data_url)
    img_h, img_w = bgr.shape[:2]

    elements = elements_data.get("elements", [])
    assets: Dict[str, str] = {}

    # Heuristic: treat a very large element as background and skip.
    full_area = float(img_w * img_h) if img_w and img_h else 1.0

    for element in elements:
        element_id = element.get("id")
        coords = element.get("coordinates", {}) or {}
        if not element_id:
            continue

        try:
            x = int(coords.get("x", 0))
            y = int(coords.get("y", 0))
            w = int(coords.get("width", 0))
            h = int(coords.get("height", 0))
        except Exception:
            continue

        if w <= 0 or h <= 0:
            continue

        element_type = str(element.get("type", "")).lower()
        text_content = element.get("text_content")

        # Prefer real DOM text; don't turn it into an image asset by default.
        if element_type == "text" and text_content:
            continue

        # Skip likely background layer.
        if element_type == "background" or (w * h) / full_area > 0.80:
            continue

        x, y, w, h = _clamp_bbox(x, y, w, h, img_w, img_h)
        roi_bgr = bgr[y : y + h, x : x + w]
        if roi_bgr.size == 0:
            continue

        try:
            alpha = _grabcut_alpha(roi_bgr)
            roi_bgra = cv2.cvtColor(roi_bgr, cv2.COLOR_BGR2BGRA)
            roi_bgra[:, :, 3] = alpha
            assets[element_id] = _encode_png_data_url(roi_bgra)
        except Exception:
            # Best effort: skip this asset rather than failing the whole run.
            continue

    return assets

