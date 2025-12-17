# VendorGuard

Analyze vendor security, legal, and compliance documents using a Retrieval-Augmented Generation (RAG) based risk assessment system.

## Features

- Multi-Document Analysis – Upload and analyze multiple vendor PDFs together.
- Compliance Evaluation – Assess documents against predefined security controls.
- RAG Architecture – Evidence-backed analysis using embeddings and semantic search.
- Vector Database – Qdrant-based storage and retrieval of document chunks.
- Risk Scoring – Quantitative risk scores derived from control coverage.
- Framework Support – SOC 2, ISO 27001, GDPR, and partial NIST coverage.
- Modern Web UI – Clean Next.js interface with step-based progress tracking.
- Structured Reports – Control-level findings with metadata and evidence.

## Architecture

```
Vendor Documents (PDF)
        ↓
PDF Text Extraction
        ↓
Text Chunking
        ↓
Embedding Generation
        ↓
Qdrant Vector Store
        ↓
Semantic Retrieval (RAG)
        ↓
LLM-based Control Evaluation
        ↓
Risk Scoring & Compliance Report
        ↓
Web UI Visualization
```

## Prerequisites

1. Python 3.10+
2. Node.js 18+
3. Docker
4. Qdrant (via Docker)
5. Embedding / LLM Provider (Google Gemini by default)

## Installation

### 1. Clone the Repository
```
git clone https://github.com/your-username/VendorGuard.git
cd VendorGuard
```
### 2. Start Qdrant
```
docker run -d \
  -p 6333:6333 \
  -v qdrant_storage:/qdrant/storage \
  qdrant/qdrant:latest
```
### 3. Backend Setup (FastAPI)

```
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
Create a .env file:
```
UPLOAD_DIR=/tmp/vendorguard/uploads
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=
EMBEDDING_PROVIDER=gemini
LLM_PROVIDER=gemini
GEMINI_EMBEDDING_MODEL=gemini-embedding-001
GEMINI_LLM_MODEL=gemini-2.5-flash
EMBEDDING_DIM=768
ALLOWED_ORIGINS=http://localhost:3000
```
Start the backend:
```
uvicorn main:app --reload
```
```
Backend runs on http://localhost:8000
```

### 4. Frontend Setup (Next.js)

```
cd ../frontend
npm install
```

Create .env.local:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Start the frontend:

```
npm run dev
```
```
Frontend runs on http://localhost:3000
```

## Usage

### Quick Start

1. Open the web UI in your browser
2. Upload one or more vendor PDF documents
3. Trigger analysis
4. Monitor progress using the step indicator
5. Review risk score and compliance findings

## API Flow

1. Upload documents for a vendor
2. Trigger analysis request
3. Backend parses and chunks documents
4. Embeddings are generated and stored in Qdrant
5. Relevant chunks are retrieved per control
6. LLM evaluates compliance and risk
7. Structured report is returned to the frontend

## Project Structure

```
VendorGuard/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── services/
│   │   ├── models/
│   │   └── core/
│   ├── main.py
│   └── requirements.txt
├── frontend/
│   ├── app/ or pages/
│   ├── components/
│   ├── styles/
│   └── public/
├── docker/
│   └── docker-compose.yml
└── README.md
```

## Configuration

Backend configuration is controlled via .env:

```
EMBEDDING_DIM=768
ALLOWED_ORIGINS=http://localhost:3000
GEMINI_LLM_MODEL=gemini-2.5-flash
```
## Limitations

- No authentication or authorization
- Single analysis session at a time
- Limited retry and rate-limit handling
- No persistent background job queue

## Future Enhancements

- Authentication and role-based access
- Background job processing
- Analysis history and dashboards
- Framework-specific scoring models
- Improved evidence traceability
- Model-agnostic provider switching
- Dockerized production deployment

## License

See the LICENSE file for details.

## Author

Created by 
[kartikeyaswarup-m1](https://github.com/kartikeyaswarup-m1)

## Acknowledgments

- FastAPI, Next.js, Qdrant, and Tailwind CSS communities
- Public documentation for SOC 2, ISO 27001, GDPR, and NIST
- Research and open-source work on Retrieval-Augmented Generation