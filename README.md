VendorGuard — AI-Powered Vendor Security Compliance Analyzer

VendorGuard is an end-to-end system for analyzing vendor security documents using RAG (Retrieval-Augmented Generation), vector search, and LLM-based classification.
It ingests multiple document types (Contracts, SLAs, SOC2, ISO27001, GDPR policies), extracts evidence, maps them to security frameworks, and generates detailed compliance and risk reports.

🚀 Key Features

🔍 1. Multi-Document Support

Analyze multiple documents per vendor, including:
	•	Contracts / MSAs
	•	SLAs
	•	SOC2 reports
	•	ISO 27001 reports
	•	Privacy policies (GDPR/CCPA)
Each document is processed, chunked, embedded, and linked to a single vendor profile.

🧠 2. Automatic Document Classification

VendorGuard automatically predicts the type of each uploaded document using semantic cues:
	•	“Service Agreement” → Contract
	•	“Annex A” → ISO 27001
	•	“SOC2 Type II Audit” → SOC2
	•	“Data Subject Rights” → GDPR

📄 3. Page-Level Evidence Tracking

All extracted evidence includes:
	•	Page number
	•	Document source
	•	Similarity score
	•	Confidence score

📚 4. Comprehensive Framework Coverage

VendorGuard currently maps controls to:
	•	SOC 2 (Security, Availability, Confidentiality)
	•	ISO 27001:2022 Annex A
	•	NIST 800-53
	•	GDPR
	•	CCPA

🤖 5. RAG Architecture (Semantic Search + LLM)
	•	Qdrant vector store for chunk embeddings
	•	Filtering by vendor, document type, similarity threshold
	•	Reranking evidence
	•	LLM evaluates coverage: Covered, Partial, Missing
	•	Includes explanation, reasoning, and evidence citations

📈 6. Confidence-Weighted Risk Scoring

Every classification includes:
	•	Coverage level
	•	Confidence score
	•	Evidence similarity

Final risk score formula:
risk = (1 - weighted_security_percentage) × 100


Each analysis stores:
	•	vendor_id
	•	document_name
	•	document_type
	•	page count
	•	timestamp of analysis

🏗 Architecture Overview
Frontend (Next.js)
     ↓ Upload PDFs
Backend (FastAPI)
     ↓
PDF Parser → Chunker → Embeddings → Qdrant DB
     ↓
Semantic Search → Evidence Reranking → LLM Classification
     ↓
Risk Score Calculation → Final Report (JSON)

Installation & Setup

1. Clone the repo
git clone https://github.com/YOUR_USERNAME/VendorGuard.git
cd VendorGuard

2. Environment Variables
GOOGLE_API_KEY=your_key_here
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=none_or_key

3. Run Docker Services
docker-compose up --build

Services started:
	•	FastAPI on localhost:8000
	•	Qdrant on localhost:6333
	•	Frontend on localhost:3000

Planned Improvements

Short Term
	•	Local embeddings to reduce API cost
	•	Reranking using BM25
	•	Enhanced chunk overlap
	•	Caching layer for embeddings

Long Term
	•	Human-in-the-loop correction
	•	Remediation recommendations
	•	PDF highlighting (visual evidence)
	•	SOC2, ISO, NIST control customization
	•	Cross-vendor comparison dashboard

Contributing

Pull requests welcome!
Please run formatting and linting before submitting:
black .
flake8 .

