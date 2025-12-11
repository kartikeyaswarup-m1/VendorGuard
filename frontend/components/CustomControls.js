// frontend/components/CustomControls.js
import { useState, useEffect } from "react";

export default function CustomControls({ vendorId }) {
  const [controls, setControls] = useState([]);
  const [showAdd, setShowAdd] = useState(false);
  const [newControl, setNewControl] = useState({
    control_id: "",
    name: "",
    description: "",
    framework: "Custom",
    category: "Custom",
    weight: 1.0
  });

  useEffect(() => {
    loadControls();
  }, []);

  const loadControls = async () => {
    try {
      const res = await fetch("http://localhost:8000/api/controls");
      const data = await res.json();
      setControls(data);
    } catch (err) {
      console.error("Failed to load controls:", err);
    }
  };

  const addControl = async () => {
    try {
      const res = await fetch("http://localhost:8000/api/controls/custom", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(newControl)
      });
      if (!res.ok) throw new Error("Failed to add control");
      await loadControls();
      setShowAdd(false);
      setNewControl({
        control_id: "",
        name: "",
        description: "",
        framework: "Custom",
        category: "Custom",
        weight: 1.0
      });
    } catch (err) {
      alert("Failed to add control: " + err.message);
    }
  };

  const deleteControl = async (controlId) => {
    if (!confirm("Delete this custom control?")) return;
    try {
      const res = await fetch(`http://localhost:8000/api/controls/custom/${controlId}`, {
        method: "DELETE"
      });
      if (!res.ok) throw new Error("Failed to delete control");
      await loadControls();
    } catch (err) {
      alert("Failed to delete control: " + err.message);
    }
  };

  return (
    <div className="card" style={{marginTop:16}}>
      <div style={{display:"flex", justifyContent:"space-between", alignItems:"center", marginBottom:12}}>
        <strong>Custom Controls</strong>
        <button className="button" onClick={() => setShowAdd(!showAdd)} style={{fontSize:12, padding:6}}>
          {showAdd ? "Cancel" : "+ Add Control"}
        </button>
      </div>

      {showAdd && (
        <div style={{padding:12, background:"#1112", borderRadius:4, marginBottom:12}}>
          <input
            placeholder="Control ID (e.g., C-CUSTOM-01)"
            value={newControl.control_id}
            onChange={e => setNewControl({...newControl, control_id: e.target.value})}
            style={{width:"100%", padding:6, marginBottom:6, borderRadius:4, fontSize:12}}
          />
          <input
            placeholder="Control Name"
            value={newControl.name}
            onChange={e => setNewControl({...newControl, name: e.target.value})}
            style={{width:"100%", padding:6, marginBottom:6, borderRadius:4, fontSize:12}}
          />
          <textarea
            placeholder="Control Description"
            value={newControl.description}
            onChange={e => setNewControl({...newControl, description: e.target.value})}
            style={{width:"100%", padding:6, marginBottom:6, borderRadius:4, fontSize:12, minHeight:60}}
          />
          <div style={{display:"flex", gap:8}}>
            <input
              type="number"
              placeholder="Weight (0-1)"
              value={newControl.weight}
              onChange={e => setNewControl({...newControl, weight: parseFloat(e.target.value)})}
              style={{flex:1, padding:6, borderRadius:4, fontSize:12}}
              min="0"
              max="1"
              step="0.1"
            />
            <button className="button" onClick={addControl} style={{padding:6, fontSize:12}}>
              Add
            </button>
          </div>
        </div>
      )}

      <div style={{fontSize:12}}>
        {controls.filter(c => c.framework === "Custom").map(c => (
          <div key={c.control_id} style={{padding:8, marginBottom:6, background:"#1112", borderRadius:4, display:"flex", justifyContent:"space-between"}}>
            <div>
              <strong>{c.name}</strong>
              <div style={{color:"#888", fontSize:11}}>{c.description.substring(0, 100)}...</div>
            </div>
            <button 
              onClick={() => deleteControl(c.control_id)}
              style={{padding:"4px 8px", fontSize:11, background:"#f44336", color:"white", border:"none", borderRadius:4, cursor:"pointer"}}
            >
              Delete
            </button>
          </div>
        ))}
        {controls.filter(c => c.framework === "Custom").length === 0 && (
          <div style={{color:"#888", fontSize:11}}>No custom controls yet</div>
        )}
      </div>
    </div>
  );
}

