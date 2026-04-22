import { useRef } from "react";

export default function CameraCapture({ onCapture }) {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);

  const startCamera = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ video: true });
    videoRef.current.srcObject = stream;
  };

  const captureFace = () => {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    canvas.width = 300;
    canvas.height = 200;

    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0, 300, 200);

    canvas.toBlob(blob => {
      onCapture(blob);
    }, "image/jpeg");
  };

  return (
    <div>
      <video ref={videoRef} autoPlay />
      <canvas ref={canvasRef} hidden />

      <button onClick={startCamera}>
        Activer la caméra
      </button>

      <button onClick={captureFace}>
        Capturer le visage
      </button>
    </div>
  );
}