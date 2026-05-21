# Google Gemini Omni ComfyUI Nodes

> **ComfyUI custom nodes for Google Gemini Omni** — Google's natively multimodal any-to-any video generation model.
> Generate, animate, and edit AI videos directly inside ComfyUI using the [muapi.ai](https://muapi.ai) Gemini Omni API.
> For REST API documentation and Python examples see [Gemini Omni API](https://github.com/Anil-matcha/Awesome-Gemini-Omni-API-Prompts)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![ComfyUI](https://img.shields.io/badge/ComfyUI-Custom%20Node-blue)](https://github.com/comfyanonymous/ComfyUI)
[![Google Gemini Omni](https://img.shields.io/badge/Model-Google%20Gemini%20Omni-green)](https://muapi.ai)
[![Google AI](https://img.shields.io/badge/Powered%20by-Google%20AI-orange)](https://muapi.ai)

---

## What is Google Gemini Omni?

**Google Gemini Omni** is Google's natively multimodal any-to-any video generation model, capable of producing high-quality videos from text, images, or existing video clips. Accessed via the [Gemini Omni API](https://muapi.ai), it supports:

- **Text-to-Video** — generate video from a text description with optional AI voiceover
- **Image-to-Video** — animate up to 5 reference images using the Gemini Omni image-to-video API
- **Video Edit** — restyle or transform an existing video clip with the Gemini Omni video editing API

These ComfyUI nodes wrap the Google Gemini Omni API so you can use the model directly inside ComfyUI workflows without writing any code.

---

## Nodes

| Node | Description |
|------|-------------|
| 🔑 Gemini Omni API Key | Set your muapi.ai key once — wire to all nodes |
| 🎬 Gemini Omni Text to Video | Generate video from a text prompt via Google Gemini Omni |
| 🎬 Gemini Omni Image to Video | Animate up to 5 reference images with Gemini Omni |
| 🎬 Gemini Omni Video Edit | Restyle a video clip with Gemini Omni video editing |
| 🎤 Gemini Omni Create Audio Profile | Create a custom AI voice profile for use in generation nodes |
| 🧑 Gemini Omni Create Character | Create a character from a reference image for use in generation nodes |
| 💾 Gemini Omni Video Saver | Download video URL → disk + ComfyUI IMAGE frames |

---

## Installation

### Via ComfyUI Manager (recommended)
1. Open **ComfyUI Manager** → **Install via Git URL**
2. Paste: `https://github.com/Anil-matcha/gemini-omni-comfyui`
3. Restart ComfyUI

### Manual
```bash
cd ComfyUI/custom_nodes
git clone https://github.com/Anil-matcha/gemini-omni-comfyui
pip install -r gemini-omni-comfyui/requirements.txt
```

---

## Quick Start

1. Sign up at [muapi.ai](https://muapi.ai) and go to **Dashboard → API Keys → Create Key**
2. Right-click the ComfyUI canvas → **Add Node** → **MuAPI/Gemini Omni**
3. Add a **🔑 Gemini Omni API Key** node, paste your key, and wire its output to any generation node
4. Write a prompt and hit **Queue Prompt**

> **Tip:** If you use the [MuAPI CLI](https://github.com/SamurAIGPT/muapi-cli), run `muapi auth configure --api-key YOUR_KEY` once and all nodes will pick it up automatically — no need to paste the key anywhere.

---

## Node Reference

### 🔑 Gemini Omni API Key

Set your muapi.ai API key once and wire the output to all Gemini Omni generation nodes. Alternatively, leave every `api_key` field blank — nodes automatically read from `~/.muapi/config.json` if you've authenticated via the CLI.

---

### 🎬 Gemini Omni Text to Video

Generate a video from a text description using the Google Gemini Omni text-to-video API.

| Field | Values | Default |
|-------|--------|---------|
| `api_key` | Wire from API Key node or leave blank for CLI config | — |
| `prompt` | Text describing the video | — |
| `duration` | 4 / 6 / 8 / 10 seconds | 8 |
| `aspect_ratio` | 16:9 / 9:16 | 16:9 |
| `resolution` | 720p / 1080p / 4k | 1080p |
| `audio_id_1` … `audio_id_3` | (none) or one of 30 Google Gemini AI voice names — up to 3 voices | (none) |
| `character_id_1` … `character_id_3` | Optional — character IDs from Create Character node — up to 3 | — |
| `seed` | -1 (random) or 0–2147483647 | -1 |

**Outputs:** `video_url` (STRING) · `request_id` (STRING)

---

### 🎬 Gemini Omni Image to Video

Animate up to 5 reference images into a video using the Google Gemini Omni image-to-video API.

| Field | Values | Default |
|-------|--------|---------|
| `api_key` | Wire from API Key node | — |
| `prompt` | Text describing the animation | — |
| `image_1` | Required — ComfyUI IMAGE tensor | — |
| `image_2` … `image_5` | Optional — additional reference images | — |
| `duration` | 4 / 6 / 8 / 10 seconds | 8 |
| `aspect_ratio` | 16:9 / 9:16 | 16:9 |
| `resolution` | 720p / 1080p / 4k | 1080p |
| `audio_id_1` … `audio_id_3` | (none) or one of 30 Google Gemini AI voice names — up to 3 voices | (none) |
| `character_id_1` … `character_id_3` | Optional — character IDs from Create Character node — up to 3 | — |
| `seed` | -1 (random) or 0–2147483647 | -1 |

**Outputs:** `video_url` (STRING) · `request_id` (STRING)

---

### 🎬 Gemini Omni Video Edit

Restyle or transform a video clip using the Google Gemini Omni video editing API. Optionally supply up to 5 reference images alongside the video (7 total slots — video uses 2, each image uses 1). At least one of `video_url` or `image_1` must be connected.

| Field | Values | Default |
|-------|--------|---------|
| `api_key` | Wire from API Key node | — |
| `prompt` | Editing instruction | — |
| `duration` | 4 / 6 / 8 / 10 seconds | 8 |
| `aspect_ratio` | 16:9 / 9:16 | 16:9 |
| `resolution` | 720p / 1080p / 4k | 1080p |
| `trim_start` | 0.0 – 29.0 (seconds) | 0.0 |
| `trim_end` | 0.5 – 30.0 (seconds, max window 10s) | 8.0 |
| `video_url` | Optional — HTTPS URL or local file path | — |
| `image_1` … `image_5` | Optional — reference images (max 5 with video) | — |
| `audio_id_1` … `audio_id_3` | (none) or one of 30 Google Gemini AI voice names — up to 3 voices | (none) |
| `character_id_1` … `character_id_3` | Optional — character IDs from Create Character node — up to 3 | — |
| `seed` | -1 (random) or 0–2147483647 | -1 |

**Outputs:** `video_url` (STRING) · `request_id` (STRING)

---

### 🎤 Gemini Omni Create Audio Profile

Create a custom Gemini Omni AI voice profile. The resulting `kie_audio_id` can be passed into the `audio_id_1` … `audio_id_3` fields of the generation nodes.

| Field | Values | Default |
|-------|--------|---------|
| `api_key` | Wire from API Key node | — |
| `audio_id` | One of 30 Google Gemini AI voice names (base voice to customise) | — |
| `name` | Profile display name (max 210 characters) | — |
| `voice_description` | Optional — text description of the voice style | — |
| `example_dialogue` | Optional — example speech for the voice | — |

**Outputs:** `kie_audio_id` (STRING) · `profile_name` (STRING)

---

### 🧑 Gemini Omni Create Character

Create a Gemini Omni character from a reference image. The resulting `character_id` can be passed into the `character_id_1` … `character_id_3` fields of the generation nodes.

| Field | Values | Default |
|-------|--------|---------|
| `api_key` | Wire from API Key node | — |
| `image` | ComfyUI IMAGE tensor — reference image for the character | — |
| `descriptions` | Text description of the character | — |
| `character_name` | Optional — display name for the character | — |
| `audio_id_1` … `audio_id_3` | Optional — voice IDs to associate with this character | — |

**Outputs:** `character_id` (STRING) · `character_name` (STRING) · `character_image_url` (STRING)

---

### 💾 Gemini Omni Video Saver

Download a Gemini Omni output video URL to disk and decode frames as a ComfyUI IMAGE tensor for downstream processing.

| Field | Values | Default |
|-------|--------|---------|
| `video_url` | Wire from any Gemini Omni generation node | — |
| `prefix` | Output filename prefix | `gemini_omni` |
| `save_subfolder` | Subfolder under `ComfyUI/output/` | `gemini_omni` |
| `frame_load_cap` | Max frames to load (0 = all) | 0 |
| `skip_first_frames` | Skip N frames from the start | 0 |
| `select_every_nth` | Load every Nth frame | 1 |

**Outputs:** `frames` (IMAGE) · `filepath` (STRING) · `frame_count` (INT)

---

## Audio Voices

When `audio_id` is set, a Google Gemini AI voice narrates or accompanies the generated video. Available voices:

`achernar` · `achird` · `algenib` · `algieba` · `alnilam` · `aoede` · `autonoe` · `callirrhoe` · `charon` · `despina` · `enceladus` · `erinome` · `fenrir` · `gacrux` · `iapetus` · `kore` · `laomedeia` · `leda` · `orus` · `puck` · `pulcherrima` · `rasalgethi` · `sadachbia` · `sadaltager` · `schedar` · `sulafat` · `umbriel` · `vindemiatrix` · `zephyr` · `zubenelgenubi`

---

## Example Workflows

Import any of these into ComfyUI via **Load** or drag-and-drop:

- [`GeminiOmni_T2V_Example.json`](workflows/GeminiOmni_T2V_Example.json) — Google Gemini Omni Text to Video
- [`GeminiOmni_I2V_Example.json`](workflows/GeminiOmni_I2V_Example.json) — Google Gemini Omni Image to Video
- [`GeminiOmni_VideoEdit_Example.json`](workflows/GeminiOmni_VideoEdit_Example.json) — Google Gemini Omni Video Edit

---

## Related

- [Gemini Omni API — Python wrapper, MCP server, REST examples](https://github.com/Anil-matcha/Awesome-Gemini-Omni-API-Prompts)
- [muapi.ai — Google Gemini Omni API access](https://muapi.ai)
- [MuAPI CLI — run Gemini Omni from the terminal](https://github.com/SamurAIGPT/muapi-cli)

---

## License

MIT — see [LICENSE](LICENSE)
