import os
import re

def find_president_contexts(text):
    """
    Finds all occurrences of the word 'prezident' or 'president' in the text,
    along with two words before and after each match (a 5-word context window).
    
    Args:
        text (str): The full text from a file.
    
    Returns:
        list[str]: List of string snippets containing matched context.
    """
    words = re.findall(r'\w+|[^\s\w]', text, flags=re.UNICODE)
    contexts = []
    for i, word in enumerate(words):
        clean_word = re.sub(r'[^\w]', '', word.lower())  # Normalize word for comparison
        if 'prezident' in clean_word or 'president' in clean_word:
            start = max(0, i - 2)
            end = min(len(words), i + 3)
            context = words[start:end]
            contexts.append(' '.join(context))
    return contexts

def process_folder(folder_path):
    """
    Processes all .txt files in a given folder to find mentions of 'prezident'/'president'
    and saves all matched contexts into 'records_president.txt'.

    Args:
        folder_path (str): Path to folder containing .txt files.
    """
    output_path = os.path.join(folder_path, "records_president.txt")
    records = []

    for filename in sorted(os.listdir(folder_path)):
        if filename.endswith(".txt") and filename != "records_president.txt":
            file_path = os.path.join(folder_path, filename)
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
                contexts = find_president_contexts(text)
                for context in contexts:
                    records.append(f"{filename} | {context}")

    with open(output_path, "w", encoding="utf-8") as out:
        for record in records:
            out.write(record + "\n")

# Only for federace_zaznamy
process_folder("federace_zaznamy")
