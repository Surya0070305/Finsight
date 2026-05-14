import json
from datetime import datetime


def log_query(question, top_indices, similartities, chunks, answer, log_file='output_annual_report/query_logs.jsonl'):
    
    
    log_entry={
        
        'timestamp':datetime.now().isoformat(),
        'question':question,
        'retrived_chunks':[
            {
                'rank':rank+1,
                'chunk_index':chunks[idx]['chunk_index'],
                'score':float(similartities[idx]),
                'chunk':chunks[idx]['chunk'][:200]
            }
            for rank,idx in enumerate(top_indices)
        ],
        'answer':answer
    }
    
    with open(log_file,'a') as f:
        f.write(json.dumps(log_entry)+'\n')
        
    print(f"Query logged at {log_entry['timestamp']}") 
    
    
print('log_query function defined')