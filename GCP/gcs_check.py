import os
os.environ['GOOGLE_APPLICATION_CREDENTIALS']='gcp-key.json'
from google.cloud import storage



def upload_to_gcs(local_path, bucket_name, gcs_path):
    client=storage.Client()
    bucket=client.get_bucket(bucket_name)
    blob=bucket.blob(gcs_path)
    blob.upload_from_filename(local_path)
    print(f'The file {local_path} has been uploaded to the bucket {bucket_name} ')
    

upload_to_gcs(local_path="D:\\Surya\\Apache Beam\\input_annual_report\\AnnualReport.pdf", bucket_name='finsight-data', gcs_path='raw/AnnualReport.pdf')
    
    
    