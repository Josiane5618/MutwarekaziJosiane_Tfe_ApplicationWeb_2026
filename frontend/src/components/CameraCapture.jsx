import { useEffect, useRef, useState } from "react";

export default function CameraCapture({ onCapture, hasCapture }) {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);
  const [cameraOn, setCameraOn] = useState(false);
  const [previewUrl, setPreviewUrl] = useState("");
  const [cameraError, setCameraError] = useState("");

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

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      streamRef.current = stream;
      videoRef.current.srcObject = stream;
      setCameraOn(true);
    } catch {
      setCameraError("Impossible d'acceder a la camera sur cet appareil.");
    }
  };

  const captureFace = () => {
    const video = videoRef.current;
    const canvas = canvasRef.current;

    canvas.width = 300;
    canvas.height = 200;

    const context = canvas.getContext("2d");
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    canvas.toBlob(
      (blob) => {
        if (blob) {
          if (previewUrl) {
            URL.revokeObjectURL(previewUrl);
          }

          const nextPreviewUrl = URL.createObjectURL(blob);
          setPreviewUrl(nextPreviewUrl);
          onCapture(blob);
          stopCamera();
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

    onCapture(null);
    startCamera();
  };

  return (
    <section className="camera-card">
      <div className="camera-header">
        <div>
          <p className="section-label">Verification faciale</p>
          <h3>Capture webcam</h3>
        </div>
        {hasCapture ? <span className="capture-badge">Capture prete</span> : null}
      </div>

      <p className="camera-copy">
        Placez votre visage devant la camera puis capturez une image nette.
      </p>

      {cameraError ? <div className="feedback feedback-error">{cameraError}</div> : null}

      <div className="camera-preview">
        {previewUrl ? (
          <img src={previewUrl} alt="Capture faciale" className="preview-image" />
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
            La camera n'est pas encore activee.
          </div>
        ) : null}
        <canvas ref={canvasRef} style={{ display: "none" }} />
      </div>

      <div className="camera-actions">
        {!cameraOn && !previewUrl ? (
          <button className="secondary-button" type="button" onClick={startCamera}>
            Activer la camera
          </button>
        ) : null}

        {cameraOn ? (
          <>
            <button className="secondary-button" type="button" onClick={stopCamera}>
              Fermer la camera
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
