// frontend/pages/index.js
import { useState, useEffect } from "react";
import UploadForm from "../components/UploadForm";
import ReportView from "../components/ReportView";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function Home(){
  const [uploaded, setUploaded] = useState(null);
  const [report, setReport] = useState(null);
  const [running, setRunning] = useState(false);
  const [frameworkFilter, setFrameworkFilter] = useState("");
  const [frameworks, setFrameworks] = useState([]);
  const [history, setHistory] = useState([]);

  // Load frameworks on mount
  useEffect(() => {
    fetch(`${API_BASE}/api/controls/frameworks`)
      .then(res => res.json())
      .then(data => setFrameworks(data))
      .catch(err => console.error("Failed to load frameworks:", err));
  }, []);

  // Load history when vendor changes
  useEffect(() => {
    if (uploaded?.vendor_id) {
      fetch(`${API_BASE}/api/history/${uploaded.vendor_id}?limit=5`)
        .then(res => res.json())
        .then(data => setHistory(data))
        .catch(err => console.error("Failed to load history:", err));
    }
  }, [uploaded?.vendor_id]);

  // called after a successful upload
  async function handleUploaded(data){
    // data must include: vendor_id, filename, path
    console.log("Upload response:", data);
    setUploaded(data);
    // Optionally auto-run analyze:
    // await runAnalyze(data.vendor_id, [data.path]);
  }

  async function runAnalyze(vendorId, filePaths) {
    setRunning(true);
    try {
      // if no explicit filePaths passed in, use uploaded.path
      if (!filePaths || filePaths.length === 0) {
        if (!uploaded || !uploaded.path) throw new Error("No uploaded file path available. Upload a PDF first.");
        filePaths = [uploaded.path];
      }

      // Build request body exactly how backend expects it
      const body = { 
        vendor_name: vendorId, 
        file_paths: filePaths,
        framework_filter: frameworkFilter || null
      };
      console.log("Analyze body:", body);

      const res = await fetch(`${API_BASE}/api/analyze/${vendorId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body)
      });

      const text = await res.text();
      let data = null;
      try { data = text ? JSON.parse(text) : null; } catch(e) {
        throw new Error("Analyze: failed to parse server response: " + text);
      }

      if (!res.ok) {
        throw new Error(data?.detail || JSON.stringify(data) || "Analyze failed");
      }

      console.log("Analyze response:", data);
      setReport(data);
    } catch (err) {
      console.error("Analyze failed:", err);
      alert("Analyze failed: " + err.message);
    } finally {
      setRunning(false);
    }
  }

  return (
    <div className="container">
      <div className="header">
        <div className="logo">VG</div>
        <div className="title">VendorGuard — Demo UI</div>
      </div>

      <div className="grid">
        <div>
          <UploadForm onUploaded={handleUploaded} />
          
          {uploaded && (
            <div className="card" style={{marginTop:16}}>
              <div style={{fontWeight:700, marginBottom:8}}>Uploaded Document</div>
              <div className="file-list">
                <div className="file-item">
                  <div>
                    <div className="file-name">{uploaded.filename}</div>
                    <div className="small">Type: {uploaded.document_type || "Unknown"}</div>
                    <div className="small">Path: {uploaded.path}</div>
                  </div>
                </div>
              </div>
              
              <div style={{marginTop:12}}>
                <label style={{display:"block", marginBottom:4, fontSize:12, fontWeight:600}}>
                  Filter by Framework (optional):
                </label>
                <select
                  value={frameworkFilter}
                  onChange={e => setFrameworkFilter(e.target.value)}
                  style={{padding:6, borderRadius:4, width:"100%", fontSize:12}}
                >
                  <option value="">All Frameworks</option>
                  {frameworks.map(f => (
                    <option key={f} value={f}>{f}</option>
                  ))}
                </select>
              </div>
              
              <button 
                className="button" 
                onClick={() => runAnalyze(uploaded.vendor_id, [uploaded.path])} 
                disabled={running}
                style={{marginTop:12, width:"100%"}}
              >
                {running ? "Analyzing..." : "Analyze Documents"}
              </button>
            </div>
          )}

          {history.length > 0 && (
            <div className="card" style={{marginTop:16}}>
              <div style={{fontWeight:700, marginBottom:8}}>Analysis History</div>
              <div style={{fontSize:12}}>
                {history.slice(0, 5).map((h, i) => (
                  <div key={i} style={{padding:6, marginBottom:4, background:"#1112", borderRadius:4}}>
                    <div>{new Date(h.analysis_timestamp).toLocaleString()}</div>
                    <div style={{color:"#888"}}>Risk: {h.risk_score} | Docs: {h.document_count} | Controls: {h.control_count}</div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        <div>
          <div className="card">
            <div style={{fontWeight:700}}>VendorGuard</div>
            <div style={{marginTop:8, fontSize:12}}>
              AI-powered vendor risk analysis using RAG. Upload contracts, SLAs, SOC2, ISO reports and analyze compliance.
            </div>
          </div>

          <div style={{marginTop:16}}>
            <ReportView 
              report={report} 
              onRerun={() => uploaded && runAnalyze(uploaded.vendor_id, [uploaded.path])}
              vendorId={uploaded?.vendor_id}
            />
          </div>
        </div>
      </div>
    </div>
  );
}