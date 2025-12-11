import os
from fastapi import APIRouter, UploadFile, File, HTTPException
from uuid import uuid4
from ..config import UPLOAD_DIR
from ..services.parser import ensure_dir
from ..services.document_classifier import classify_document_type
from ..models.schemas import UploadResponse
import fitz  # PyMuPDF

router = APIRouter()

@router.post("/upload/{vendor_id}", response_model=UploadResponse)
async def upload_pdf(vendor_id: str, file: UploadFile = File(...)):
    ensure_dir(UPLOAD_DIR)
    vendor_folder = os.path.join(UPLOAD_DIR, vendor_id)
    ensure_dir(vendor_folder)

    filename = f"{uuid4()}_{file.filename}"
    path = os.path.join(vendor_folder, filename)

    try:
        content = await file.read()
        with open(path, "wb") as f:
            f.write(content)
        
        # Classify document type
        doc_type = classify_document_type(file.filename)
        
        # Try to get content preview for better classification
        try:
            doc = fitz.open(path)
            if len(doc) > 0:
                first_page = doc[0]
                content_preview = first_page.get_text("text")[:2000]
                doc_type = classify_document_type(file.filename, content_preview)
            doc.close()
        except Exception:
            pass  # If classification fails, use filename-based classification
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return UploadResponse(
        vendor_id=vendor_id, 
        filename=filename, 
        path=path,
        document_type=doc_type
    )