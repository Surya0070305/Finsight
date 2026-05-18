import json
import time
import os
import vertexai
from vertexai.language_models import TextEmbeddingModel


# step 1 vertex AI model initialization
os.environ['GOOGLE_APPLICATION_CREDENTIALS']='gcp-key.json'

vertexai.init(
    project='finsight-496405',
    location='us-central1'
)


# step 2 enabling the embedded model

model=TextEmbeddingModel.from_pretrained('text-embedding-004')

# step 3 pulling the cleansed data

chunks=[]

with open("D:\Surya\Apache Beam\output_annual_report\\beam-temp-JSON_value_holdings-aeb80d5a2a9911f18d85a196c2c621d4\\5846f0aa-89c9-4eb2-91a5-e697dc5c1a82.JSON_value_holdings.jsonl", 'r') as f:
    for line in f:
        chunks.append(json.loads(line))


# step 4 cleaning the cleansed data by adding certain data rules

def is_clean_chunk(chunks):
    text=chunks['chunk']
    total_characters= len('text')
    digit_characters= sum(1 for d in text if d.isdigit())
    if digit_characters/total_characters>0.2:
        return False
    if len(text.split())<40:
        return False
    words=text.split()
    hypen_words=sum(1 for w in words if '-' in w and len(w)<=6)
    if hypen_words/len(words)>0.3:
        return False
    return True

clean_chunks=[c for c in chunks if is_clean_chunk(c)]
print(f' Clean chunks are ready {len(clean_chunks)} ')

# step 5 embed the chunks in the respective batches

def embed_chunks_vertexai(chunks, model, batch_size=5):
    all_embeddings=[]
    for i in range(0, len(chunks), batch_size):
        batch=chunks[i:i+batch_size]
        
        text=[c['chunk'] for c in batch]
        
        embeddings=model.get_embeddings(text)
        
        all_embeddings.extend([e.values for e in embeddings])
        print(f"Embedded {min(i+batch_size, len(chunks))}/{len(chunks)}")
        time.sleep(10)
    return all_embeddings


print('Starting Vertex AI.............')
all_embed_values=embed_chunks_vertexai(clean_chunks, model)

print(f' Embedding is done------->{len(all_embed_values)}')
