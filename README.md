# Edit before submission of Milestone / Final Milestone

# CS50x Workshop on AI

This workshop is designed to introduce you to the capabilities of OpenAI's APIs, including Chat Completion, Embedding, and Assistant APIs, with hands-on demonstrations and code examples.

Slides for this workshop are available [here](https://docs.google.com/presentation/d/11k93gz0mYpSwaB9bvbtofa2o11Pg7Z2_hrH3pB4APQ0/).

## Requirements

- Python 3.x
- OpenAI Python Library (installation guide below)
- OpenAI API Key
- Internet Connection

## Installation

Before we dive into the demos, please ensure your environment is set up with the necessary software and libraries:

```bash
# Install the OpenAI library
pip3 install -r requirements.txt
```

## Text Embeddings and Semantic Search

This demo showcases the use of OpenAI's text embeddings to perform semantic search, enabling the identification of the most relevant information chunk in response to a user query. This technique can significantly enhance the way educational content is queried and retrieved, making it a powerful tool for educators and students alike.

### Key Features of Demo

- **Text Embeddings**: Illustrates how to generate and utilize text embeddings using OpenAI's `embeddings.create` method.
- **Semantic Search**: Demonstrates how to compute similarity scores between embeddings to find the most relevant content.
- **Integration with Chat API**: Combines the result of semantic search with the Chat Completion API to generate contextually relevant responses.

### Usage Notes

- **Pre-computed Embeddings**: Before running this demo, ensure you have an `embeddings.jsonl` file containing pre-computed embeddings for various content chunks relevant to your subject matter.
- **Custom Model Selection**: You can experiment with different models for embeddings to suit your content and accuracy requirements.
