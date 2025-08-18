import base64
import logging
from typing import List, Tuple, Optional

import requests
from django.conf import settings
from django.core.exceptions import ValidationError


logger = logging.getLogger(__name__)


class StabilityAIError(Exception):
    pass


def _headers() -> dict:
    api_key = settings.STABILITY_API_KEY
    if not api_key:
        raise StabilityAIError("Clé API Stability manquante. Définissez STABILITY_API_KEY dans votre .env")
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def validate_prompt(prompt: str) -> str:
    if not prompt or not prompt.strip():
        raise StabilityAIError("Prompt cannot be empty")
    clean = prompt.strip()
    if len(clean) < 3:
        raise StabilityAIError("Prompt must be at least 3 characters long")
    if len(clean) > 1000:
        raise StabilityAIError("Prompt is too long (maximum 1000 characters)")
    harmful_words = ['hack', 'exploit', 'virus', 'malware', 'spam']
    lower = clean.lower()
    if any(w in lower for w in harmful_words):
        raise StabilityAIError("Prompt contains inappropriate content")
    return clean


def generate_images(
    prompt: str,
    *,
    cfg_scale: int | None = None,
    steps: int | None = None,
    width: int | None = None,
    height: int | None = None,
    samples: int = 1,
) -> List[Tuple[bytes, str]]:
    """
    Appelle l'API Stability AI pour générer des images.

    Retourne une liste de tuples (image_bytes, extension_sans_point),
    ex: (b'...png bytes...', 'png').
    """
    # Validate prompt first
    prompt = validate_prompt(prompt)

    # Use explicit URL if provided, otherwise default to XL-1024 v1.0 endpoint
    explicit_url = getattr(settings, 'STABILITY_API_URL', None)
    url = _build_generation_url(engine=None, explicit_url=explicit_url)

    # Determine dimensions with model-specific constraints
    effective_width = width or getattr(settings, "STABILITY_DEFAULT_WIDTH", 1024)
    effective_height = height or getattr(settings, "STABILITY_DEFAULT_HEIGHT", 1024)
    eff_w, eff_h = _normalize_dimensions_for_url(url, effective_width, effective_height)

    payload = {
        "text_prompts": [{"text": prompt}],
        "cfg_scale": cfg_scale or getattr(settings, "STABILITY_DEFAULT_CFG_SCALE", 7),
        "height": eff_h,
        "width": eff_w,
        "samples": samples,
        "steps": steps or getattr(settings, "STABILITY_DEFAULT_STEPS", 30),
    }

    response = requests.post(url, headers=_headers(), json=payload, timeout=60)
    images = _parse_generation_response(response)
    if images is not None:
        return images

    # Gestion d'erreurs explicites
    if response.status_code in (401,):
        raise StabilityAIError("Invalid API key. Please check your configuration.")
    if response.status_code in (403,):
        raise StabilityAIError("API access denied. Please check your account status.")
    if response.status_code in (429,):
        raise StabilityAIError("Rate limit exceeded. Please try again later.")
    if response.status_code in (500,):
        raise StabilityAIError("Stability AI service is currently unavailable. Please try again later.")

    # 404: engine not found or bad path
    if response.status_code == 404:
        raise StabilityAIError("The selected model/endpoint was not found. Use a valid STABILITY_API_URL (e.g. stable-diffusion-xl-1024-v1-0 or stable-diffusion-v1-6) or check your account access.")

    # Si on arrive ici: lever une erreur détaillée
    try:
        err = response.json()
    except Exception:
        err = {"error": response.text}
    raise StabilityAIError(f"Erreur API Stability ({response.status_code}): {err}")


def _build_generation_url(*, engine: Optional[str], explicit_url: Optional[str]) -> str:
    # Always prefer explicit URL per user config/snippet; otherwise default to the XL endpoint
    if explicit_url:
        return explicit_url
    return "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"


def _parse_generation_response(response: requests.Response) -> Optional[List[Tuple[bytes, str]]]:
    content_type = response.headers.get("Content-Type", "")
    if response.status_code >= 400:
        return None

    # Cas JSON avec 'artifacts' (base64)
    if "application/json" in content_type:
        data = response.json()
        artifacts = data.get("artifacts") or data.get("images") or []
        images: List[Tuple[bytes, str]] = []
        for artifact in artifacts:
            b64 = artifact.get("base64") or artifact.get("b64_json") or artifact.get("image") or artifact.get("img")
            if not b64:
                continue
            try:
                image_bytes = base64.b64decode(b64)
            except Exception:
                continue
            images.append((image_bytes, _guess_ext(artifact)))
        return images

    # Cas image binaire (png/jpeg)
    if any(t in content_type for t in ("image/png", "image/jpeg", "application/octet-stream")):
        ext = "png" if "png" in content_type else ("jpg" if "jpeg" in content_type else "bin")
        return [(response.content, ext)]

    # Par défaut essayer json
    try:
        data = response.json()
        artifacts = data.get("artifacts", [])
        images: List[Tuple[bytes, str]] = []
        for artifact in artifacts:
            b64 = artifact.get("base64") or artifact.get("b64_json")
            if b64:
                images.append((base64.b64decode(b64), _guess_ext(artifact)))
        return images
    except Exception:
        return None


def _normalize_dimensions_for_url(url: str, width: int, height: int) -> tuple[int, int]:
    """Clamp/adjust dimensions to model-allowed sizes.
    For SDXL endpoints, only specific pairs are allowed. Choose 1024x1024 if invalid.
    """
    if 'stable-diffusion-xl-1024' in url:
        allowed = {
            (1024, 1024), (1152, 896), (1216, 832), (1344, 768), (1536, 640),
            (640, 1536), (768, 1344), (832, 1216), (896, 1152)
        }
        if (width, height) not in allowed:
            logger.info(
                "Adjusting dimensions from %sx%s to 1024x1024 for SDXL endpoint",
                width, height
            )
            return (1024, 1024)
    return (width, height)


def _guess_ext(artifact: dict) -> str:
    mime = artifact.get("mime") or artifact.get("media_type") or ""
    if "png" in mime:
        return "png"
    if "jpeg" in mime or "jpg" in mime:
        return "jpg"
    return "png"


