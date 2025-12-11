from typing import List, Optional
from datetime import datetime
from ..models.schemas import AnalysisReport, ControlResult, EvidenceItem, DocumentMetadata
from .llm import classify_control_with_gemini
from .control_framework import CONTROLS
from ..api.controls import custom_controls


def analyze_vendor_controls(
    vendor_id: str, 
    vendor_name: str, 
    qwrap,
    document_metadata: Optional[List[DocumentMetadata]] = None,
    framework_filter: Optional[str] = None
) -> AnalysisReport:
    """
    Analyze vendor controls using embeddings + LLM classification.

    Args:
        vendor_id: identifier for the vendor
        vendor_name: human-readable vendor name
        qwrap: an object providing .search(vector, limit=..., with_payload=True) that returns hits
               where each hit has .payload (dict) and .id (or .clause_hash) attributes
        document_metadata: List of analyzed documents
        framework_filter: Optional framework to filter controls (SOC2, ISO27001, etc.)

    Returns:
        AnalysisReport dataclass (from ..models.schemas)
    """
    # local import to avoid potential circular imports
    from .embeddings import embed_texts

    controls_results: List[ControlResult] = []
    total_weighted = 0.0
    accumulated = 0.0

    # Get all controls (standard + custom)
    custom_controls_list = _get_custom_controls()
    all_controls = CONTROLS + custom_controls_list
    
    # Filter by framework if specified
    if framework_filter:
        all_controls = [
            c for c in all_controls
            if framework_filter.upper() in c.get("framework", "").upper()
        ]

    for c in all_controls:
        # Create expanded query with related terms for better search
        query = c["description"]
        # Add control name and key terms to improve search
        expanded_query = f"{c['name']}. {query}"
        
        # embed_texts should return a list of vectors for the provided texts
        qvecs = embed_texts([expanded_query])
        qvec = qvecs[0] if qvecs else None

        hits = []
        if qvec is not None:
            # Use lower score threshold (0.2) to catch more potentially relevant results
            # The LLM will filter out irrelevant ones
            hits = qwrap.search(qvec, limit=20, with_payload=True, vendor_id=vendor_id, score_threshold=0.2)

        evidences = []
        # Sort hits by score (similarity) if available, highest first
        scored_hits = []
        for h in hits:
            score = getattr(h, "score", 0.0)
            scored_hits.append((score, h))
        scored_hits.sort(key=lambda x: x[0], reverse=True)
        
        for score, h in scored_hits:
            payload = getattr(h, "payload", {}) or {}
            # Always prefer clause_hash from payload, fallback to string conversion of point ID
            clause_hash = payload.get("clause_hash")
            if not clause_hash:
                clause_hash = str(getattr(h, "id", ""))
            evidences.append(
                {
                    "doc_id": payload.get("doc_id"),
                    "doc_type": payload.get("doc_type"),  # Include document type
                    "page": payload.get("page"),
                    "snippet": payload.get("preview", ""),
                    "clause_hash": clause_hash,
                    "similarity_score": round(score, 3) if score else None,
                }
            )

        # Call Gemini LLM for classification (handle exceptions so one failure doesn't break everything)
        try:
            resp = classify_control_with_gemini(c["control_id"], c["description"], evidences) or {}
        except Exception as exc:
            resp = {
                "classification": "Missing",
                "confidence": 0.0,
                "rationale": f"LLM error: {exc}",
                "followup_questions": [],
            }

        classification = resp.get("classification", "Missing")
        confidence = float(resp.get("confidence", 0.0))
        rationale = resp.get("rationale", "")
        followups = resp.get("followup_questions", []) or []

        # Adjust score based on confidence - higher confidence = more weight
        base_mapval = {"Covered": 1.0, "Partial": 0.5, "Missing": 0.0}.get(classification, 0.0)
        # Apply confidence as a multiplier (confidence 0.9 means 90% of the base value)
        adjusted_mapval = base_mapval * confidence
        weight = float(c.get("weight", 0.0))
        total_weighted += weight
        accumulated += adjusted_mapval * weight

        evidence_items: List[EvidenceItem] = []
        # Show top 5 most relevant evidence items (sorted by similarity score)
        for e in evidences[:5]:
            snippet = (e.get("snippet") or "")[:800]  # Increased from 500 to 800
            evidence_items.append(
                EvidenceItem(
                    doc_id=e.get("doc_id"),
                    doc_type=e.get("doc_type"),
                    page=e.get("page"),
                    snippet=snippet,
                    clause_hash=e.get("clause_hash"),
                    similarity_score=e.get("similarity_score"),
                )
            )

        controls_results.append(
            ControlResult(
                control_id=c["control_id"],
                name=c["name"],
                classification=classification,
                confidence=confidence,
                evidence=evidence_items,
                rationale=rationale,
                followup_questions=followups,
                framework=c.get("framework", "Custom"),
            )
        )

    safety_pct = accumulated / total_weighted if total_weighted else 0.0
    risk_score = round((1.0 - safety_pct) * 100, 2)

    report = AnalysisReport(
        vendor_id=vendor_id,
        vendor_name=vendor_name,
        overall_risk_score=risk_score,
        controls=controls_results,
        documents_analyzed=document_metadata or [],
        analysis_timestamp=datetime.utcnow().isoformat(),
    )
    return report