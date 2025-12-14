export default function ReportView({ report, onRerun, vendorId }) {
  if (!report) return null;

  const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  const exportReport = async (format) => {
    try {
      const url = `${API_BASE}/api/export/${vendorId || report.vendor_id}/${format}`;
      const res = await fetch(url);
      if (!res.ok) throw new Error("Export failed");
      
      const blob = await res.blob();
      const downloadUrl = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = downloadUrl;
      a.download = `vendorguard_${report.vendor_id}_${new Date().toISOString().split('T')[0]}.${format}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(downloadUrl);
      document.body.removeChild(a);
    } catch (err) {
      alert("Export failed: " + err.message);
    }
  };

  const getStatusColor = (status) => {
    switch(status) {
      case "Covered": return "#4caf50";
      case "Partial": return "#ff9800";
      case "Missing": return "#f44336";
      default: return "#888";
    }
  };

  return (
    <div className="card">
      <div style={{display:"flex", justifyContent:"space-between", alignItems:"center", marginBottom:12}}>
        <div>
          <h3 style={{margin:0}}>{report.vendor_name || report.vendor_id || "Vendor Report"}</h3>
          <div style={{fontSize:12, color:"#888", marginTop:4}}>
            {report.analysis_timestamp && new Date(report.analysis_timestamp).toLocaleString()}
          </div>
        </div>
        <div style={{fontSize:24, fontWeight:700, color: report.overall_risk_score > 70 ? "#f44336" : report.overall_risk_score > 40 ? "#ff9800" : "#4caf50"}}>
          {report.overall_risk_score}
        </div>
      </div>

      <div style={{marginBottom:12, padding:8, background:"#1112", borderRadius:4, fontSize:12}}>
        <strong>Risk Score: {report.overall_risk_score}/100</strong>
        {report.documents_analyzed && report.documents_analyzed.length > 0 && (
          <div style={{marginTop:4}}>
            Documents Analyzed: {report.documents_analyzed.map(d => 
              `${d.filename} (${d.doc_type || "unknown"})`
            ).join(", ")}
          </div>
        )}
      </div>

      <div style={{display:"flex", gap:8, marginBottom:12}}>
        <button onClick={() => exportReport("json")} className="button" style={{flex:1, fontSize:12, padding:6}}>
          Export JSON
        </button>
        <button onClick={() => exportReport("csv")} className="button" style={{flex:1, fontSize:12, padding:6}}>
          Export CSV
        </button>
        <button onClick={onRerun} className="button" style={{flex:1, fontSize:12, padding:6}}>
          Re-analyze
        </button>
      </div>

      <div style={{maxHeight:"60vh", overflowY:"auto"}}>
        {report.controls.map(c => (
          <div key={c.control_id} style={{ marginTop: 12, padding: 12, background: "#1112", borderRadius: 6, borderLeft: `4px solid ${getStatusColor(c.status)}` }}>
            <div style={{display:"flex", justifyContent:"space-between", alignItems:"start", marginBottom:6}}>
              <div>
                <strong>{c.control_name}</strong>
                <span style={{marginLeft:8, fontSize:11, color:"#888"}}>
                  [{(c.frameworks || []).join(", ") || "Custom"}]
                </span>
                <div style={{fontSize:11, color:"#888", marginTop:4}}>
                  Risk: <span style={{color:getStatusColor(c.status), fontWeight:700}}>{c.risk_level}</span>
                </div>
              </div>
              <div style={{display:"flex", gap:8, alignItems:"center"}}>
                <span style={{
                  padding:"2px 8px",
                  borderRadius:4,
                  fontSize:11,
                  fontWeight:600,
                  background: getStatusColor(c.status) + "33",
                  color: getStatusColor(c.status)
                }}>
                  {c.status}
                </span>
                <span style={{fontSize:11, color:"#888"}}>
                  {Number.isFinite(c.confidence) ? c.confidence : 0}%
                </span>
              </div>
            </div>

            {c.key_findings && c.key_findings.length > 0 && (
              <div style={{marginTop:8, fontSize:11}}>
                <strong>Key findings:</strong>
                <ul style={{margin:6, paddingLeft:18}}>
                  {c.key_findings.map((f, i) => (
                    <li key={i} style={{marginTop:2, color:"#ccc"}}>{f}</li>
                  ))}
                </ul>
              </div>
            )}

            {c.missing_requirements && c.missing_requirements.length > 0 && (
              <div style={{marginTop:8, fontSize:11}}>
                <strong>Missing requirements:</strong>
                <ul style={{margin:6, paddingLeft:18}}>
                  {c.missing_requirements.map((r, i) => (
                    <li key={i} style={{marginTop:2, color:"#ccc"}}>{r}</li>
                  ))}
                </ul>
              </div>
            )}

            {c.top_evidence && c.top_evidence.length > 0 && (
              <details style={{marginTop:8, fontSize:11}}>
                <summary style={{cursor:"pointer"}}><strong>Evidence preview</strong></summary>
                {c.top_evidence.map((e, i) => (
                  <div key={i} style={{marginTop:6, padding:8, background:"#0002", borderRadius:4}}>
                    <div style={{color:"#888"}}>{e.doc} — Page {e.page}</div>
                    <div style={{marginTop:4, color:"#aaa", fontSize:10}}>{e.excerpt}</div>
                  </div>
                ))}
              </details>
            )}

            {c.recommended_actions && c.recommended_actions.length > 0 && (
              <div style={{marginTop:8, fontSize:11}}>
                <strong>Recommended actions:</strong>
                <ul style={{margin:6, paddingLeft:18}}>
                  {c.recommended_actions.map((a, i) => (
                    <li key={i} style={{marginTop:2, color:"#ccc"}}>{a}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}