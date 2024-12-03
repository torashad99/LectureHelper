import json
import os
from dotenv import load_dotenv
load_dotenv()

# Import the OpenAI module to use OpenAI's API
from openai import OpenAI

# Initialize the OpenAI client
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

def reverseSearchText(file_path: str, text_chunk: str) -> List[str]:
   """
   Searches for the text_chunk in the VTT file and returns the associated start timestamp(s).


   :param file_path: Path to the VTT file.
   :param text_chunk: The text to search for.
   :return: A list of start timestamps where the text_chunk is found.
   """
   if not file_path:
       raise ValueError("File path is None.")
   if not os.path.isfile(file_path):
       raise FileNotFoundError(f"The file '{file_path}' does not exist.")


   timestamps = []
   try:
       captions = list(webvtt.read(file_path))
       if not captions:
           return timestamps


       # Normalize the search text: lowercase and remove extra spaces
       search_text = ' '.join(text_chunk.lower().split())


       # Normalize captions' texts similarly
       normalized_captions = [' '.join(caption.text.lower().split()) for caption in captions]
       start_times = [caption.start for caption in captions]


       n = len(captions)


       # Iterate through each caption as a potential starting point
       for i in range(n):
           concatenated_text = ""
           for j in range(i, n):
               if concatenated_text:
                   concatenated_text += ' '
               concatenated_text += normalized_captions[j]


               # Check if the concatenated text starts with the search_text
               if concatenated_text.startswith(search_text):
                   timestamps.append(start_times[i])
                   break  # Found a match starting at caption i, move to the next starting point


               # If the concatenated text length exceeds the search_text length, no need to continue
               if len(concatenated_text) >= len(search_text):
                   break


       # Remove duplicate timestamps if any
       timestamps = list(dict.fromkeys(timestamps))


   except Exception as e:
       print(f"An error occurred while parsing the VTT file '{file_path}': {e}")
       return []


   return timestamps


def process_vtt_files(directory: str, search_text: str) -> Dict[str, List[str]]:
   """
   Processes all VTT files in the specified directory, searching for the given text chunk.


   :param directory: Path to the directory containing VTT files.
   :param search_text: The text to search for in each VTT file.
   :return: A dictionary mapping each VTT file to a list of timestamps where the text is found.
   """
   if not os.path.isdir(directory):
       raise NotADirectoryError(f"The directory '{directory}' does not exist.")




   results = {}




   for filename in os.listdir(directory):
       if filename.lower().endswith('.vtt'):
           file_path = os.path.join(directory, filename)
           timestamps = reverseSearchText(file_path, search_text)
           results[filename] = timestamps


   return results

# Define a function to get the embedding of a text using a specified model
def get_embedding(text, model="text-embedding-3-small"):

    # Replace newline characters with spaces in the text
    text = text.replace("\n", " ")

    # Use the OpenAI client to create embeddings for the text using the specified model
    # and return the first embedding from the result
    return client.embeddings.create(input=[text], model=model).data[0].embedding


# Open the file 'ai.txt' from the 'data/transcripts' directory in read mode
FILE_PATH = "../../../data/transcripts/ai.txt"
with open(FILE_PATH, "r") as f:

    # Read the entire content of the file into 'data'
    data = f.read()

    # Split the data into chunks of 500 characters and store them in a list called 'chunks'
    chunks = [data[i:i+500] for i in range(0, len(data), 500)]

    # Initialize a dictionary to hold the mapping of text chunks to their embeddings
    embeddings = {}

    # Loop through each chunk in the chunks list
    print("Creating embeddings...")
    for chunk in chunks:

        # Get the embedding for the current chunk and store it in the 'embeddings' dictionary
        timestamp = reverseSearchText("../../../CS410Transcripts/vtt/", chunk)
        embedding= get_embedding(chunk)

        embeddings[chunk] = {
        "embedding": embedding,
        "timestamp": timestamp
    }

    # Open a new file 'embeddings.jsonl' in write mode
    print("Writing embeddings to file...")
    with open("embeddings.jsonl", "w") as f:

        # Loop through the items in the 'embeddings' dictionary
       for chunk, data in embeddings.items():
            embedding = data["embedding"]
            timestamp = data["timestamp"]

            # Write each chunk, its embedding, and timestamp as a JSON object to the 'embeddings.jsonl' file
            f.write(f'{{"text": {json.dumps(chunk)}, "embedding": {embedding}, "timestamp": {json.dumps(timestamp)}}}\n')

    print("Embeddings written to file 'embeddings.jsonl'")