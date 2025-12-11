"""
API endpoints for control management
"""
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from ..services.control_framework import CONTROLS, get_controls_by_framework, get_controls_by_category

router = APIRouter()


class ControlResponse(BaseModel):
    control_id: str
    name: str
    description: str
    framework: str
    category: str
    weight: float


class CustomControlRequest(BaseModel):
    control_id: str
    name: str
    description: str
    framework: str = "Custom"
    category: str = "Custom"
    weight: float = 1.0


# In-memory storage for custom controls (in production, use a database)
custom_controls: List[dict] = []


@router.get("/controls", response_model=List[ControlResponse])
def get_controls(framework: Optional[str] = None, category: Optional[str] = None):
    """
    Get all controls, optionally filtered by framework or category.
    
    Args:
        framework: Filter by framework (SOC2, ISO27001, NIST, GDPR, etc.)
        category: Filter by category (Data Protection, Access Control, etc.)
    """
    controls = CONTROLS + custom_controls
    
    if framework:
        controls = [c for c in controls if framework.upper() in c.get("framework", "").upper()]
    
    if category:
        controls = [c for c in controls if c.get("category", "").lower() == category.lower()]
    
    return controls


@router.get("/controls/frameworks")
def get_frameworks():
    """Get list of all available frameworks."""
    frameworks = set()
    for c in CONTROLS + custom_controls:
        framework_str = c.get("framework", "")
        if framework_str:
            frameworks.update([f.strip() for f in framework_str.split(",")])
    return sorted(list(frameworks))


@router.get("/controls/categories")
def get_categories():
    """Get list of all control categories."""
    categories = set()
    for c in CONTROLS + custom_controls:
        cat = c.get("category")
        if cat:
            categories.add(cat)
    return sorted(list(categories))


@router.post("/controls/custom", response_model=ControlResponse)
def add_custom_control(control: CustomControlRequest):
    """
    Add a custom control.
    
    Args:
        control: Custom control definition
    """
    # Check if control_id already exists
    all_controls = CONTROLS + custom_controls
    if any(c["control_id"] == control.control_id for c in all_controls):
        raise HTTPException(status_code=400, detail=f"Control ID {control.control_id} already exists")
    
    custom_control = {
        "control_id": control.control_id,
        "name": control.name,
        "description": control.description,
        "framework": control.framework,
        "category": control.category,
        "weight": control.weight,
    }
    custom_controls.append(custom_control)
    return custom_control


@router.delete("/controls/custom/{control_id}")
def delete_custom_control(control_id: str):
    """Delete a custom control."""
    global custom_controls
    original_count = len(custom_controls)
    custom_controls = [c for c in custom_controls if c["control_id"] != control_id]
    
    if len(custom_controls) == original_count:
        raise HTTPException(status_code=404, detail=f"Custom control {control_id} not found")
    
    return {"message": f"Control {control_id} deleted"}

