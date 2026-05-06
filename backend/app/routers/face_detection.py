from fastapi import APIRouter, File, HTTPException, UploadFile

from app.face_recognition.engine import detect_face_box

router = APIRouter(
    prefix="/face",
    tags=["Reconnaissance faciale"]
)


@router.post("/detect")
async def detect_face(file: UploadFile = File(...)):
    image_bytes = await file.read()
    box = detect_face_box(image_bytes)

    if box is None:
        raise HTTPException(
            status_code=400,
            detail="Aucun visage détecté"
        )

    return {
        "face_detected": True,
        "box": box,
    }
