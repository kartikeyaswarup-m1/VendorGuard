"""
API endpoints for control management
"""
from fastapi import APIRouter
from typing import List, Optional
from pydantic import BaseModel
from ..services.control_framework import CONTROLS

router = APIRouter()


class ControlResponse(BaseModel):
    control_id: str
    name: str
    description: str
    framework: str
    category: str
    weight: float


@router.get("/controls", response_model=List[ControlResponse])
def get_controls(framework: Optional[str] = None, category: Optional[str] = None):
    """
    Get all controls, optionally filtered by framework or category.
    
    Args:
        framework: Filter by framework (SOC2, ISO27001, NIST, GDPR, etc.)
        category: Filter by category (Data Protection, Access Control, etc.)
    """
    controls = CONTROLS
    
    if framework:
        controls = [c for c in controls if framework.upper() in c.get("framework", "").upper()]
    
    if category:
        controls = [c for c in controls if c.get("category", "").lower() == category.lower()]
    
    return controls


@router.get("/controls/frameworks")
def get_frameworks():
    """Get list of all available frameworks."""
    frameworks = set()
    for c in CONTROLS:
        framework_str = c.get("framework", "")
        if framework_str:
            frameworks.update([f.strip() for f in framework_str.split(",")])
    return sorted(list(frameworks))


@router.get("/controls/categories")
def get_categories():
    """Get list of all control categories."""
    categories = set()
    for c in CONTROLS:
        cat = c.get("category")
        if cat:
            categories.add(cat)
    return sorted(list(categories))

