VendorGuard

Overview

VendorGuard is a vendor security and compliance analysis system designed to assess third-party risk using security, legal, and compliance documents. The system ingests vendor-provided PDFs, extracts and semantically analyzes their content, and produces structured compliance reports and risk scores aligned with common security frameworks.

The project follows a Retrieval-Augmented Generation (RAG) architecture using embeddings and a vector database to ensure accurate, evidence-backed analysis.

What the System Does

	•	Accepts vendor security and compliance documents (PDF format)

	•	Extracts and chunks document text

	•	Generates semantic embeddings

	•	Stores and searches embeddings using a vector database

	•	Evaluates documents against predefined security controls

	•	Produces risk scores and compliance reports

	•	Displays results through a modern web interface


Supported Document Types

	•	Contracts and Master Service Agreements

	•	Service Level Agreements (SLAs)

	•	SOC 2 reports

	•	ISO 27001 documentation

	•	GDPR and privacy policies

	•	Internal security and IT policies


Supported Frameworks

	•	SOC 2

	•	ISO 27001

	•	GDPR

	•	NIST (partial)


Frontend Functionality

	•	Multi-document upload per vendor

	•	Step-based analysis progress indicator

	•	Real-time analysis status updates

	•	Risk score visualization

	•	Control-level compliance results

	•	Document metadata tracking

	•	Structured report view

Backend Functionality

	•	PDF ingestion and validation

	•	Text extraction and chunking

	•	Embedding generation

	•	Vector storage and retrieval

	•	Control evaluation using LLMs

	•	Risk score calculation

	•	Structured JSON report generation

Environment Configuration

UPLOAD_DIR=/tmp/vendorguard/uploads

QDRANT_URL=http://localhost:6333

QDRANT_API_KEY=

EMBEDDING_PROVIDER=gemini

LLM_PROVIDER=gemini

GEMINI_EMBEDDING_MODEL=gemini-embedding-001

GEMINI_LLM_MODEL=gemini-2.5-flash

EMBEDDING_DIM=768

ALLOWED_ORIGINS=http://localhost:3000

Running the Project Locally

1. Start Qdrant

docker run -d \

  -p 6333:6333 \

  -v qdrant_storage:/qdrant/storage \

  qdrant/qdrant:latest

2. Start the Backend

cd backend

pip install -r requirements.txt

uvicorn main:app --reload


Backend will run on:

http://localhost:8000

3. Start the Frontend

cd frontend

npm install

npm run dev

Frontend will run on:

http://localhost:3000

API Flow

	1.	Upload documents for a vendor

	2.	Trigger analysis request

	3.	Backend processes documents and stores embeddings

	4.	Relevant chunks are retrieved per control

	5.	LLM evaluates compliance and risk

	6.	Report is returned to the frontend


Limitations

	•	No authentication or authorization

	•	Single analysis session at a time

	•	Limited retry and rate-limit handling

	•	No persistent job queue

	•	No user or vendor management

Future Improvements

	•	Authentication and role-based access

	•	Background job processing

	•	Analysis history and dashboards

	•	Framework-specific scoring models

	•	Improved evidence traceability

	•	Model-agnostic provider switching

	•	Performance optimizations for large documents

Intended Use

VendorGuard is intended for:

	•	Vendor risk assessments

	•	Security compliance reviews

	•	Demonstrating RAG-based document analysis systems
	
	•	Academic projects and technical portfolios

