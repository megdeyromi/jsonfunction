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
    
    body = {}  # Initialize body with an empty dictionary
    query = ""
    try:
        # Read the incoming base64 encoded data
        base64_encoded_data = data.getvalue()
        
        # Decode the base64 data
        decoded_data = base64.b64decode(base64_encoded_data)
        
        # Parse the JSON data
        body = json.loads(decoded_data)
        
    except (Exception, ValueError) as ex:
        print(f"Error: {str(ex)}", flush=True)
        # Handle the error if needed

    print("Exiting Python Hello World handler", flush=True)
    
    return response.Response(
        ctx, 
        response_data=json.dumps(body),
        headers={"Content-Type": "application/json"}
    )
