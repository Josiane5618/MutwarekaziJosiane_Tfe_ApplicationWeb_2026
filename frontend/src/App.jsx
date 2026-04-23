import CameraCapture from "./components/CameraCapture";

function App() {
  const handleCapture = (imageBlob) => {
    console.log("IMAGE CAPTURÉE :", imageBlob);
  };

  return (
    <div style={{ padding: "20px" }}>
      <h2>Test CameraCapture</h2>
      <CameraCapture onCapture={handleCapture} />
    </div>
  );
}

export default App;