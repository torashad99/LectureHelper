import json
import numpy as np
import os
from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI

# Initialize the OpenAI client
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

# Define a function to get the embedding of a text using a specified model
def get_embedding(text, model="text-embedding-3-small"):
    # Replace newline characters with spaces in the text
    text = text.replace("\n", " ")

    # Use the OpenAI client to create embeddings for the text using the specified model
    # and return the first embedding from the result
    return client.embeddings.create(input=[text], model=model).data[0].embedding

# Open the 'embeddings.jsonl' file in read mode
with open('embeddings.jsonl', 'r') as f:

    # Read all lines from the file
    lines = f.readlines()

    # Initialize a dictionary to load the embeddings
    embeddings = {}

    # Loop through each line in the file
    for line in lines:

        # Parse the JSON object in the line
        line = json.loads(line)

        # Map the text chunk to its corresponding embedding in the embeddings and times in the dictionary
        embeddings[line['text']] = {
            'embedding': line['embedding'],
            'timestamp': line['timestamp']
        }

# Prompt the user to enter a query
query = input("Enter a query: ")

# Get the embedding for the query
query_embedding = get_embedding(query)

# Initialize variables to track the best matching chunk, its score and its timestamp
best_chunk = None
best_score = float("-inf")
best_timestamp = None

# Loop through each chunk and its embedding in the embeddings dictionary
for chunk, data in embeddings.items():
    embedding = data['embedding']
    timestamp = data['timestamp']

    # Compute the similarity score as the dot product of the embedding vectors
    score = np.dot(embedding, query_embedding)

    # If this score is better than the best score found so far,
    # update the best_chunk and best_score with the current chunk and score
    if score > best_score:
        best_chunk = chunk
        best_score = score
        best_timestamp = timestamp

    # Note: OpenAI embeddings are normalized to length 1, which means that:
    # Cosine similarity can be computed slightly faster using just a dot product
    # Cosine similarity and Euclidean distance will result in the identical rankings
    # https://help.openai.com/en/articles/6824809-embeddings-frequently-asked-questions

# Print the chunk that is most similar to the query
print(best_chunk)
print(best_timestamp)