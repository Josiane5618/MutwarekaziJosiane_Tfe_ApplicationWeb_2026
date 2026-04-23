import { useRef, useState } from "react";

export default function CameraCapture({ onCapture }) {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [cameraOn, setCameraOn] = useState(false);

  // Activer la caméra
  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      videoRef.current.srcObject = stream;
      setCameraOn(true);
    } catch (err) {
      alert("Impossible d'accéder à la caméra");
    }
  };

  // Capturer le visage
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
          onCapture(blob); // envoie l'image au formulaire parent
          alert("Visage capturé avec succès");
        }
      },
      "image/jpeg",
      0.95
    );
  };

  return (
    <div style={{ marginTop: "20px" }}>
      <h4>Capture faciale</h4>

      {!cameraOn && (
        <button type="button" onClick={startCamera}>
          Activer la caméra
        </button>
      )}

      <div style={{ marginTop: "10px" }}>
        <video
          ref={videoRef}
          autoPlay
          playsInline
          width="300"
          height="200"
          style={{ border: "1px solid black" }}
        />
        <canvas ref={canvasRef} style={{ display: "none" }} />
      </div>

      {cameraOn && (
        <button
          type="button"
          onClick={captureFace}
          style={{ marginTop: "10px" }}
        >
          Capturer le visage
        </button>
      )}
    </div>
  );
}