import json
import ollama
import re
import numpy as np
from sentence_transformers import SentenceTransformer

chunks=[]
with open('output_annual_report\\beam-temp-JSON_value_holdings-aeb80d5a2a9911f18d85a196c2c621d4\\5846f0aa-89c9-4eb2-91a5-e697dc5c1a82.JSON_value_holdings.jsonl', 'r') as f:  # change the output file part according to the respective file location
    for line in f:
        chunks.append(json.loads(line))
        
        
def is_clean_chunk(chunk):
    text=chunk['chunk']
    total_lenght=len(text)
    digit_length=sum(1 for c in text if c.isdigit())
    if digit_length/total_lenght>0.2:
        return False
    if len(text.split())<40:
        return False
    words=text.split()
    hypen_words=sum(1 for w in words if '-' in w and len(w)<=6)
    if hypen_words/len(words) >0.3:
        return False
    return True

clean_chunks=[c for c in chunks if is_clean_chunk(c)]


model=SentenceTransformer('all-MiniLM-L6-v2')
clean_texts=[chunk['chunk'] for chunk in clean_chunks]
clean_embedding=model.encode(clean_texts,batch_size=32,show_progress_bar=True)


print(f'Total Chunks-->{len(clean_texts)}')
print(f'Embeddings Dimensions--->{clean_embedding.shape}')



np.save('output_annual_report/embeddings.npy', clean_embedding)
with open('output_annual_report/chunks_metadata.json', 'w') as f:
    json.dump(clean_chunks, f)
print("Embeddings saved")