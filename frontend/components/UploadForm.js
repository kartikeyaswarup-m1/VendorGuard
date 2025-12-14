// frontend/components/UploadForm.js
import { useState } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function UploadForm({ onUploaded }) {
  const [vendorId, setVendorId] = useState("");
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);

  async function handleUpload(){
    if (!vendorId) return alert("Enter vendor id (eg: vendor-001)");
    if (!file) return alert("Select a PDF file");
    setLoading(true);

    try {
      const form = new FormData();
      form.append("file", file);

      const res = await fetch(`${API_BASE}/api/upload/${vendorId}`, {
        method: "POST",
        body: form
      });

      // Parse response robustly
      const text = await res.text();
      let data = null;
      try { data = text ? JSON.parse(text) : null; } catch(e) {
        throw new Error("Upload: failed to parse server response: " + text);
      }

      if (!res.ok) {
        throw new Error(data?.detail || JSON.stringify(data) || "Upload failed");
      }

      // IMPORTANT: call parent with the returned object (must contain vendor_id, filename, path)
      onUploaded(data);
    } catch (err) {
      console.error("Upload error:", err);
      alert("Upload error: " + err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="card">
      <div style={{marginBottom:8}}>
        <input
          placeholder="Vendor ID (eg: vendor-001)"
          value={vendorId}
          onChange={e => setVendorId(e.target.value)}
          style={{padding:8,borderRadius:6,width:"100%",marginBottom:8}}
        />
        <input type="file" accept="application/pdf" onChange={e => setFile(e.target.files?.[0] || null)} />
      </div>

      <div style={{display:"flex",gap:8}}>
        <button className="button" onClick={handleUpload} disabled={loading}>
          {loading ? "Uploading..." : "Upload"}
        </button>
        <button className="button" style={{background:"#44566f"}} onClick={() => { setFile(null); setVendorId(""); }}>
          Reset
        </button>
      </div>
    </div>
  );
}