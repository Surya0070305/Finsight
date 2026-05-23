import pdfplumber
import logging
import re
import json
import apache_beam as beam
import sys
sys.path.insert(0, '/home/<gcp-account-name>/.local/lib/python3.12/site-packages')
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.options.pipeline_options import StandardOptions
from apache_beam.options.pipeline_options import GoogleCloudOptions
from apache_beam.options.pipeline_options import SetupOptions
import smart_open

class ExtractFromPDF(beam.DoFn):
    def process(self, file_path):
        try:
            with smart_open.open(file_path, 'rb') as f:
                with pdfplumber.open(f) as pdf:
                    text = ' '.join(
                        page.extract_text() or ''
                        for page in pdf.pages
                    )
            yield {
                'source': file_path,
                'text':   text,
                'pages':  len(pdf.pages)
            }
        except Exception as reason:
            logging.error(f'Failed to parse {file_path}: {reason}')

def clean_text(text):
    text = re.sub(r'\d{2}-[a-zA-Z]{3}', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

class ChunkSplitter(beam.DoFn):
    def process(self, document):
        words = clean_text(document['text']).split()
        chunk_size = 100
        for i in range(0, len(words), chunk_size):
            chunk = ' '.join(words[i:i+chunk_size])
            yield {
                'source':       document['source'],
                'pages_count':  document['pages'],
                'chunk_index':  i // chunk_size,
                'chunk_length': len(chunk.split()),
                'chunk':        chunk
            }

def run():
    options = PipelineOptions()
    gcp_options = options.view_as(GoogleCloudOptions)
    gcp_options.project = 'finsight-496405'
    gcp_options.region = 'us-central1'
    gcp_options.staging_location = 'gs://finsight-data/staging'
    gcp_options.temp_location = 'gs://finsight-data/temp'
    gcp_options.job_name = 'finsight-ingestion'
    options.view_as(StandardOptions).runner = 'DataflowRunner'
    options.view_as(SetupOptions).save_main_session = True

    with beam.Pipeline(options=options) as p:
        (
            p
            | 'LoadPDF'     >> beam.Create(['gs://finsight-data/raw/AnnualReport.pdf'])
            | 'ExtractText' >> beam.ParDo(ExtractFromPDF())
            | 'ChunkText'   >> beam.ParDo(ChunkSplitter())
            | 'FilterShort' >> beam.Filter(lambda x: len(x['chunk'].split()) > 50)
            | 'ToJSON'      >> beam.Map(json.dumps)
            | 'WriteOutput' >> beam.io.WriteToText(
                                    'gs://finsight-data/processed/chunks',
                                    file_name_suffix='.jsonl'
                               )
        )

if __name__ == '__main__':
    run()
