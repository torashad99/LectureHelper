import json
import os
from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI

client = OpenAI(api_key=os.environ["OPEN_AI_API_KEY"])

def get_embedding(text, model="text-embedding-3-small"):
    text = text.replace("\n", " ")
    return client.embeddings.create(input=[text], model=model).data[0].embedding

FOLDER_PATH = "../../../CS410Transcripts/txt"
OUTPUT_FILE = "embeddings.jsonl"

def process_file(file_path):
    with open(file_path, "r") as f:
        data = f.read().replace("\n", " ")
        chunks = [data[i:i+500] for i in range(0, len(data), 500)]
        embeddings = {}
        for chunk in chunks:
            embeddings[chunk] = get_embedding(chunk)
    return embeddings

all_embeddings = {}

print("Processing files and creating embeddings...")
for i in range(1, 5):
    file_name = f"L{i}.txt"
    file_path = os.path.join(FOLDER_PATH, file_name)
    if os.path.exists(file_path):
        print(f"Processing {file_name}...")
        all_embeddings.update(process_file(file_path))
    else:
        print(f"File {file_name} not found. Skipping...")

print("Writing embeddings to file...")
with open(OUTPUT_FILE, "w") as f:
    for chunk, embedding in all_embeddings.items():
        f.write(f'{{"text": {json.dumps(chunk)}, "embedding": {embedding}}}\n')

print(f"Embeddings written to file '{OUTPUT_FILE}'")