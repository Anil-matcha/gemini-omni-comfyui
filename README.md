# Gemini Omni ComfyUI Nodes

> **ComfyUI custom nodes for Gemini Omni** — the natively multimodal any-to-any video generation model.
> Generate, animate, and edit AI videos directly inside ComfyUI using the [muapi.ai](https://muapi.ai) API.
> If you wish to check the API documentation see [Gemini Omni API](https://github.com/Anil-matcha/Awesome-Gemini-Omni-API-Prompts)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![ComfyUI](https://img.shields.io/badge/ComfyUI-Custom%20Node-blue)](https://github.com/comfyanonymous/ComfyUI)
[![Gemini Omni](https://img.shields.io/badge/Model-Gemini%20Omni-green)](https://muapi.ai)

---

## What is Gemini Omni?

Gemini Omni is a natively multimodal any-to-any video generation model capable of producing high-quality videos from text, images, or existing video clips. It supports:

- **Text-to-Video** — generate video from a text description with optional AI voiceover
- **Image-to-Video** — animate up to 7 reference images
- **Video Edit** — restyle or transform an existing video clip with reference images

---

## Nodes

| Node | Description |
|------|-------------|
| 🔑 Gemini Omni API Key | Set your key once — wire to all nodes |
| 🎬 Gemini Omni Text to Video | Generate video from a text prompt |
| 🎬 Gemini Omni Image to Video | Animate up to 7 reference images |
| 🎬 Gemini Omni Video Edit | Restyle a video clip with optional reference images |
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

Set your muapi.ai API key once and wire the output to all generation nodes. Alternatively, leave every `api_key` field blank — nodes automatically read from `~/.muapi/config.json` if you've authenticated via the CLI.

---

### 🎬 Gemini Omni Text to Video

Generate a video from a text description.

| Field | Values | Default |
|-------|--------|---------|
| `api_key` | Wire from API Key node or leave blank for CLI config | — |
| `prompt` | Text describing the video | — |
| `duration` | 4 / 6 / 8 / 10 seconds | 8 |
| `aspect_ratio` | 16:9 / 9:16 | 16:9 |
| `audio_id` | (none) or one of 30 AI voice names | (none) |
| `seed` | -1 (random) or 0–2147483647 | -1 |

**Outputs:** `video_url` (STRING) · `request_id` (STRING)

---

### 🎬 Gemini Omni Image to Video

Animate up to 7 reference images into a video.

| Field | Values | Default |
|-------|--------|---------|
| `api_key` | Wire from API Key node | — |
| `prompt` | Text describing the animation | — |
| `image_1` | Required — ComfyUI IMAGE tensor | — |
| `image_2` … `image_7` | Optional — additional reference images | — |
| `duration` | 4 / 6 / 8 / 10 seconds | 8 |
| `aspect_ratio` | 16:9 / 9:16 | 16:9 |
| `audio_id` | (none) or one of 30 AI voice names | (none) |
| `seed` | -1 (random) or 0–2147483647 | -1 |

**Outputs:** `video_url` (STRING) · `request_id` (STRING)

---

### 🎬 Gemini Omni Video Edit

Restyle or transform a video clip. Optionally supply up to 5 reference images alongside the video (7 total slots — video uses 2, each image uses 1). At least one of `video_url` or `image_1` must be connected.

| Field | Values | Default |
|-------|--------|---------|
| `api_key` | Wire from API Key node | — |
| `prompt` | Editing instruction | — |
| `duration` | 4 / 6 / 8 / 10 seconds | 8 |
| `aspect_ratio` | 16:9 / 9:16 | 16:9 |
| `trim_start` | 0.0 – 29.0 (seconds) | 0.0 |
| `trim_end` | 0.5 – 30.0 (seconds, max window 10s) | 8.0 |
| `video_url` | Optional — HTTPS URL or local file path | — |
| `image_1` … `image_5` | Optional — reference images (max 5 with video) | — |
| `audio_id` | (none) or one of 30 AI voice names | (none) |
| `seed` | -1 (random) or 0–2147483647 | -1 |

**Outputs:** `video_url` (STRING) · `request_id` (STRING)

---

### 💾 Gemini Omni Video Saver

Download a video URL to disk and decode frames as a ComfyUI IMAGE tensor for downstream processing.

| Field | Values | Default |
|-------|--------|---------|
| `video_url` | Wire from any generation node | — |
| `prefix` | Output filename prefix | `gemini_omni` |
| `save_subfolder` | Subfolder under `ComfyUI/output/` | `gemini_omni` |
| `frame_load_cap` | Max frames to load (0 = all) | 0 |
| `skip_first_frames` | Skip N frames from the start | 0 |
| `select_every_nth` | Load every Nth frame | 1 |

**Outputs:** `frames` (IMAGE) · `filepath` (STRING) · `frame_count` (INT)

---

## Audio Voices

When `audio_id` is set, an AI voice narrates or accompanies the video. Available voices:

`achernar` · `achird` · `algenib` · `algieba` · `alnilam` · `aoede` · `autonoe` · `callirrhoe` · `charon` · `despina` · `enceladus` · `erinome` · `fenrir` · `gacrux` · `iapetus` · `kore` · `laomedeia` · `leda` · `orus` · `puck` · `pulcherrima` · `rasalgethi` · `sadachbia` · `sadaltager` · `schedar` · `sulafat` · `umbriel` · `vindemiatrix` · `zephyr` · `zubenelgenubi`

---

## Example Workflows

Import any of these into ComfyUI via **Load** or drag-and-drop:

- [`GeminiOmni_T2V_Example.json`](workflows/GeminiOmni_T2V_Example.json) — Text to Video
- [`GeminiOmni_I2V_Example.json`](workflows/GeminiOmni_I2V_Example.json) — Image to Video
- [`GeminiOmni_VideoEdit_Example.json`](workflows/GeminiOmni_VideoEdit_Example.json) — Video Edit

---

## License

MIT — see [LICENSE](LICENSE)
