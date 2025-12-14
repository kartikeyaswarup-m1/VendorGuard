from typing import List, Optional, Dict, Any
from datetime import datetime
from ..models.schemas import AnalysisReportUI, ControlSummary, EvidenceSummary, DocumentMetadata
from .llm import classify_control_with_gemini
from .control_framework import CONTROLS


_STATUS_TO_RISK = {
    "Covered": "Low",
    "Partial": "Medium",
    "Missing": "High",
}


def _normalize_status(value: str) -> str:
    if value in ("Covered", "Partial", "Missing"):
        return value
    return "Missing"


def _split_frameworks(framework_value: Optional[str]) -> List[str]:
    if not framework_value:
        return []
    return [f.strip() for f in framework_value.split(",") if f.strip()]


def _dedupe_top_evidence(evidences: List[Dict[str, Any]], max_items: int = 3) -> List[EvidenceSummary]:
    # Sort by similarity score desc (None -> 0)
    def score_of(e: Dict[str, Any]) -> float:
        s = e.get("similarity_score")
        try:
            return float(s) if s is not None else 0.0
        except Exception:
            return 0.0

    sorted_evs = sorted(evidences or [], key=score_of, reverse=True)
    seen = set()
    top: List[EvidenceSummary] = []

    for e in sorted_evs:
        doc_id = (e.get("doc_id") or "").strip()
        page = e.get("page")
        clause_hash = (e.get("clause_hash") or "").strip()
        key = (doc_id, page, clause_hash)
        if key in seen:
            continue
        seen.add(key)

        snippet = (e.get("snippet") or "").replace("\n", " ").strip()
        excerpt = snippet[:220]
        if not doc_id or not page or not excerpt:
            continue

        top.append(EvidenceSummary(doc=doc_id, page=int(page), excerpt=excerpt))
        if len(top) >= max_items:
            break

    return top


def summarize_for_ui(raw_result: Dict[str, Any]) -> ControlSummary:
    """Convert internal analysis output into a clean UI-facing ControlSummary.

    IMPORTANT: This must not expose raw LLM rationale or follow-up questions.
    """
    status = _normalize_status(str(raw_result.get("status") or "Missing"))
    risk_level = _STATUS_TO_RISK[status]

    confidence_float = raw_result.get("confidence", 0.0)
    try:
        confidence_float = float(confidence_float)
    except Exception:
        confidence_float = 0.0
    confidence_pct = int(round(max(0.0, min(1.0, confidence_float)) * 100))

    control_description = (raw_result.get("control_description") or "").strip()
    evidence = _dedupe_top_evidence(raw_result.get("evidence") or [], max_items=3)

    key_findings: List[str] = []
    if evidence:
        key_findings.append(f"Top evidence found in {evidence[0].doc} (p.{evidence[0].page}).")
        if len(evidence) > 1:
            key_findings.append(f"Additional supporting references across {len(evidence)} excerpts.")
    else:
        key_findings.append("No relevant evidence found in the uploaded documents.")

    missing_requirements: List[str] = []
    if status in ("Partial", "Missing") and control_description:
        missing_requirements.append(control_description)

    recommended_actions: List[str] = []
    if status == "Covered":
        recommended_actions = [
            "Maintain the control and retain current evidence artifacts.",
            "Re-validate periodically (e.g., annually) and on major system changes.",
        ]
    elif status == "Partial":
        recommended_actions = [
            "Clarify scope and document how the control is implemented.",
            "Close remaining gaps and produce an auditable policy/procedure and evidence.",
        ]
    else:
        recommended_actions = [
            "Implement the control and publish a policy/procedure.",
            "Collect evidence (configs, screenshots, reports) demonstrating operation.",
        ]

    return ControlSummary(
        control_id=str(raw_result.get("control_id") or ""),
        control_name=str(raw_result.get("control_name") or ""),
        frameworks=list(raw_result.get("frameworks") or []),
        status=status,
        confidence=confidence_pct,
        risk_level=risk_level,
        key_findings=key_findings,
        missing_requirements=missing_requirements,
        top_evidence=evidence,
        recommended_actions=recommended_actions,
    )


def analyze_vendor_controls(
    vendor_id: str, 
    vendor_name: str, 
    qwrap,
    document_metadata: Optional[List[DocumentMetadata]] = None,
    framework_filter: Optional[str] = None
) -> AnalysisReportUI:
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

    controls_results: List[ControlSummary] = []
    total_weighted = 0.0
    accumulated = 0.0

    # Get all controls
    all_controls = CONTROLS
    
    # Filter by framework if specified
    if framework_filter:
        all_controls = [
            c for c in all_controls
            if framework_filter.upper() in c.get("framework", "").upper()
        ]

    # If no controls are left after filtering, return a benign report instead of 100% risk
    if not all_controls:
        return AnalysisReportUI(
            vendor_id=vendor_id,
            vendor_name=vendor_name,
            overall_risk_score=0.0,
            controls=[],
            documents_analyzed=document_metadata or [],
            analysis_timestamp=datetime.utcnow().isoformat(),
        )

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

        evidences: List[Dict[str, Any]] = []
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

        # Call LLM for classification (handle exceptions so one failure doesn't break everything)
        try:
            resp = classify_control_with_gemini(c["control_id"], c["description"], evidences) or {}
        except Exception as exc:
            resp = {
                "classification": "Missing",
                "confidence": 0.0,
                "rationale": f"LLM error: {exc}",
                "followup_questions": [],
            }

        classification = _normalize_status(resp.get("classification", "Missing"))
        confidence = float(resp.get("confidence", 0.0))

        # Adjust score based on confidence - higher confidence = more weight
        base_mapval = {"Covered": 1.0, "Partial": 0.5, "Missing": 0.0}.get(classification, 0.0)
        # Apply confidence as a multiplier (confidence 0.9 means 90% of the base value)
        adjusted_mapval = base_mapval * confidence
        weight = float(c.get("weight", 0.0))
        total_weighted += weight
        accumulated += adjusted_mapval * weight

        raw_for_ui = {
            "control_id": c.get("control_id"),
            "control_name": c.get("name"),
            "control_description": c.get("description"),
            "frameworks": _split_frameworks(c.get("framework")),
            "status": classification,
            "confidence": confidence,
            "evidence": evidences,
        }
        controls_results.append(summarize_for_ui(raw_for_ui))

    safety_pct = accumulated / total_weighted if total_weighted else 0.0
    risk_score = round((1.0 - safety_pct) * 100, 2)

    report = AnalysisReportUI(
        vendor_id=vendor_id,
        vendor_name=vendor_name,
        overall_risk_score=risk_score,
        controls=controls_results,
        documents_analyzed=document_metadata or [],
        analysis_timestamp=datetime.utcnow().isoformat(),
    )
    return report