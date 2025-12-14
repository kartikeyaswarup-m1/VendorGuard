"""
API endpoints for historical analysis tracking
"""
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import json
import os
from ..config import HISTORY_DIR

router = APIRouter()

class AnalysisHistory(BaseModel):
    vendor_id: str
    vendor_name: Optional[str]
    analysis_timestamp: str
    risk_score: float
    document_count: int
    control_count: int


@router.get("/history/{vendor_id}", response_model=List[AnalysisHistory])
def get_vendor_history(vendor_id: str, limit: int = 10):
    """
    Get analysis history for a vendor.
    
    Args:
        vendor_id: Vendor identifier
        limit: Maximum number of historical analyses to return
    """
    history_file = os.path.join(HISTORY_DIR, f"{vendor_id}_history.json")
    
    if not os.path.exists(history_file):
        return []
    
    try:
        with open(history_file, "r") as f:
            history = json.load(f)
        # Return most recent first, limited
        return sorted(history, key=lambda x: x.get("analysis_timestamp", ""), reverse=True)[:limit]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load history: {str(e)}")


@router.get("/history/{vendor_id}/{timestamp}")
def get_analysis_by_timestamp(vendor_id: str, timestamp: str):
    """
    Get a specific analysis by timestamp.
    
    Args:
        vendor_id: Vendor identifier
        timestamp: ISO timestamp of the analysis
    """
    history_file = os.path.join(HISTORY_DIR, f"{vendor_id}_history.json")
    
    if not os.path.exists(history_file):
        raise HTTPException(status_code=404, detail="History not found")
    
    try:
        with open(history_file, "r") as f:
            history = json.load(f)
        
        for analysis in history:
            if analysis.get("analysis_timestamp") == timestamp:
                return analysis
        
        raise HTTPException(status_code=404, detail="Analysis not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load analysis: {str(e)}")


def save_analysis_to_history(vendor_id: str, report: dict):
    """Save an analysis report to history."""
    history_file = os.path.join(HISTORY_DIR, f"{vendor_id}_history.json")
    
    # Load existing history
    history = []
    if os.path.exists(history_file):
        try:
            with open(history_file, "r") as f:
                history = json.load(f)
        except Exception:
            history = []
    
    # Add summary to history
    history_entry = {
        "vendor_id": report.get("vendor_id"),
        "vendor_name": report.get("vendor_name"),
        "analysis_timestamp": report.get("analysis_timestamp"),
        "risk_score": report.get("overall_risk_score"),
        "document_count": len(report.get("documents_analyzed", [])),
        "control_count": len(report.get("controls", [])),
    }
    
    history.append(history_entry)
    
    # Save full report separately
    report_file = os.path.join(HISTORY_DIR, f"{vendor_id}_{report.get('analysis_timestamp', '').replace(':', '-')}.json")
    try:
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)
    except Exception as e:
        print(f"Warning: Failed to save full report: {e}")
    
    # Save history
    try:
        with open(history_file, "w") as f:
            json.dump(history, f, indent=2)
    except Exception as e:
        print(f"Warning: Failed to save history: {e}")

