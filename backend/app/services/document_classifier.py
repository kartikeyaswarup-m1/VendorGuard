"""
Document Type Classifier
Automatically detects document types based on filename and content patterns.
"""
import re
from typing import Optional
from ..models.schemas import DocumentType


def classify_document_type(filename: str, content_preview: Optional[str] = None) -> DocumentType:
    """
    Classify document type based on filename patterns and optional content preview.
    
    Args:
        filename: The document filename
        content_preview: Optional preview of document content (first 2000 chars)
    
    Returns:
        DocumentType enum value
    """
    filename_lower = filename.lower()
    
    # SOC2 patterns
    soc2_patterns = [
        r'soc.?2', r'type.?2', r'soc.?ii', r'system.?organization.?controls',
        r'service.?organization.?control', r'audit.?report', r'attestation'
    ]
    if any(re.search(pattern, filename_lower) for pattern in soc2_patterns):
        return DocumentType.SOC2
    
    # ISO patterns
    iso_patterns = [
        r'iso.?27001', r'iso.?27002', r'iso.?27017', r'iso.?27018',
        r'iso.?27701', r'information.?security.?management',
        r'isms', r'certification'
    ]
    if any(re.search(pattern, filename_lower) for pattern in iso_patterns):
        return DocumentType.ISO
    
    # SLA patterns
    sla_patterns = [
        r'sla', r'service.?level.?agreement', r'service.?agreement',
        r'performance.?agreement', r'operational.?level.?agreement'
    ]
    if any(re.search(pattern, filename_lower) for pattern in sla_patterns):
        return DocumentType.SLA
    
    # Contract patterns
    contract_patterns = [
        r'contract', r'agreement', r'msa', r'master.?service',
        r'terms.?of.?service', r'terms.?and.?conditions', r'engagement.?letter'
    ]
    if any(re.search(pattern, filename_lower) for pattern in contract_patterns):
        return DocumentType.CONTRACT
    
    # Privacy Policy patterns
    privacy_patterns = [
        r'privacy.?policy', r'privacy.?notice', r'data.?protection',
        r'gdpr', r'ccpa', r'privacy.?statement'
    ]
    if any(re.search(pattern, filename_lower) for pattern in privacy_patterns):
        return DocumentType.PRIVACY_POLICY
    
    # Security Policy patterns
    security_patterns = [
        r'security.?policy', r'information.?security', r'cyber.?security',
        r'security.?standards', r'security.?framework'
    ]
    if any(re.search(pattern, filename_lower) for pattern in security_patterns):
        return DocumentType.SECURITY_POLICY
    
    # Content-based classification if preview available
    if content_preview:
        content_lower = content_preview.lower()
        
        # Check for SOC2 indicators in content
        if any(term in content_lower for term in ['trust services criteria', 'tsc', 'cc6.1', 'cc7.1', 'common criteria']):
            return DocumentType.SOC2
        
        # Check for ISO indicators
        if any(term in content_lower for term in ['iso/iec 27001', 'iso 27001', 'isms', 'information security management system']):
            return DocumentType.ISO
        
        # Check for SLA indicators
        if any(term in content_lower for term in ['service level', 'uptime', 'availability target', 'sla']):
            return DocumentType.SLA
    
    return DocumentType.OTHER

