Lecture Helper
--------------

![image](https://github.com/user-attachments/assets/98d667ce-7af1-4264-b491-7261afc62fcf)


Lecture Helper is a question-answering system designed for college lectures, providing relevant responses based on lecture video content. This project aims to enhance student engagement with course material by offering an efficient way to review and retrieve information from recorded lectures.

Key Features
------------

*   **Text Preprocessing**: Segments lecture transcripts into meaningful chunks with associated timestamps.
*   **Embedding Generation**: Creates embeddings to capture semantic relationships within the text.
*   **Semantic Search**: Employs similarity measures to match user queries with relevant lecture segments.
*   **OpenAI LLM Integration**: Utilizes OpenAI's API to generate contextually appropriate answers.
*   **Timestamp Retrieval**: Provides timestamps for relevant lecture segments, allowing quick access to specific video content.
*   **User-Friendly Interface**: Offers a clean and intuitive frontend for easy interaction.

System Components
-----------------

1.  **Transcript Processing**: Converts lecture transcripts into manageable chunks with timestamps.
2.  **Embedding Generation**: Creates embeddings for each text chunk to capture semantic meaning.
3.  **Semantic Search Algorithm**: Calculates similarity scores between user queries and pre-computed embeddings.
4.  **Answer Generation**: Integrates OpenAI's LLM API to produce coherent and relevant responses.
5.  **Timestamp Matching**: Reverse searches chunks to determine corresponding lecture timestamps.
6.  **Frontend Interface**: Presents a sleek user interface for seamless interaction.

Implementation Details
----------------------

*   **Transcript Source**: YouTube transcripts in VTT format, which include timestamps.
*   **Embedding Model**: Utilizes OpenAI's embedding model for semantic representation.
*   **Similarity Measure**: Employs cosine similarity for matching queries to lecture content.
*   **Language Model**: Integrates OpenAI's LLM API for generating contextual responses.

Evaluation
----------

The Lecture Helper demonstrates high accuracy in providing precise and relevant answers to user queries. It effectively handles out-of-scope questions by clearly indicating when content is not related to the lecture material.

Usage Notes
-----------

*   Ensure pre-computed embeddings are available in an `embeddings.jsonl` file before running the system.
*   The system is designed to work with lecture transcripts in VTT format, which can be obtained from YouTube videos.

Challenges and Solutions
------------------------

*   **Transcript Sourcing**: Overcame initial setbacks with ClassTranscribe by using YouTube transcripts in VTT format.
*   **Timestamp Integration**: Successfully incorporated timestamps from VTT files into the response system.
*   **Response Relevance**: Refined the prompt engineering to ensure the LLM stays within the context of provided lecture content.

Future Improvements
-------------------

*   Explore alternative embedding models for potentially improved semantic understanding.
*   Enhance the user interface to provide more detailed lecture navigation options.
*   Implement a feedback system for continuous improvement of answer quality.

Lecture Helper represents a significant step forward in making lecture content more accessible and easier to navigate for students, potentially revolutionizing the way learners interact with recorded educational material.experiment with different models for embeddings to suit your content and accuracy requirements.

## Requirements to run backend only

- Python 3.x
- OpenAI Python Library (installation guide below)
- OpenAI API Key
- Internet Connection

## Installation 

Run the following command

```bash
# Install the OpenAI library
pip3 install -r requirements.txt
```

Run 01_create_embdeddings.py first, and Run 04_reverse_search.py then. Before running, please put the openAI key as a PATH variable or paste it at the file (not recommended)
