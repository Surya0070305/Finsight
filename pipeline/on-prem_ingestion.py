import pdfplumber 
import logging
import re
import json
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.options.pipeline_options import StandardOptions

class ExtractFromPDF(beam.DoFn):
    def process(self,file_path):
        try:
            with pdfplumber.open(file_path) as pdf:
                text=' '.join(page.extract_text() or '' for page in pdf.pages)
            yield {
                'source' : file_path,
                'text': text,
                'pages': len(pdf.pages)
            }
        except Exception as reason:
            logging.error(f'Failed to parse {file_path}: {reason}')
            
            
def clean_text(text):
    # remove reversed date patterns like '71-rpA', '81-beF'
    text = re.sub(r'\d{2}-[a-zA-Z]{3}', '', text)
    # remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text


class chunkSplitter(beam.DoFn):
    def process(self, document):
        words=clean_text(document['text']).split()
        chunk_size=100
        for i in range(0,len(words),chunk_size):
            chunk=' '.join(words[i:i+chunk_size])
            yield {
                'source': document['source'],
                'pages_count': document['pages'],
                'chunk_index': i//chunk_size,
                'chunk_lenght':len(chunk.split()),
                'chunk': chunk
            }
            
            
with beam.Pipeline() as P:
    (
        P
        | 'Creating the Pcollection' >> beam.Create(['input_annual_report\AnnualReport.pdf'])
        | 'Extract Info from PDF' >> beam.ParDo(ExtractFromPDF())
        | 'Split into chunks' >> beam.ParDo(chunkSplitter())
        | 'Filter the records by length' >> beam.Filter(lambda x: len(x['chunk'].split())>50)
        | 'Convert the in fo to JSON' >> beam.Map(json.dumps)
        | 'Writing the data to output folder' >> beam.io.WriteToText('output_annual_report/new/JSON_value_holdings',file_name_suffix='.jsonl')
    )
