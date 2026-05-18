# FinSight — AI-Powered Financial Document Intelligence

A production-grade RAG pipeline that ingests financial documents, 
converts them into searchable embeddings, and answers analyst 
questions using grounded LLM responses.

Built on GCP-native stack: Apache Beam, Dataflow, BigQuery, Vertex AI.

---

## The Problem

Financial analysts spend hours manually searching through hundreds 
of pages of RBI circulars, annual reports, and regulatory filings 
to find specific information. FinSight automates this — ask a 
question in plain English, get a grounded answer with source citations.

---

## Architecture
PDF Documents (GCS)
↓
Pub/Sub trigger
↓
Apache Beam / Dataflow
→ extract text (pdfplumber)
→ clean text
→ chunk into 100-word segments
↓
Vertex AI text-embedding-gecko
→ convert chunks to 768D vectors
↓
BigQuery Vector Search
→ store and index vectors
↓
Query layer
→ embed user question
→ retrieve top-k similar chunks
→ send context to Vertex AI Gemini
→ return grounded answer with citations
↓
Observability
→ log every query, chunks, answer
→ track retrieval quality over time

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Ingestion | Apache Beam + Dataflow |
| PDF Extraction | pdfplumber |
| Embeddings (local) | sentence-transformers |
| Embeddings (prod) | Vertex AI text-embedding-gecko |
| Vector Store (local) | numpy + cosine similarity |
| Vector Store (prod) | BigQuery Vector Search |
| LLM (local) | ollama + llama3.2 |
| LLM (prod) | Vertex AI Gemini |
| Observability | JSONL logging → BigQuery |
| Trigger | Pub/Sub + GCS notifications |

---


## GCP Setup

### Prerequisites
- GCP account with billing enabled
- Project ID: your-project-id
- APIs enabled: Vertex AI, BigQuery, GCS, Pub/Sub, Dataflow

### Steps
1. Create GCS bucket and upload PDF:
```bash
python GCP/gcs_check.py
```

2. Create BigQuery table:
```bash
python GCP/bq_table.py
```

3. Embed chunks and upload to BigQuery:
```bash
python GCP/storing.py
```

4. Query with Gemini:
```bash
python GCP/query.py
```

### Environment
Set your credentials:
```bash
export GOOGLE_APPLICATION_CREDENTIALS='GCP/gcp-key.json'
```


├── GCP/
│   ├── bq_conn_check.py   → BigQuery connection test
│   ├── bq_table.py        → create BigQuery table + schema
│   ├── embed.py           → Vertex AI text-embedding-004
│   ├── gcs_check.py       → upload PDFs to GCS
│   ├── storing.py         → embed + store in BigQuery
│   └── query.py           → Vector Search + Gemini RAG



## Project Structure
finsight/
├── data/input/          → raw PDFs
├── pipeline/
│   └── ingestion.py     → Beam pipeline: PDF → chunks → JSONL
├── embeddings/
│   └── embed.py         → chunk → vector conversion
├── search/
│   └── retrieval.py     → RAG query layer
├── observability/
│   └── logger.py        → query logging
├── output/              → generated files (gitignored)
├── requirements.txt
└── README.md

---

## Setup

```bash
git clone https://github.com/yourusername/finsight.git
cd finsight
pip install -r requirements.txt
```

Install and start ollama:
```bash
ollama pull llama3.2
ollama serve
```

Run the ingestion pipeline:
```bash
python pipeline/ingestion.py
```

Generate embeddings:
```bash
python embeddings/embed.py
```

Ask a question:
```python
from search.retrieval import ask_finsight
import numpy as np, json

embeddings = np.load('output/embeddings.npy')
with open('output/chunks_metadata.json') as f:
    chunks = json.load(f)

ask_finsight("What were the key economic challenges in 2024-25?", 
             embeddings, chunks)
```

---

## Sample Output
Question: What were the key economic challenges in 2024-25?
Retrieved chunks:
Rank 1 — Score: 0.5471 — Chunk 7
Rank 2 — Score: 0.5323 — Chunk 98
Rank 3 — Score: 0.5151 — Chunk 123
Answer:
According to Source 3 (chunk 123), the key economic challenges
in 2024-25 included geopolitical tensions, trade fragmentation,
supply chain disruptions, and climate-induced uncertainties.
(Sources: chunk 123, chunk 56, chunk 143)

---

## Lessons Learned

**1. Chunk size matters**
Smaller focused chunks (100 words) produce sharper embeddings 
than large chunks. Large chunks dilute the vector across too 
many topics, reducing retrieval accuracy.

**2. PDF extraction has limits**
pdfplumber extracts text well but cannot read tables, charts, 
or images. Specific ratio numbers (e.g. capital adequacy ratio) 
that appear only in tables are invisible to the pipeline.
Future improvement: add pdfplumber's extract_table() method.

**3. Data cleaning must happen at ingestion**
Noisy chunks (chart labels, reversed date codes like 71-rpA) 
degrade embedding quality. Cleaning at the Dataflow stage 
prevents noise from propagating downstream.

**4. top_k matters for retrieval quality**
top_k=3 misses relevant chunks ranked 4-8. top_k=8-10 
significantly improves answer quality at minimal cost.

**5. Error handling inside DoFn is critical**
One corrupt PDF should not crash a pipeline processing 500 files. 
try/except inside the DoFn logs the error and skips the file.
