
import ollama
import numpy as np
from sentence_transformers import SentenceTransformer
from logger import log_query


def ask_finsight(question, embeddings, chunks, top_k=10):
    
    # step 1 — retrieve top 8 chunks
    model=SentenceTransformer('all-MiniLM-L6-v2')
    question_vector = model.encode(question)
    similarities = np.dot(embeddings, question_vector) / (
        np.linalg.norm(embeddings, axis=1) * np.linalg.norm(question_vector)
    )
    top_indices = np.argsort(similarities)[::-1][:top_k]
    
    # step 2 — build context
    context = ""
    for rank, idx in enumerate(top_indices):
        context += f"Source {rank+1} (chunk {chunks[idx]['chunk_index']}):\n"
        context += f"{chunks[idx]['chunk']}\n\n"
    
    # step 3 — build prompt
    prompt = f"""You are a financial analyst assistant.
Answer the question using ONLY the context provided below.
Cite which source you used in your answer.
If the answer is not in the context say "I cannot find this in the provided documents."

Context:
{context}

Question: {question}

Answer:"""
    
    # step 4 — send to LLM
    response = ollama.chat(
        model='llama3.2',
        messages=[{'role': 'user', 'content': prompt}]
    )
    # step 5 - Getting the response
    answer = response['message']['content']
    
    # step 6 - logging the output
    log_query(question, top_indices, similarities, chunks, answer)
    
    print(f"Question: {question}\n")
    print(f"Retrieved chunks:")
    for rank, idx in enumerate(top_indices):
        print(f"  Rank {rank+1} — Score: {similarities[idx]:.4f} — Chunk {chunks[idx]['chunk_index']}")
    print(f"\nAnswer:\n{response['message']['content']}")
    
    
    

