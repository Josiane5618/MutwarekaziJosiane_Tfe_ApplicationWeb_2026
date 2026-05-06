import { useEffect, useRef, useState } from "react";
import { detectFaceBox } from "../api/api";

export default function CameraCapture({ onCapture, hasCapture }) {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);
  const [cameraOn, setCameraOn] = useState(false);
  const [previewUrl, setPreviewUrl] = useState("");
  const [faceBox, setFaceBox] = useState(null);
  const [cameraError, setCameraError] = useState("");
  const [faceDetectionMessage, setFaceDetectionMessage] = useState("");

  useEffect(() => {
    return () => {
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
      }

      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
    };
  }, [previewUrl]);

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }

    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }

    setCameraOn(false);
  };

  const startCamera = async () => {
    setCameraError("");
    setFaceBox(null);
    setFaceDetectionMessage("");

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      streamRef.current = stream;
      videoRef.current.srcObject = stream;
      setCameraOn(true);
    } catch {
      setCameraError("Impossible d'accéder à la caméra sur cet appareil.");
    }
  };

  const captureFace = () => {
    const video = videoRef.current;
    const canvas = canvasRef.current;

    canvas.width = 400;
    canvas.height = 300;

    const context = canvas.getContext("2d");
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    canvas.toBlob(
      async (blob) => {
        if (blob) {
          if (previewUrl) {
            URL.revokeObjectURL(previewUrl);
          }

          const nextPreviewUrl = URL.createObjectURL(blob);
          setPreviewUrl(nextPreviewUrl);
          onCapture(blob);
          stopCamera();

          try {
            const response = await detectFaceBox(blob);
            const payload = await response.json().catch(() => null);

            if (!response.ok) {
              setFaceBox(null);
              setFaceDetectionMessage(
                payload?.detail || "Aucun visage détecté sur la capture."
              );
              return;
            }

            setFaceBox(payload.box);
            setFaceDetectionMessage("Visage détecté sur la capture.");
          } catch {
            setFaceBox(null);
            setFaceDetectionMessage("Détection du visage indisponible.");
          }
        }
      },
      "image/jpeg",
      0.95
    );
  };

  const retakeCapture = () => {
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
      setPreviewUrl("");
    }

    setFaceBox(null);
    setFaceDetectionMessage("");
    onCapture(null);
    startCamera();
  };

  return (
    <section className="camera-card">
      <div className="camera-header">
        <div>
          <p className="section-label">Vérification faciale</p>
          <h3>Capture webcam</h3>
        </div>
        {hasCapture ? <span className="capture-badge">Capture prête</span> : null}
      </div>

      <p className="camera-copy">
        Placez votre visage devant la caméra puis capturez une image nette.
      </p>

      {cameraError ? <div className="feedback feedback-error">{cameraError}</div> : null}
      {faceDetectionMessage ? (
        <div
          className={
            faceBox
              ? "feedback feedback-success"
              : "feedback feedback-error"
          }
        >
          {faceDetectionMessage}
        </div>
      ) : null}

      <div className="camera-preview">
        {previewUrl ? (
          <>
            <img src={previewUrl} alt="Capture faciale" className="preview-image" />
            {faceBox ? (
              <div
                className="face-detection-box"
                aria-label="Visage détecté"
                style={{
                  left: `${faceBox.x}%`,
                  top: `${faceBox.y}%`,
                  width: `${faceBox.width}%`,
                  height: `${faceBox.height}%`
                }}
              />
            ) : null}
          </>
        ) : (
          <video
            ref={videoRef}
            autoPlay
            playsInline
            className={`camera-video ${cameraOn ? "is-active" : ""}`}
          />
        )}

        {!cameraOn && !previewUrl ? (
          <div className="camera-placeholder">
            La caméra n'est pas encore activée.
          </div>
        ) : null}
        <canvas ref={canvasRef} style={{ display: "none" }} />
      </div>

      <div className="camera-actions">
        {!cameraOn && !previewUrl ? (
          <button className="secondary-button" type="button" onClick={startCamera}>
            Activer la caméra
          </button>
        ) : null}

        {cameraOn ? (
          <>
            <button className="secondary-button" type="button" onClick={stopCamera}>
              Fermer la caméra
            </button>
            <button className="secondary-button" type="button" onClick={captureFace}>
              Capturer le visage
            </button>
          </>
        ) : null}

        {previewUrl ? (
          <button className="secondary-button" type="button" onClick={retakeCapture}>
            Reprendre la photo
          </button>
        ) : null}
      </div>
    </section>
  );
}
