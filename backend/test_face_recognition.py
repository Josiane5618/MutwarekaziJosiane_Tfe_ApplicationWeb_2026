from backend.app.face_recognition.engine import extract_face_encoding

IMAGE_PATH = "backend/test_image.jpg"

with open(IMAGE_PATH, "rb") as f:
    image_bytes = f.read()

encoding = extract_face_encoding(image_bytes)

if encoding is None:
    print("Aucun visage detecte")
else:
    print("Encodage detecte")
    print("Type :", type(encoding))
    print("Shape :", encoding.shape)
    print("5 premières valeurs :", encoding[:5])