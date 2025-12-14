from __future__ import annotations
from pydantic import BaseModel
from typing import List, Optional, Literal
from enum import Enum


class DocumentType(str, Enum):
    CONTRACT = "contract"
    SLA = "sla"
    SOC2 = "soc2"
    ISO = "iso"
    SECURITY_POLICY = "security_policy"
    PRIVACY_POLICY = "privacy_policy"
    OTHER = "other"


class UploadResponse(BaseModel):
    vendor_id: str
    filename: str
    path: str
    document_type: Optional[DocumentType] = None


class EvidenceItem(BaseModel):
    doc_id: str
    doc_type: Optional[str] = None  # Document type (contract, SOC2, etc.)
    page: int
    snippet: str
    clause_hash: str
    similarity_score: Optional[float] = None


class ControlResult(BaseModel):
    control_id: str
    name: str
    classification: str  # Covered/Partial/Missing
    confidence: float
    evidence: List[EvidenceItem]
    rationale: str
    followup_questions: List[str]
    framework: Optional[str] = None  # e.g., "SOC2", "ISO27001", "Custom"


class EvidenceSummary(BaseModel):
    doc: str
    page: int
    excerpt: str


class ControlSummary(BaseModel):
    control_id: str
    control_name: str
    frameworks: List[str]
    status: Literal["Covered", "Partial", "Missing"]
    confidence: int  # percentage 0-100
    risk_level: Literal["Low", "Medium", "High"]
    key_findings: List[str]
    missing_requirements: List[str]
    top_evidence: List[EvidenceSummary]  # max 3
    recommended_actions: List[str]


class AnalysisReportUI(BaseModel):
    vendor_id: str
    vendor_name: Optional[str]
    overall_risk_score: float
    controls: List[ControlSummary]
    documents_analyzed: List[DocumentMetadata] = []
    analysis_timestamp: Optional[str] = None


class DocumentMetadata(BaseModel):
    doc_id: str
    doc_type: Optional[DocumentType] = None
    filename: str
    page_count: Optional[int] = None


class AnalysisReport(BaseModel):
    vendor_id: str
    vendor_name: Optional[str]
    overall_risk_score: float
    controls: List[ControlResult]
    documents_analyzed: List[DocumentMetadata] = []
    analysis_timestamp: Optional[str] = None
