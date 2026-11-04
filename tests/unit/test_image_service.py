"""Image service: pending → confirm/discard (FR-A2.1–2.3)."""
import io
import os

import pytest
from PIL import Image

from app.models.services.image_service import ImageService, StubImageProvider


@pytest.fixture
def service(tmp_path):
    return ImageService(str(tmp_path), StubImageProvider())


def png_bytes():
    out = io.BytesIO()
    Image.new("RGB", (10, 10), (200, 0, 0)).save(out, format="PNG")
    return out.getvalue()


def test_instruction_creates_pending_png(service, tmp_path):
    token = service.pending_from_instruction("Fish soup in a white bowl")
    assert service.pending_exists(token)
    with Image.open(tmp_path / "pending" / token) as img:
        assert img.format == "PNG"
    assert os.listdir(tmp_path / "items") == []  # nothing saved before confirm


def test_confirm_moves_image_into_place(service, tmp_path):
    token = service.pending_from_upload("soup.png", png_bytes())
    rel = service.confirm(token, "item1")
    assert (tmp_path / rel).exists()
    assert not service.pending_exists(token)


def test_modify_uses_current_picture(service):
    rel = service.confirm(service.pending_from_upload("a.png", png_bytes()), "item1")
    token = service.pending_from_instruction("make it brighter", current_image=rel)
    assert service.pending_exists(token)


def test_discard_removes_pending(service):
    token = service.pending_from_instruction("Lamb")
    service.discard(token)
    assert not service.pending_exists(token)


@pytest.mark.parametrize("name, data", [("x.gif", b"GIF89a"), ("x.png", b""), ("x.png", b"not an image")])
def test_bad_uploads_are_rejected(service, name, data):
    with pytest.raises(ValueError):
        service.pending_from_upload(name, data)


def test_path_traversal_is_refused(service):
    assert not service.pending_exists("../secret.png")
    with pytest.raises(ValueError):
        service.confirm("../secret.png", "item1")
