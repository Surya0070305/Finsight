import os
from google.cloud import bigquery


#os.environ['GOOGLE_CLOUD_CREDENTIALS']='gcp-key.json'
os.environ['GOOGLE_APPLICATION_CREDENTIALS']='gcp-key.json'


client=bigquery.Client(project='finsight-496405')

dataset_id='finsight-496405.finsight_db'
dataset=bigquery.Dataset(dataset_id)
dataset.location='US'
dataset=client.create_dataset(dataset, exists_ok=True)
print(f'Dataset has been created {dataset}')



table_id='finsight-496405.finsight_db.document_chunks'

schema=[
    bigquery.SchemaField('doc_id', 'STRING', mode='REQUIRED'),
    bigquery.SchemaField('source', 'STRING', mode='REQUIRED'),
    bigquery.SchemaField('chunk_index', 'INTEGER', mode='REQUIRED' ),
    bigquery.SchemaField('chunk_text', 'STRING', mode='REQUIRED'),
    bigquery.SchemaField('embedding', 'FLOAT', mode='REPEATED')
]

table=bigquery.Table(table_id, schema=schema)

table=client.create_table(table, exists_ok=True)
print(f'Table has been created {table_id}')
print(' The table has been created')
