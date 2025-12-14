from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from typing import List, Optional
from ..services.parser import extract_text_chunks
from ..services.embeddings import embed_texts
from ..services.qdrant_client import QdrantClientWrapper
from ..services.analyzer import analyze_vendor_controls
from ..services.document_classifier import classify_document_type
from ..models.schemas import AnalysisReportUI, DocumentMetadata
import os
import fitz  # PyMuPDF

router = APIRouter()
qwrap = QdrantClientWrapper()


class AnalyzeRequest(BaseModel):
    vendor_name: Optional[str] = None
    file_paths: List[str]
    framework_filter: Optional[str] = None  # Filter controls by framework (SOC2, ISO27001, etc.)


@router.post("/analyze/{vendor_id}", response_model=AnalysisReportUI)
def analyze(vendor_id: str, request: AnalyzeRequest):
    """
    file_paths: list of local PDF paths to ingest for this vendor
    """
    file_paths = request.file_paths
    vendor_name = request.vendor_name
    if not file_paths:
        raise HTTPException(status_code=400, detail="Provide file_paths list in body")
    
    try:
        all_chunks = []
        document_metadata_list = []
        
        # Process each document
        for p in file_paths:
            if not os.path.exists(p):
                continue
                
            filename = os.path.basename(p)
            
            # Classify document type
            doc_type = classify_document_type(filename)
            
            # Get page count
            try:
                doc = fitz.open(p)
                page_count = len(doc)
                # Get content preview for better classification
                content_preview = ""
                if page_count > 0:
                    first_page = doc[0]
                    content_preview = first_page.get_text("text")[:2000]
                doc.close()
                # Re-classify with content preview
                doc_type = classify_document_type(filename, content_preview)
            except Exception:
                page_count = None
                content_preview = None
            
            # Extract text chunks
            chunks = extract_text_chunks(p)
            for c in chunks:
                c["doc_id"] = filename
                c["doc_type"] = doc_type.value if doc_type else None
                all_chunks.append(c)
            
            # Store document metadata
            document_metadata_list.append(
                DocumentMetadata(
                    doc_id=filename,
                    doc_type=doc_type,
                    filename=filename,
                    page_count=page_count
                )
            )
        
        if not all_chunks:
            raise HTTPException(status_code=400, detail="No text extracted from PDFs")
        
        texts = [c["text"] for c in all_chunks]
        embeddings = embed_texts(texts)
        points = []
        import hashlib
        for i, (c, emb) in enumerate(zip(all_chunks, embeddings)):
            # Generate unique point ID using vendor_id, doc_id, and clause_hash
            # This ensures no collisions across different uploads
            unique_id_str = f"{vendor_id}:{c['doc_id']}:{c['clause_hash']}:{i}"
            point_id = int(hashlib.md5(unique_id_str.encode()).hexdigest()[:15], 16)
            points.append({
                "id": point_id,
                "vector": emb,
                "payload": {
                    "vendor_id": vendor_id,
                    "doc_id": c["doc_id"],
                    "doc_type": c.get("doc_type"),  # Include document type
                    "page": c["page"],
                    "clause_hash": c["clause_hash"],
                    "preview": c["text"][:800]  # Increased from 400 to 800 for better context
                }
            })
        qwrap.upsert_points(points)
        report = analyze_vendor_controls(
            vendor_id, 
            vendor_name, 
            qwrap, 
            document_metadata_list,
            framework_filter=request.framework_filter
        )
        
        # Save to history
        try:
            from .history import save_analysis_to_history
            save_analysis_to_history(vendor_id, report.dict())
        except Exception as e:
            print(f"Warning: Failed to save to history: {e}")
        
        return report
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=f"Qdrant unavailable: {str(e)}. Please ensure Qdrant is running on http://localhost:6333")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")