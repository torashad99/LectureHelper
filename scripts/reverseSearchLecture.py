import webvtt
import os
import sys
from typing import List, Tuple, Dict

# need to adjust this to search over multiple code chunks

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

def main():
    """
    Main function to execute the reverse search on all VTT files in a directory.
    """

    if len(sys.argv) != 3:
        print("Usage: python reverse_search.py <directory_path> <search_text>")
        sys.exit(1)

    directory = sys.argv[1]
    search_text = sys.argv[2]

    print(f"Searching for '{search_text}' in all VTT files within '{directory}'...\n")

    results = process_vtt_files(directory, search_text)

    for filename, timestamps in results.items():
        if timestamps:
            print(f"File: {filename}")
            for ts in timestamps:
                print(f"  - {ts}")
            print()
        else:
            print(f"File: {filename}")
            print("  - No matches found.\n")

if __name__ == "__main__":
    main()
