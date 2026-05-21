"""
MuAPI Gemini Omni ComfyUI Nodes
================================
Focused nodes for Gemini Omni video generation via muapi.ai.

  GeminiOmniTextToVideo     — POST /api/v1/gemini-omni-text-to-video
  GeminiOmniImageToVideo    — POST /api/v1/gemini-omni-image-to-video
  GeminiOmniVideoEdit       — POST /api/v1/gemini-omni-video-edit
  GeminiOmniCreateAudio     — POST /api/v1/gemini-omni-audio
  GeminiOmniCreateCharacter — POST /api/v1/gemini-omni-character

Auth:     x-api-key header
Polling:  GET /api/v1/predictions/{request_id}/result
Upload:   POST /api/v1/upload_file
"""

import io, json, os, time
import numpy as np
import requests
import torch
from PIL import Image

BASE_URL = "https://api.muapi.ai/api/v1"
POLL_INTERVAL = 10
MAX_WAIT = 900

AUDIO_IDS = [
    "(none)",
    "achernar", "achird", "algenib", "algieba", "alnilam", "aoede", "autonoe",
    "callirrhoe", "charon", "despina", "enceladus", "erinome", "fenrir", "gacrux",
    "iapetus", "kore", "laomedeia", "leda", "orus", "puck", "pulcherrima",
    "rasalgethi", "sadachbia", "sadaltager", "schedar", "sulafat", "umbriel",
    "vindemiatrix", "zephyr", "zubenelgenubi",
]

RESOLUTIONS = ["720p", "1080p", "4k"]

_NONE = "(none)"


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _load_api_key(api_key: str) -> str:
    key = (api_key or "").strip()
    if key:
        return key
    cfg = os.path.expanduser("~/.muapi/config.json")
    if os.path.exists(cfg):
        try:
            return json.load(open(cfg)).get("api_key", "")
        except Exception:
            pass
    raise ValueError("No API key found. Pass one into the node or run `muapi auth login`.")


def _headers(api_key: str) -> dict:
    return {"x-api-key": _load_api_key(api_key)}


def _upload_image(tensor: torch.Tensor, api_key: str) -> str:
    """Upload a ComfyUI IMAGE tensor and return its public URL."""
    img = tensor[0].cpu().numpy()
    img = (img * 255).clip(0, 255).astype(np.uint8)
    pil = Image.fromarray(img)
    buf = io.BytesIO()
    pil.save(buf, format="PNG")
    buf.seek(0)
    resp = requests.post(
        f"{BASE_URL}/upload_file",
        headers=_headers(api_key),
        files={"file": ("image.png", buf, "image/png")},
        timeout=120,
    )
    _check(resp)
    return resp.json()["url"]


def _upload_video(path_or_url: str, api_key: str) -> str:
    """Return URL as-is if it's already a URL, else upload the local file."""
    if path_or_url.startswith("http://") or path_or_url.startswith("https://"):
        return path_or_url
    with open(path_or_url, "rb") as f:
        resp = requests.post(
            f"{BASE_URL}/upload_file",
            headers=_headers(api_key),
            files={"file": (os.path.basename(path_or_url), f)},
            timeout=300,
        )
    _check(resp)
    return resp.json()["url"]


def _submit(endpoint: str, payload: dict, api_key: str) -> str:
    resp = requests.post(
        f"{BASE_URL}/{endpoint}",
        headers={**_headers(api_key), "Content-Type": "application/json"},
        json=payload,
        timeout=60,
    )
    _check(resp)
    return resp.json()["request_id"]


def _poll(request_id: str, api_key: str) -> str:
    deadline = time.time() + MAX_WAIT
    while time.time() < deadline:
        r = requests.get(
            f"{BASE_URL}/predictions/{request_id}/result",
            headers=_headers(api_key),
            timeout=30,
        )
        _check(r)
        data = r.json()
        status = data.get("status", "")
        if status == "completed":
            outputs = data.get("outputs", [])
            if outputs:
                return outputs[0]
            raise RuntimeError(f"Job {request_id} completed but outputs list is empty")
        if status in ("failed", "cancelled"):
            raise RuntimeError(f"Job {request_id} ended with status: {status}")
        time.sleep(POLL_INTERVAL)
    raise TimeoutError(f"Job {request_id} did not complete within {MAX_WAIT}s")


def _check(resp: requests.Response):
    if resp.status_code == 401:
        raise PermissionError("Invalid API key — check your MuAPI key at muapi.ai")
    if resp.status_code == 402:
        raise RuntimeError("Insufficient credits — top up at muapi.ai/topup")
    if resp.status_code == 429:
        raise RuntimeError("Rate limited — reduce request frequency")
    resp.raise_for_status()


def _collect_audio_ids(*ids) -> list:
    """Collect up to 3 optional audio ID strings, filtering out _NONE and empty."""
    return [a for a in ids if a and a != _NONE]


def _collect_character_ids(*ids) -> list:
    """Collect up to 3 optional character ID strings, filtering out empty values."""
    return [c for c in ids if c and c.strip()]


# ---------------------------------------------------------------------------
# Node: GeminiOmniApiKey
# ---------------------------------------------------------------------------

class GeminiOmniApiKey:
    """Store and validate your MuAPI key for Gemini Omni nodes."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "placeholder": "muapi_…  (or leave blank to use ~/.muapi/config.json)",
                }),
            }
        }

    RETURN_TYPES = ("GEMINI_OMNI_API_KEY",)
    RETURN_NAMES = ("api_key",)
    FUNCTION = "load"
    CATEGORY = "MuAPI/Gemini Omni"

    def load(self, api_key):
        key = _load_api_key(api_key)
        return (key,)


# ---------------------------------------------------------------------------
# Node: GeminiOmniTextToVideo
# ---------------------------------------------------------------------------

class GeminiOmniTextToVideo:
    """Generate video from a text prompt using Gemini Omni."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key": ("GEMINI_OMNI_API_KEY",),
                "prompt": ("STRING", {"multiline": True, "default": ""}),
                "duration": ([4, 6, 8, 10], {"default": 8}),
                "aspect_ratio": (["16:9", "9:16"], {"default": "16:9"}),
                "resolution": (RESOLUTIONS, {"default": "1080p"}),
            },
            "optional": {
                "audio_id_1": (AUDIO_IDS, {"default": _NONE}),
                "audio_id_2": (AUDIO_IDS, {"default": _NONE}),
                "audio_id_3": (AUDIO_IDS, {"default": _NONE}),
                "character_id_1": ("STRING", {"default": ""}),
                "character_id_2": ("STRING", {"default": ""}),
                "character_id_3": ("STRING", {"default": ""}),
                "seed": ("INT", {"default": -1, "min": -1, "max": 2147483647}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("video_url", "request_id")
    FUNCTION = "generate"
    CATEGORY = "MuAPI/Gemini Omni"

    def generate(
        self, api_key, prompt, duration, aspect_ratio, resolution,
        audio_id_1=_NONE, audio_id_2=_NONE, audio_id_3=_NONE,
        character_id_1="", character_id_2="", character_id_3="",
        seed=-1,
    ):
        payload = {
            "prompt": prompt,
            "duration": duration,
            "aspect_ratio": aspect_ratio,
            "resolution": resolution,
        }
        audio_ids = _collect_audio_ids(audio_id_1, audio_id_2, audio_id_3)
        if audio_ids:
            payload["audio_ids"] = audio_ids
        character_ids = _collect_character_ids(character_id_1, character_id_2, character_id_3)
        if character_ids:
            payload["character_ids"] = character_ids
        if seed >= 0:
            payload["seed"] = seed

        request_id = _submit("gemini-omni-text-to-video", payload, api_key)
        video_url = _poll(request_id, api_key)
        return (video_url, request_id)


# ---------------------------------------------------------------------------
# Node: GeminiOmniImageToVideo
# ---------------------------------------------------------------------------

class GeminiOmniImageToVideo:
    """Animate one or more reference images with Gemini Omni (up to 5 images)."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key": ("GEMINI_OMNI_API_KEY",),
                "prompt": ("STRING", {"multiline": True, "default": ""}),
                "image_1": ("IMAGE",),
                "duration": ([4, 6, 8, 10], {"default": 8}),
                "aspect_ratio": (["16:9", "9:16"], {"default": "16:9"}),
                "resolution": (RESOLUTIONS, {"default": "1080p"}),
            },
            "optional": {
                "image_2": ("IMAGE",),
                "image_3": ("IMAGE",),
                "image_4": ("IMAGE",),
                "image_5": ("IMAGE",),
                "audio_id_1": (AUDIO_IDS, {"default": _NONE}),
                "audio_id_2": (AUDIO_IDS, {"default": _NONE}),
                "audio_id_3": (AUDIO_IDS, {"default": _NONE}),
                "character_id_1": ("STRING", {"default": ""}),
                "character_id_2": ("STRING", {"default": ""}),
                "character_id_3": ("STRING", {"default": ""}),
                "seed": ("INT", {"default": -1, "min": -1, "max": 2147483647}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("video_url", "request_id")
    FUNCTION = "generate"
    CATEGORY = "MuAPI/Gemini Omni"

    def generate(
        self, api_key, prompt, image_1, duration, aspect_ratio, resolution,
        image_2=None, image_3=None, image_4=None, image_5=None,
        audio_id_1=_NONE, audio_id_2=_NONE, audio_id_3=_NONE,
        character_id_1="", character_id_2="", character_id_3="",
        seed=-1,
    ):
        tensors = [image_1, image_2, image_3, image_4, image_5]
        image_urls = [_upload_image(t, api_key) for t in tensors if t is not None]

        payload = {
            "prompt": prompt,
            "image_urls": image_urls,
            "duration": duration,
            "aspect_ratio": aspect_ratio,
            "resolution": resolution,
        }
        audio_ids = _collect_audio_ids(audio_id_1, audio_id_2, audio_id_3)
        if audio_ids:
            payload["audio_ids"] = audio_ids
        character_ids = _collect_character_ids(character_id_1, character_id_2, character_id_3)
        if character_ids:
            payload["character_ids"] = character_ids
        if seed >= 0:
            payload["seed"] = seed

        request_id = _submit("gemini-omni-image-to-video", payload, api_key)
        video_url = _poll(request_id, api_key)
        return (video_url, request_id)


# ---------------------------------------------------------------------------
# Node: GeminiOmniVideoEdit
# ---------------------------------------------------------------------------

class GeminiOmniVideoEdit:
    """
    Edit or restyle a source video and/or reference images with Gemini Omni.

    Slot budget: 7 total — the video uses 2 slots, so at most 5 image_urls
    when a video is also provided.

    At least one of video_url or image_1 must be connected.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key": ("GEMINI_OMNI_API_KEY",),
                "prompt": ("STRING", {"multiline": True, "default": ""}),
                "duration": ([4, 6, 8, 10], {"default": 8}),
                "aspect_ratio": (["16:9", "9:16"], {"default": "16:9"}),
                "resolution": (RESOLUTIONS, {"default": "1080p"}),
                "trim_start": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 29.0, "step": 0.5}),
                "trim_end": ("FLOAT", {"default": 8.0, "min": 0.5, "max": 30.0, "step": 0.5}),
            },
            "optional": {
                "video_url": ("STRING", {"default": "", "multiline": False,
                                         "placeholder": "https://… or /path/to/clip.mp4"}),
                "image_1": ("IMAGE",),
                "image_2": ("IMAGE",),
                "image_3": ("IMAGE",),
                "image_4": ("IMAGE",),
                "image_5": ("IMAGE",),
                "audio_id_1": (AUDIO_IDS, {"default": _NONE}),
                "audio_id_2": (AUDIO_IDS, {"default": _NONE}),
                "audio_id_3": (AUDIO_IDS, {"default": _NONE}),
                "character_id_1": ("STRING", {"default": ""}),
                "character_id_2": ("STRING", {"default": ""}),
                "character_id_3": ("STRING", {"default": ""}),
                "seed": ("INT", {"default": -1, "min": -1, "max": 2147483647}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("video_url", "request_id")
    FUNCTION = "generate"
    CATEGORY = "MuAPI/Gemini Omni"

    def generate(
        self, api_key, prompt, duration, aspect_ratio, resolution, trim_start, trim_end,
        video_url="", image_1=None, image_2=None, image_3=None, image_4=None,
        image_5=None,
        audio_id_1=_NONE, audio_id_2=_NONE, audio_id_3=_NONE,
        character_id_1="", character_id_2="", character_id_3="",
        seed=-1,
    ):
        video_url = (video_url or "").strip()
        image_tensors = [t for t in [image_1, image_2, image_3, image_4, image_5] if t is not None]

        if not video_url and not image_tensors:
            raise ValueError("Connect at least one of video_url or image_1")

        if trim_end - trim_start > 10:
            raise ValueError("trim_end − trim_start must not exceed 10 seconds")
        if trim_end <= trim_start:
            raise ValueError("trim_end must be greater than trim_start")

        payload: dict = {
            "prompt": prompt,
            "duration": duration,
            "aspect_ratio": aspect_ratio,
            "resolution": resolution,
            "trim_start": trim_start,
            "trim_end": trim_end,
        }

        if video_url:
            payload["video_url"] = _upload_video(video_url, api_key)

        if image_tensors:
            payload["image_urls"] = [_upload_image(t, api_key) for t in image_tensors]

        audio_ids = _collect_audio_ids(audio_id_1, audio_id_2, audio_id_3)
        if audio_ids:
            payload["audio_ids"] = audio_ids
        character_ids = _collect_character_ids(character_id_1, character_id_2, character_id_3)
        if character_ids:
            payload["character_ids"] = character_ids
        if seed >= 0:
            payload["seed"] = seed

        request_id = _submit("gemini-omni-video-edit", payload, api_key)
        out_url = _poll(request_id, api_key)
        return (out_url, request_id)


# ---------------------------------------------------------------------------
# Node: GeminiOmniCreateAudio
# ---------------------------------------------------------------------------

class GeminiOmniCreateAudio:
    """Create a custom Gemini Omni audio voice profile."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key": ("GEMINI_OMNI_API_KEY",),
                "audio_id": (AUDIO_IDS, {"default": _NONE}),
                "name": ("STRING", {"default": "", "multiline": False}),
            },
            "optional": {
                "voice_description": ("STRING", {"default": "", "multiline": True}),
                "example_dialogue": ("STRING", {"default": ""}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("kie_audio_id", "profile_name")
    FUNCTION = "generate"
    CATEGORY = "MuAPI/Gemini Omni"

    def generate(self, api_key, audio_id, name, voice_description="", example_dialogue=""):
        payload = {
            "audio_id": audio_id,
            "name": name[:210],
        }
        if voice_description:
            payload["voice_description"] = voice_description
        if example_dialogue:
            payload["example_dialogue"] = example_dialogue

        request_id = _submit("gemini-omni-audio", payload, api_key)
        raw_output = _poll(request_id, api_key)

        try:
            data = json.loads(raw_output)
            kie_audio_id = data.get("kieAudioId", raw_output)
            profile_name = data.get("name", name)
        except Exception:
            kie_audio_id = raw_output
            profile_name = name

        return (kie_audio_id, profile_name)


# ---------------------------------------------------------------------------
# Node: GeminiOmniCreateCharacter
# ---------------------------------------------------------------------------

class GeminiOmniCreateCharacter:
    """Create a Gemini Omni character from a reference image."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key": ("GEMINI_OMNI_API_KEY",),
                "image": ("IMAGE",),
                "descriptions": ("STRING", {"multiline": True, "default": ""}),
            },
            "optional": {
                "character_name": ("STRING", {"default": ""}),
                "audio_id_1": ("STRING", {"default": ""}),
                "audio_id_2": ("STRING", {"default": ""}),
                "audio_id_3": ("STRING", {"default": ""}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("character_id", "character_name", "character_image_url")
    FUNCTION = "generate"
    CATEGORY = "MuAPI/Gemini Omni"

    def generate(
        self, api_key, image, descriptions,
        character_name="", audio_id_1="", audio_id_2="", audio_id_3="",
    ):
        image_url = _upload_image(image, api_key)

        payload = {
            "images_list": [image_url],
            "descriptions": descriptions,
        }
        if character_name:
            payload["character_name"] = character_name

        audio_ids = _collect_character_ids(audio_id_1, audio_id_2, audio_id_3)
        if audio_ids:
            payload["audio_ids"] = audio_ids

        request_id = _submit("gemini-omni-character", payload, api_key)
        raw_output = _poll(request_id, api_key)

        try:
            data = json.loads(raw_output)
            char_id = data.get("characterId", raw_output)
            char_name = data.get("characterName", character_name)
            char_image = data.get("image", "")
        except Exception:
            char_id = raw_output
            char_name = character_name
            char_image = ""

        return (char_id, char_name, char_image)


# ---------------------------------------------------------------------------
# ComfyUI registration
# ---------------------------------------------------------------------------

NODE_CLASS_MAPPINGS = {
    "GeminiOmniApiKey": GeminiOmniApiKey,
    "GeminiOmniTextToVideo": GeminiOmniTextToVideo,
    "GeminiOmniImageToVideo": GeminiOmniImageToVideo,
    "GeminiOmniVideoEdit": GeminiOmniVideoEdit,
    "GeminiOmniCreateAudio": GeminiOmniCreateAudio,
    "GeminiOmniCreateCharacter": GeminiOmniCreateCharacter,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "GeminiOmniApiKey": "Gemini Omni API Key",
    "GeminiOmniTextToVideo": "Gemini Omni Text to Video",
    "GeminiOmniImageToVideo": "Gemini Omni Image to Video",
    "GeminiOmniVideoEdit": "Gemini Omni Video Edit",
    "GeminiOmniCreateAudio": "Gemini Omni Create Audio Profile",
    "GeminiOmniCreateCharacter": "Gemini Omni Create Character",
}
