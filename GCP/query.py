import os
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'GCP/gcp-key.json'

import vertexai
from vertexai.preview.language_models import TextEmbeddingModel
from google.cloud import bigquery
from google import genai

vertexai.init(project='finsight-496405', location='us-central1')
embed_model = TextEmbeddingModel.from_pretrained('text-embedding-004')
bq_client = bigquery.Client(project='finsight-496405')
client = genai.Client(api_key='YOUR_API_KEY_HERE')

def ask_finsight_gcp(question):
    
    # step 1 — embed question
    question_embedding = embed_model.get_embeddings([question])[0].values
    embedding_str = ','.join(map(str, question_embedding))
    
    # step 2 — BigQuery Vector Search
    query = f"""
    SELECT
        base.doc_id,
        base.chunk_index,
        base.chunk_text,
        distance
    FROM
        VECTOR_SEARCH(
            (SELECT * FROM `finsight-496405.finsight_db.document_chunks`),
            'embedding',
            (SELECT [{embedding_str}] as embedding),
            top_k => 5,
            distance_type => 'COSINE'
        )
    ORDER BY distance ASC
    """
    
    rows = list(bq_client.query(query).result())
    
    # step 3 — build context
    context = ""
    for i, row in enumerate(rows):
        context += f"Source {i+1} (chunk {row.chunk_index}):\n"
        context += f"{row.chunk_text}\n\n"
    
    # step 4 — build prompt
    prompt = f"""You are a financial analyst assistant.
Answer the question using ONLY the context provided below.
Cite which source you used in your answer.
If the answer is not in the context say "I cannot find this in the provided documents."

Context:
{context}

Question: {question}

Answer:"""
    
    # step 5 — Gemini answer
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt
    )
    
    print(f"Question: {question}\n")
    print(f"Retrieved chunks:")
    for i, row in enumerate(rows):
        print(f"  Rank {i+1} — Distance: {row.distance:.4f} — Chunk {row.chunk_index}")
    print(f"\nAnswer:\n{response.text}")

# test
ask_finsight_gcp("What is RBI's role in monetary policy?")