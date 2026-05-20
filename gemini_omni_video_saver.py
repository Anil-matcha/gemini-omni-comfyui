"""
Gemini Omni Video Saver
=======================
Downloads a video URL returned by Gemini Omni nodes, saves it to
ComfyUI/output/<save_subfolder>/, and optionally returns frames as an
IMAGE tensor for downstream processing.
"""

import os
import time
import requests
import numpy as np
import torch

try:
    import cv2
    _CV2 = True
except ImportError:
    _CV2 = False

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "output")


class GeminiOmniVideoSaver:
    """Download and save a Gemini Omni video URL to disk."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "video_url": ("STRING", {"forceInput": True}),
                "prefix": ("STRING", {"default": "gemini_omni"}),
                "save_subfolder": ("STRING", {"default": "gemini_omni"}),
            },
            "optional": {
                "frame_load_cap": ("INT", {"default": 0, "min": 0, "max": 9999,
                                           "tooltip": "Max frames to load (0 = all)"}),
                "skip_first_frames": ("INT", {"default": 0, "min": 0, "max": 9999}),
                "select_every_nth": ("INT", {"default": 1, "min": 1, "max": 100}),
            },
        }

    RETURN_TYPES = ("IMAGE", "STRING", "INT")
    RETURN_NAMES = ("frames", "filepath", "frame_count")
    FUNCTION = "save"
    OUTPUT_NODE = True
    CATEGORY = "MuAPI/Gemini Omni"

    def save(
        self,
        video_url,
        prefix="gemini_omni",
        save_subfolder="gemini_omni",
        frame_load_cap=0,
        skip_first_frames=0,
        select_every_nth=1,
    ):
        out_dir = os.path.join(OUTPUT_DIR, save_subfolder)
        os.makedirs(out_dir, exist_ok=True)

        # Auto-increment filename
        idx = 1
        while True:
            filepath = os.path.join(out_dir, f"{prefix}_{idx:05d}.mp4")
            if not os.path.exists(filepath):
                break
            idx += 1

        # Download
        resp = requests.get(video_url, stream=True, timeout=300)
        resp.raise_for_status()
        with open(filepath, "wb") as f:
            for chunk in resp.iter_content(chunk_size=1 << 16):
                f.write(chunk)

        # Load frames
        frames_tensor, frame_count = self._load_frames(
            filepath, frame_load_cap, skip_first_frames, select_every_nth
        )

        results = [{
            "filename": os.path.basename(filepath),
            "subfolder": save_subfolder,
            "type": "output",
        }]
        return {"ui": {"gifs": results}, "result": (frames_tensor, filepath, frame_count)}

    @staticmethod
    def _load_frames(filepath, cap, skip, nth):
        if not _CV2:
            dummy = torch.zeros(1, 64, 64, 3)
            return dummy, 0

        vc = cv2.VideoCapture(filepath)
        frames = []
        total = 0
        while True:
            ok, frame = vc.read()
            if not ok:
                break
            total += 1
            if total <= skip:
                continue
            if (total - skip - 1) % nth != 0:
                continue
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frames.append(frame)
            if cap and len(frames) >= cap:
                break
        vc.release()

        if not frames:
            return torch.zeros(1, 64, 64, 3), 0

        arr = np.stack(frames).astype(np.float32) / 255.0
        return torch.from_numpy(arr), len(frames)


NODE_CLASS_MAPPINGS = {"GeminiOmniVideoSaver": GeminiOmniVideoSaver}
NODE_DISPLAY_NAME_MAPPINGS = {"GeminiOmniVideoSaver": "Gemini Omni Video Saver"}
