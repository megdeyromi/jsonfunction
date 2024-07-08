import io
import json
import base64
import os
import cohere
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import time
from fdk import response
from urllib.parse import urlparse, parse_qs


from fdk import response
# Load Documents
def load_documents(file_path):
    with open(file_path, "r") as f:
        text = f.read()
    return text

# Initialize Cohere client
cohere_api_key = "TX8xfSGQm7btpYjQBrf3qYHyo7M9gAXtGrp2kJtT"
co = cohere.Client(cohere_api_key)
api_url = "https"
# Function to embed texts
def embed_texts(texts):
    response = co.embed(
        texts=texts,
        model='large',
    )
    return response.embeddings

# Function to retrieve relevant documents
def retrieve_relevant_documents(query, document_texts, document_embeddings, top_k=5):
    query_embedding = embed_texts([query])[0]
    similarities = cosine_similarity([query_embedding], document_embeddings)[0]
    top_indices = np.argsort(similarities)[-top_k:][::-1]
    return [document_texts[i] for i in top_indices]

# Function to generate API URL
def generate_api(template, question, retrieved_text):
    for doc in retrieved_text:
        prompt = template.format(api_docs=doc, question=question)
        response = co.generate(
            prompt=prompt,
            model='command',
            max_tokens=1000,
            return_likelihoods="None",
            temperature=0,
            p=1,
            truncate="END"
        )
        generated = response
        time.sleep(10)
        generated = response.generations[0].text.strip()
        return generated  # Assuming you want the first 115 characters



def handler(ctx, data: io.BytesIO=None):
    print("Entering Python Hello World handler", flush=True)
    api_url = "https"
    body = {}  # Initialize body with an empty dictionary
    query = ""
    json_data_encoded = ""
    try:
        # Read the incoming JSON data
        body = json.loads(data.getvalue())
        
        # Extract query and json_data from the input JSON
        query = body.get("query", "")
        json_data_encoded = body.get("json_data", "")
        
        # Decode the json_data
        json_data_decoded = base64.b64decode(json_data_encoded)
        json_data = json.loads(json_data_decoded)
        
         # Process the json_data (this example assumes it contains documents)
        document_texts = json_data["items"]
        documents = [{"content": document_texts, "id": "json_1"}]
        document_texts = [doc['content'] for doc in documents]
        document_embeddings = embed_texts(document_texts)

        # Retrieve relevant documents based on query
        retrieved_docs = retrieve_relevant_documents(query, document_texts, document_embeddings)
        retrieved_text = "\n".join(retrieved_docs)
        template = '''

        You are given the below Json Data:
        {api_docs}
        Using this documentation, generate the responses by answering the user question.
        Question:{question}
        API url:
        '''
        api_url = generate_api(template, query, retrieved_text)

    except (Exception, ValueError) as ex:
        print(f"Error: {str(ex)}", flush=True)
        # Handle the error if needed

    print("Exiting Python Hello World handler", flush=True)
    
    return response.Response(
        ctx, 
        response_data=json.dumps(api_url),
        headers={"Content-Type": "application/json"}
    )
