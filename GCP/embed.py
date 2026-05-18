import os
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'GCP/gcp-key.json'

import json
import time
import vertexai
from vertexai.preview.language_models import TextEmbeddingModel
from google.cloud import bigquery
from google.api_core.exceptions import ResourceExhausted

vertexai.init(project='finsight-496405', location='us-central1')
embed_model = TextEmbeddingModel.from_pretrained('text-embedding-004')
bq_client = bigquery.Client(project='finsight-496405')

def is_clean_chunk(input_chunk):
    actual_info = input_chunk['chunk']
    total_len = len(actual_info)
    digit_len = sum(1 for d in actual_info if d.isdigit())
    if digit_len / total_len > 0.2:
        return False
    if len(actual_info.split()) < 20:
        return False
    words = actual_info.split()
    hyphen_words = sum(1 for w in words if '-' in w and len(w) <= 6)
    if hyphen_words / len(words) > 0.3:
        return False
    return True

def embed_and_upload(cleaner_data, embed_model, bq_client, batch_size=5):
    all_rows = []
    
    for i in range(0, len(cleaner_data), batch_size):
        batch = cleaner_data[i:i+batch_size]
        actual_info = [c['chunk'] for c in batch]
        
        for attempt in range(3):
            try:
                embeddings = embed_model.get_embeddings(actual_info)
                
                for chunk, embed_value in zip(batch, embeddings):
                    row = {
                        'doc_id':      f"rbi_annual_2024_{chunk['chunk_index']}",
                        'source':      chunk['source'],
                        'chunk_index': chunk['chunk_index'],
                        'chunk_text':  chunk['chunk'],
                        'embedding':   list(embed_value.values)
                    }
                    all_rows.append(row)
                
                print(f"Embedded {min(i+batch_size, len(cleaner_data))}/{len(cleaner_data)}")
                time.sleep(10)
                break
                
            except ResourceExhausted:
                print(f"Rate limit — waiting 60 seconds... (attempt {attempt+1})")
                time.sleep(60)
    
    # insert to BigQuery in batches of 200
    print(f"\nInserting {len(all_rows)} rows to BigQuery...")
    batch_size_bq = 200
    for i in range(0, len(all_rows), batch_size_bq):
        batch = all_rows[i:i+batch_size_bq]
        errors = bq_client.insert_rows_json(
            'finsight-496405.finsight_db.document_chunks',
            batch
        )
        if not errors:
            print(f"Inserted rows {i} to {min(i+batch_size_bq, len(all_rows))} ✅")
        else:
            print(f"Errors: {errors}")
    
    print(f"Done — {len(all_rows)} rows uploaded ✅")

# load and clean chunks
chunks = []
with open('output_annual_report/JSON_value_holdings-00000-of-00001.jsonl', 'r') as f:
    for line in f:
        chunks.append(json.loads(line))

cleaner_data = [c for c in chunks if is_clean_chunk(c)]
print(f"Clean chunks: {len(cleaner_data)}")

embed_and_upload(cleaner_data, embed_model, bq_client)