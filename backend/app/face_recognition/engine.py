import cv2
import dlib
import numpy as np
import os

FACE_RECO_DIR = os.path.dirname(__file__)
APP_DIR = os.path.dirname(FACE_RECO_DIR)
BACKEND_DIR = os.path.dirname(APP_DIR)
PROJECT_DIR = os.path.dirname(BACKEND_DIR)
ASSETS_DIR = os.path.join(PROJECT_DIR, "assets")

PREDICTOR_PATH = os.path.join(
    ASSETS_DIR, "shape_predictor_68_face_landmarks.dat"
)
REC_MODEL_PATH = os.path.join(
    ASSETS_DIR, "dlib_face_recognition_resnet_model_v1.dat"
)

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(PREDICTOR_PATH)
face_rec_model = dlib.face_recognition_model_v1(REC_MODEL_PATH)


def extract_face_encoding(image_bytes: bytes):
    """
    Extrait l'encodage facial (numpy array de taille 128)
    à partir d'une image envoyée sous forme de bytes.
    """
    image_array = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

    if image is None:
        return None

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = detector(gray, 1)

    if not faces:
        return None

    face = faces[0]
    shape = predictor(gray, face)

    encoding = np.array(
        face_rec_model.compute_face_descriptor(image, shape),
        dtype=np.float32
    )

    return encoding
