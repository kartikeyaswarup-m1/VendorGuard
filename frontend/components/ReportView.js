export default function ReportView({ report, onRerun, vendorId }) {
  if (!report) return null;

  const exportReport = async (format) => {
    try {
      const url = `http://localhost:8000/api/export/${vendorId || report.vendor_id}/${format}`;
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

  const getClassificationColor = (classification) => {
    switch(classification) {
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
          <div key={c.control_id} style={{ marginTop: 12, padding: 12, background: "#1112", borderRadius: 6, borderLeft: `4px solid ${getClassificationColor(c.classification)}` }}>
            <div style={{display:"flex", justifyContent:"space-between", alignItems:"start", marginBottom:6}}>
              <div>
                <strong>{c.name}</strong>
                <span style={{marginLeft:8, fontSize:11, color:"#888"}}>
                  [{c.framework || "Custom"}]
                </span>
              </div>
              <div style={{display:"flex", gap:8, alignItems:"center"}}>
                <span style={{
                  padding:"2px 8px",
                  borderRadius:4,
                  fontSize:11,
                  fontWeight:600,
                  background: getClassificationColor(c.classification) + "33",
                  color: getClassificationColor(c.classification)
                }}>
                  {c.classification}
                </span>
                <span style={{fontSize:11, color:"#888"}}>
                  {(c.confidence * 100).toFixed(0)}%
                </span>
              </div>
            </div>
            
            <div style={{ fontSize: 12, marginTop: 6, color: "#ccc" }}>
              {c.rationale}
            </div>

            {c.evidence && c.evidence.length > 0 && (
              <div style={{marginTop:8, fontSize:11}}>
                <strong>Evidence:</strong>
                {c.evidence.slice(0, 3).map((e, i) => (
                  <div key={i} style={{marginTop:4, padding:6, background:"#0002", borderRadius:4}}>
                    <div style={{color:"#888"}}>
                      {e.doc_id} {e.doc_type && `(${e.doc_type})`} - Page {e.page}
                      {e.similarity_score && ` [Similarity: ${(e.similarity_score * 100).toFixed(1)}%]`}
                    </div>
                    <div style={{marginTop:2, color:"#aaa", fontSize:10}}>
                      {e.snippet.substring(0, 150)}...
                    </div>
                  </div>
                ))}
              </div>
            )}

            {c.followup_questions && c.followup_questions.length > 0 && (
              <div style={{marginTop:8, fontSize:11}}>
                <strong>Follow-up Questions:</strong>
                <ul style={{margin:4, paddingLeft:20}}>
                  {c.followup_questions.map((q, i) => (
                    <li key={i} style={{marginTop:2}}>{q}</li>
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