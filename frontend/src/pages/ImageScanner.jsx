import { useState } from "react";
export default function ImageScanner() {
  const [image, setImage] = useState(null);
  const [result, setResult] = useState("");

  const handleUpload = async () => {
    const formData = new FormData();
    formData.append("image", image);

    const res = await fetch("http://localhost:5000/api/image-scan", {
      method: "POST",
      body: formData,
    });

    const data = await res.json();
    setResult(data.text);
  };

  return (
    <div className="page">
      <h1>Image Scanner</h1>
      <p className="page-sub">
        Extract text and insights from images using OCR and AI.
      </p>

      <div className="tool-card">
        <div className="tool-header">
          <span>🖼️ Image Processing</span>
          <span className="live-badge">● Live</span>
        </div>

        <div className="tool-body split">
          {/* LEFT */}
          <div className="tool-section">
            <div className="section-label">UPLOAD</div>
            <input type="file" onChange={(e) => setImage(e.target.files[0])} />
          </div>

          {/* RIGHT */}
          <div className="tool-section">
            <div className="section-label">EXTRACTED TEXT</div>
            <div className="output-box">
              {result || "Scanned text will appear here..."}
            </div>
          </div>
        </div>

        <button onClick={handleUpload} className="primary-btn">
          Scan Image
        </button>
      </div>
    </div>
  );
}