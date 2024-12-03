import json
import numpy as np
import os
from dotenv import load_dotenv
import re
from pathlib import Path

load_dotenv()

from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

def get_embedding(text, model="text-embedding-3-small"):
    text = text.replace("\n", " ")
    return client.embeddings.create(input=[text], model=model).data[0].embedding

# def find_timestamp_in_vtt(chunk, vtt_directory):
#     first_five_words = ' '.join(chunk.split()[:5])
#     pattern = re.compile(re.escape(first_five_words), re.IGNORECASE)
    
#     for vtt_file in Path(vtt_directory).glob('L*.vtt'):
#         lecture_index = vtt_file.stem
#         with open(vtt_file, 'r', encoding='utf-8') as f:
#             content = f.read()
#             matches = list(pattern.finditer(content))
#             if matches:
#                 # Find the nearest timestamp before the match
#                 lines = content[:matches[0].start()].split('\n')
#                 for line in reversed(lines):
#                     if '-->' in line:
#                         start_time = line.split(' --> ')[0]
#                         return lecture_index, start_time
    
#     return None, None

def sliding_window_vtt(best_chunk, vtt_directory):
    # Split the best chunk into words
    words = best_chunk.split()
    # Start from the second word for the sliding window
    start_index = 1
    window_size = 5
    
    for i in range(start_index, len(words) - window_size + 1):
        window = ' '.join(words[i:i+window_size])
        
        for vtt_file in Path(vtt_directory).glob('L*.vtt'):
            with open(vtt_file, 'r', encoding='utf-8') as f:
                content = f.read()
                pattern = re.compile(re.escape(window), re.IGNORECASE)
                match = pattern.search(content)
                
                if match:
                    # Find the timestamp
                    lines = content[:match.start()].split('\n')
                    timestamp = None
                    
                    for line in reversed(lines):
                        if '-->' in line:
                            timestamp = line.split(' --> ')[0]
                            break
                    
                    if timestamp:
                        lecture_index = vtt_file.stem
                        return lecture_index, timestamp
    
    return None, None

# Load embeddings
with open('embeddings.jsonl', 'r') as f:
    lines = f.readlines()
    embeddings = {}
    for line in lines:
        line = json.loads(line)
        embeddings[line['text']] = line['embedding']

system_prompt = "You are a friendly and supportive teaching assistant for a course on Text Information Systems. Your task is to determine whether a user's query is relevant. If the query is relevant, provide a detailed and accurate answer. If it is not, respond with This is not a relevant question. Please ask a different question." 

user_query = input("User: ")
query_embedding = get_embedding(user_query)

best_chunk = None
best_score = float("-inf")

for chunk, embedding in embeddings.items():
    score = np.dot(embedding, query_embedding)
    if score > best_score:
        best_chunk = chunk
        best_score = score

prompt = "Answer the question using the following information from the professor of Text Information Systems delimited by triple brackets:\n\n"
prompt += f"```\n{best_chunk}\n```"
prompt += "\nQuestion: " + user_query

# print(f"Prompt:\n\n{prompt}\n")
# print("\n")

chat_completion = client.chat.completions.create(
    messages=[
        {"role": "system", "content": f"{system_prompt}"},
        {"role": "user", "content": f"{prompt}"}
    ],
    model="gpt-4o",
)

response_text = chat_completion.choices[0].message.content
print(f"Assistant: {response_text}")

# Find the timestamp in the VTT files
vtt_directory = "../../../CS410Transcripts/vtt"
lecture_index, start_time = sliding_window_vtt(best_chunk, vtt_directory)

if (lecture_index and start_time) and (response_text != "This is not a relevant question. Please ask a different question."):
    lecture_number = int(lecture_index[1:])
    # print(f"\nThis came from Lecture {lecture_number}, which the professor talks about the topic around {start_time}.")
    print(f"\nThe professor talks about this in Lecture {lecture_number}, around the {start_time} mark.")
# else:
#     print("\nCould not find a matching timestamp in the VTT files.")

# # Set a similarity threshold
# similarity_threshold = 0.7  # Adjust this value as needed

# # Only search for timestamp if the similarity score is above the threshold
# if best_score > similarity_threshold:
#     vtt_directory = "../../../CS410Transcripts/vtt"
#     lecture_index, subtitle_number, start_time = sliding_window_vtt(best_chunk, vtt_directory)

#     if lecture_index and subtitle_number and start_time:
#         lecture_number = int(lecture_index[1:])
#         print(f"This came from Lecture {lecture_number}, subtitle number {subtitle_number}, which the professor talks about the topic around {start_time}.")
#     else:
#         print("Could not find a matching timestamp in the VTT files.")
# else:
#     print(f"Best Score: {best_score} ")