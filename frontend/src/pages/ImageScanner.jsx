import { useState } from "react";
import { scanImage } from "../services/api";

export default function ImageScanner() {
  const [image, setImage] = useState(null);
  const [result, setResult] = useState("");

  const handleUpload = async () => {
    const data = await scanImage(image);
    setResult(data.text);
  };

  return (
    <div className="page">
      <h1>Image Scanner</h1>
      <p className="page-sub">Extract text and insights from images using OCR and AI.</p>

      <div className="tool-card">
        <div className="tool-header">
          <span>🖼️ Image Processing</span>
          <span className="live-badge">● Live</span>
        </div>

        <div className="tool-body split">
          <div className="tool-section">
            <div className="section-label">UPLOAD</div>
            <input type="file" onChange={(event) => setImage(event.target.files[0])} />
          </div>

          <div className="tool-section">
            <div className="section-label">EXTRACTED TEXT</div>
            <div className="output-box">{result || "Scanned text will appear here..."}</div>
          </div>
        </div>

        <button onClick={handleUpload} className="primary-btn">
          Scan Image
        </button>
      </div>
    </div>
  );
}
