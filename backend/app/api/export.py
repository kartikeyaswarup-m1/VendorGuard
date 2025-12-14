"""
API endpoints for exporting analysis reports
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from typing import Optional
import json
import os
from datetime import datetime
from io import BytesIO
import csv

router = APIRouter()


@router.get("/export/{vendor_id}/json")
def export_json(vendor_id: str, timestamp: Optional[str] = None):
    """
    Export analysis report as JSON.
    
    Args:
        vendor_id: Vendor identifier
        timestamp: Optional timestamp to export specific analysis
    """
    from ..api.history import HISTORY_DIR
    
    if timestamp:
        report_file = os.path.join(HISTORY_DIR, f"{vendor_id}_{timestamp.replace(':', '-')}.json")
        if not os.path.exists(report_file):
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        return FileResponse(
            report_file,
            media_type="application/json",
            filename=f"vendorguard_{vendor_id}_{timestamp}.json"
        )
    else:
        # Get latest analysis
        history_file = os.path.join(HISTORY_DIR, f"{vendor_id}_history.json")
        if not os.path.exists(history_file):
            raise HTTPException(status_code=404, detail="No analysis history found")
        
        with open(history_file, "r") as f:
            history = json.load(f)
        
        if not history:
            raise HTTPException(status_code=404, detail="No analysis history found")
        
        latest = sorted(history, key=lambda x: x.get("analysis_timestamp", ""), reverse=True)[0]
        timestamp = latest.get("analysis_timestamp", "").replace(":", "-")
        report_file = os.path.join(HISTORY_DIR, f"{vendor_id}_{timestamp}.json")
        
        if not os.path.exists(report_file):
            raise HTTPException(status_code=404, detail="Analysis file not found")
        
        return FileResponse(
            report_file,
            media_type="application/json",
            filename=f"vendorguard_{vendor_id}_latest.json"
        )


@router.get("/export/{vendor_id}/csv")
def export_csv(vendor_id: str, timestamp: Optional[str] = None):
    """
    Export analysis report as CSV.
    
    Args:
        vendor_id: Vendor identifier
        timestamp: Optional timestamp to export specific analysis
    """
    from ..api.history import HISTORY_DIR
    
    if timestamp:
        report_file = os.path.join(HISTORY_DIR, f"{vendor_id}_{timestamp.replace(':', '-')}.json")
    else:
        # Get latest
        history_file = os.path.join(HISTORY_DIR, f"{vendor_id}_history.json")
        if not os.path.exists(history_file):
            raise HTTPException(status_code=404, detail="No analysis history found")
        
        with open(history_file, "r") as f:
            history = json.load(f)
        
        if not history:
            raise HTTPException(status_code=404, detail="No analysis history found")
        
        latest = sorted(history, key=lambda x: x.get("analysis_timestamp", ""), reverse=True)[0]
        timestamp = latest.get("analysis_timestamp", "").replace(":", "-")
        report_file = os.path.join(HISTORY_DIR, f"{vendor_id}_{timestamp}.json")
    
    if not os.path.exists(report_file):
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    with open(report_file, "r") as f:
        report = json.load(f)
    
    # Create CSV
    output = BytesIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow([
        "Control ID", "Control Name", "Frameworks", "Status",
        "Confidence (%)", "Risk Level"
    ])
    
    # Data rows
    for control in report.get("controls", []):
        frameworks = control.get("frameworks", [])
        if isinstance(frameworks, list):
            frameworks_str = ",".join(frameworks)
        else:
            frameworks_str = str(frameworks or "")
        writer.writerow([
            control.get("control_id", ""),
            control.get("control_name", ""),
            frameworks_str,
            control.get("status", ""),
            control.get("confidence", 0),
            control.get("risk_level", ""),
        ])
    
    output.seek(0)
    
    return StreamingResponse(
        BytesIO(output.read()),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=vendorguard_{vendor_id}_{timestamp or 'latest'}.csv"}
    )


@router.get("/export/{vendor_id}/pdf")
def export_pdf(vendor_id: str, timestamp: Optional[str] = None):
    """
    Export analysis report as PDF.
    Note: This is a placeholder - in production, use a library like reportlab or weasyprint
    """
    # For now, return JSON with instructions
    # In production, generate actual PDF using reportlab or similar
    raise HTTPException(
        status_code=501,
        detail="PDF export not yet implemented. Use JSON or CSV export instead."
    )

