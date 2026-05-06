import asyncio

import pytest
from fastapi import HTTPException

from app.routers import face_detection as face_detection_router


class FakeUploadFile:
    def __init__(self, content: bytes):
        self.content = content

    async def read(self):
        return self.content


def test_detect_face_returns_face_box(monkeypatch):
    monkeypatch.setattr(
        face_detection_router,
        "detect_face_box",
        lambda image_bytes: {
            "x": 25.0,
            "y": 20.0,
            "width": 40.0,
            "height": 45.0,
            "image_width": 400,
            "image_height": 300,
        }
    )

    response = asyncio.run(
        face_detection_router.detect_face(FakeUploadFile(b"fake-image"))
    )

    assert response["face_detected"] is True
    assert response["box"]["x"] == 25.0
    assert response["box"]["image_width"] == 400


def test_detect_face_rejects_image_without_face(monkeypatch):
    monkeypatch.setattr(
        face_detection_router,
        "detect_face_box",
        lambda image_bytes: None
    )

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(
            face_detection_router.detect_face(FakeUploadFile(b"fake-image"))
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Aucun visage détecté"
