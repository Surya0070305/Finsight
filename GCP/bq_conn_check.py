import os
import vertexai
from vertexai.language_models import TextEmbeddingModel



os.environ['GOOGLE_APPLICATION_CREDENTIALS']='gcp-key.json'
# step 1 vertex AI model initialization
vertexai.init(
    project='finsight-496405',
    location='us-central1'
)

# step 2 enabling the embedded model

model=TextEmbeddingModel.from_pretrained('text-embedding-004')


# step 3 creating the sample chunk of data for checking

chunk= "RBI maintained inflation target of 4 percent during 2024-25"

# step 4  converting the chunk in to vecctors
embeddings=model.get_embeddings([chunk])

# step 5 checking the output

vector=embeddings[0].values
print(f'Embedding dimensions-->{len(vector)}')
print(f'First 5 vector values {vector[:5]}')
print('Vector Embedding is successful')
