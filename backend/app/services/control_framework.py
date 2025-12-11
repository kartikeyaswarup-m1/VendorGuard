"""
Comprehensive Control Framework
Defines security controls from multiple frameworks: SOC2, ISO27001, NIST, etc.
"""
from typing import List, Dict

# Comprehensive control framework covering multiple standards
CONTROLS: List[Dict] = [
    # Encryption & Data Protection
    {
        "control_id": "C-ENCR-01",
        "name": "Encryption at Rest",
        "description": "Data must be encrypted at rest using AES-256 or equivalent encryption standard",
        "framework": "SOC2,ISO27001,NIST",
        "category": "Data Protection",
        "weight": 1.0,
    },
    {
        "control_id": "C-ENCR-02",
        "name": "Encryption in Transit",
        "description": "Data must be encrypted in transit using TLS 1.2 or higher",
        "framework": "SOC2,ISO27001,NIST",
        "category": "Data Protection",
        "weight": 1.0,
    },
    {
        "control_id": "C-DATA-01",
        "name": "Data Classification",
        "description": "Vendor must classify data and apply appropriate protection measures based on sensitivity",
        "framework": "ISO27001,NIST",
        "category": "Data Protection",
        "weight": 0.8,
    },
    
    # Access Control
    {
        "control_id": "C-ACCESS-01",
        "name": "Access Control Policy",
        "description": "Vendor must have documented access control policies and procedures",
        "framework": "SOC2,ISO27001",
        "category": "Access Control",
        "weight": 0.9,
    },
    {
        "control_id": "C-ACCESS-02",
        "name": "Multi-Factor Authentication",
        "description": "Vendor must implement MFA for privileged access and remote access",
        "framework": "SOC2,ISO27001,NIST",
        "category": "Access Control",
        "weight": 1.0,
    },
    {
        "control_id": "C-ACCESS-03",
        "name": "Access Reviews",
        "description": "Vendor must conduct periodic access reviews and remove unnecessary access",
        "framework": "SOC2,ISO27001",
        "category": "Access Control",
        "weight": 0.8,
    },
    
    # Third-Party & Subprocessors
    {
        "control_id": "C-SUB-01",
        "name": "Subprocessor Disclosure",
        "description": "Vendor must disclose subprocessors and provide notice of changes",
        "framework": "SOC2,GDPR",
        "category": "Third-Party Risk",
        "weight": 0.9,
    },
    {
        "control_id": "C-SUB-02",
        "name": "Subprocessor Due Diligence",
        "description": "Vendor must perform due diligence on subprocessors and ensure they meet security requirements",
        "framework": "SOC2,ISO27001",
        "category": "Third-Party Risk",
        "weight": 0.8,
    },
    
    # Backup & Recovery
    {
        "control_id": "C-BACK-01",
        "name": "Backups & Retention",
        "description": "Vendor must maintain backups and specify retention periods",
        "framework": "SOC2,ISO27001",
        "category": "Business Continuity",
        "weight": 0.9,
    },
    {
        "control_id": "C-BACK-02",
        "name": "Disaster Recovery",
        "description": "Vendor must have documented disaster recovery plan and test it regularly",
        "framework": "SOC2,ISO27001",
        "category": "Business Continuity",
        "weight": 0.8,
    },
    
    # Monitoring & Logging
    {
        "control_id": "C-MON-01",
        "name": "Security Monitoring",
        "description": "Vendor must monitor systems for security events and anomalies",
        "framework": "SOC2,ISO27001,NIST",
        "category": "Monitoring",
        "weight": 0.9,
    },
    {
        "control_id": "C-MON-02",
        "name": "Log Management",
        "description": "Vendor must maintain security logs and retain them for appropriate periods",
        "framework": "SOC2,ISO27001",
        "category": "Monitoring",
        "weight": 0.8,
    },
    {
        "control_id": "C-MON-03",
        "name": "Incident Response",
        "description": "Vendor must have incident response procedures and notify customers of breaches",
        "framework": "SOC2,ISO27001,NIST",
        "category": "Monitoring",
        "weight": 1.0,
    },
    
    # Vulnerability Management
    {
        "control_id": "C-VULN-01",
        "name": "Vulnerability Management",
        "description": "Vendor must regularly scan for vulnerabilities and apply patches promptly",
        "framework": "SOC2,ISO27001,NIST",
        "category": "Vulnerability Management",
        "weight": 0.9,
    },
    {
        "control_id": "C-VULN-02",
        "name": "Penetration Testing",
        "description": "Vendor must conduct regular penetration testing by qualified third parties",
        "framework": "SOC2,ISO27001",
        "category": "Vulnerability Management",
        "weight": 0.8,
    },
    
    # Change Management
    {
        "control_id": "C-CHANGE-01",
        "name": "Change Management",
        "description": "Vendor must have change management procedures for system modifications",
        "framework": "SOC2,ISO27001",
        "category": "Change Management",
        "weight": 0.7,
    },
    
    # Compliance & Audits
    {
        "control_id": "C-AUDIT-01",
        "name": "Security Audits",
        "description": "Vendor must undergo regular security audits and provide audit reports",
        "framework": "SOC2,ISO27001",
        "category": "Compliance",
        "weight": 0.9,
    },
    {
        "control_id": "C-AUDIT-02",
        "name": "Compliance Certifications",
        "description": "Vendor must maintain relevant security certifications (SOC2, ISO27001, etc.)",
        "framework": "SOC2,ISO27001",
        "category": "Compliance",
        "weight": 0.8,
    },
    
    # Privacy & Data Rights
    {
        "control_id": "C-PRIV-01",
        "name": "Data Subject Rights",
        "description": "Vendor must support data subject rights (access, deletion, portability) per GDPR/CCPA",
        "framework": "GDPR,CCPA",
        "category": "Privacy",
        "weight": 0.9,
    },
    {
        "control_id": "C-PRIV-02",
        "name": "Data Processing Agreement",
        "description": "Vendor must have data processing agreements that comply with applicable privacy laws",
        "framework": "GDPR,CCPA",
        "category": "Privacy",
        "weight": 0.8,
    },
    
    # Service Level Agreements
    {
        "control_id": "C-SLA-01",
        "name": "Uptime SLA",
        "description": "Vendor must specify uptime/availability SLA and provide credits for violations",
        "framework": "SLA",
        "category": "Service Level",
        "weight": 0.7,
    },
    {
        "control_id": "C-SLA-02",
        "name": "Performance Metrics",
        "description": "Vendor must define and monitor performance metrics and service levels",
        "framework": "SLA",
        "category": "Service Level",
        "weight": 0.6,
    },
]


def get_controls_by_framework(framework: str = None) -> List[Dict]:
    """
    Get controls filtered by framework.
    
    Args:
        framework: Framework name (SOC2, ISO27001, NIST, GDPR, etc.) or None for all
    
    Returns:
        List of control dictionaries
    """
    if framework is None:
        return CONTROLS
    
    framework_upper = framework.upper()
    return [
        c for c in CONTROLS
        if framework_upper in c.get("framework", "").upper()
    ]


def get_controls_by_category(category: str = None) -> List[Dict]:
    """
    Get controls filtered by category.
    
    Args:
        category: Category name or None for all
    
    Returns:
        List of control dictionaries
    """
    if category is None:
        return CONTROLS
    
    return [
        c for c in CONTROLS
        if c.get("category", "").lower() == category.lower()
    ]

