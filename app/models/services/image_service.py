"""Image service for food item pictures (CLAUDE.md, Admin panel 2; FR-A2.1–2.4).

Staff can upload a picture, or write an instruction that an image service uses
to create or modify the picture. Either way the result is kept as a *pending*
image until staff confirm it in the preview (FR-A2.3).

Providers are pluggable (implementation plan, "Images"). The stub provider works
without an API key; a real provider reads its key from .env (FR-A2.4, NFR-5).
"""
from __future__ import annotations

import hashlib
import io
import os
import shutil
import textwrap
import uuid
from typing import Protocol

from PIL import Image, ImageDraw, ImageFont

ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
MAX_UPLOAD_BYTES = 5 * 1024 * 1024
PENDING_DIR = "pending"
ITEMS_DIR = "items"


class ImageProvider(Protocol):
    def generate(self, instruction: str, base_image: bytes | None = None) -> bytes:
        """Return PNG bytes made from the instruction (optionally modifying base_image)."""


class StubImageProvider:
    """Draws a simple placeholder picture with the instruction text. No network, no key."""

    size = (800, 600)

    def generate(self, instruction: str, base_image: bytes | None = None) -> bytes:
        digest = hashlib.sha1(instruction.encode("utf-8")).digest()
        colour = (90 + digest[0] % 120, 90 + digest[1] % 120, 70 + digest[2] % 100)
        if base_image:
            img = Image.open(io.BytesIO(base_image)).convert("RGB").resize(self.size)
            overlay = Image.new("RGB", self.size, colour)
            img = Image.blend(img, overlay, 0.35)
        else:
            img = Image.new("RGB", self.size, colour)
        draw = ImageDraw.Draw(img)
        font = ImageFont.load_default(size=36) if hasattr(ImageFont, "load_default") else None
        text = "\n".join(textwrap.wrap(instruction, width=32)[:6])
        draw.multiline_text((40, 40), text, fill=(255, 255, 255), font=font, spacing=10)
        draw.text((40, self.size[1] - 60), "placeholder image (stub)", fill=(240, 240, 240), font=font)
        out = io.BytesIO()
        img.save(out, format="PNG")
        return out.getvalue()


def get_provider(name: str, api_key: str | None = None) -> ImageProvider:
    if name in ("", None, "stub"):
        return StubImageProvider()
    # A real provider (e.g. an image generation API) is added here later and
    # reads api_key from .env. Never hard-code keys (CLAUDE.md, Security basics).
    raise ValueError(f"Unknown image provider '{name}'. Set IMAGE_PROVIDER=stub in .env.")


class ImageService:
    """Keeps pending images on disk and moves them into place when confirmed."""

    def __init__(self, upload_folder: str, provider: ImageProvider):
        self.upload_folder = upload_folder
        self.provider = provider
        os.makedirs(os.path.join(upload_folder, PENDING_DIR), exist_ok=True)
        os.makedirs(os.path.join(upload_folder, ITEMS_DIR), exist_ok=True)

    # ---- creating pending images ------------------------------------------
    def _store_pending(self, data: bytes, ext: str) -> str:
        token = f"{uuid.uuid4().hex}{ext}"
        with open(os.path.join(self.upload_folder, PENDING_DIR, token), "wb") as fh:
            fh.write(data)
        return token

    def pending_from_upload(self, filename: str, data: bytes) -> str:
        ext = os.path.splitext(filename or "")[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise ValueError("Please upload a PNG, JPG or WEBP picture.")
        if not data:
            raise ValueError("The file is empty.")
        if len(data) > MAX_UPLOAD_BYTES:
            raise ValueError("The picture is larger than 5 MB.")
        try:
            Image.open(io.BytesIO(data)).verify()
        except Exception:
            raise ValueError("The file is not a valid picture.")
        return self._store_pending(data, ext)

    def pending_from_instruction(self, instruction: str, current_image: str | None = None) -> str:
        instruction = (instruction or "").strip()
        if not instruction:
            raise ValueError("Please write an instruction for the picture.")
        base = None
        if current_image:
            path = os.path.join(self.upload_folder, current_image)
            if os.path.exists(path):
                with open(path, "rb") as fh:
                    base = fh.read()
        return self._store_pending(self.provider.generate(instruction, base), ".png")

    # ---- preview / confirm / discard --------------------------------------
    def _pending_path(self, token: str) -> str:
        if os.path.basename(token) != token or not token:
            raise ValueError("Invalid image reference.")
        return os.path.join(self.upload_folder, PENDING_DIR, token)

    def pending_exists(self, token: str) -> bool:
        try:
            return os.path.exists(self._pending_path(token))
        except ValueError:
            return False

    def pending_relpath(self, token: str) -> str:
        return f"{PENDING_DIR}/{token}"

    def confirm(self, token: str, item_id: str) -> str:
        """Move a pending image into place for the item; returns the new relative path."""
        src = self._pending_path(token)
        if not os.path.exists(src):
            raise ValueError("The preview has expired. Please create the picture again.")
        ext = os.path.splitext(token)[1]
        rel = f"{ITEMS_DIR}/{item_id}-{uuid.uuid4().hex[:8]}{ext}"
        shutil.move(src, os.path.join(self.upload_folder, rel))
        return rel

    def discard(self, token: str) -> None:
        try:
            path = self._pending_path(token)
        except ValueError:
            return
        if os.path.exists(path):
            os.remove(path)

    def delete(self, rel_path: str | None) -> None:
        if not rel_path:
            return
        path = os.path.join(self.upload_folder, rel_path)
        if os.path.abspath(path).startswith(os.path.abspath(self.upload_folder)) and os.path.exists(path):
            os.remove(path)
