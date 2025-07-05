import os
import re

def find_president_contexts(text):
    """
    Searches the input text for occurrences of the word 'prezident' or 'president',
    but only keeps those where a colon (:) appears shortly after — suggesting
    the word appears in a speaker label or similar context.

    Args:
        text (str): Full plain text of a document.

    Returns:
        List[str]: A list of contextual snippets around valid 'prezident' mentions.
    """

    # Tokenize the text into words and punctuation
    words = re.findall(r'\w+|[^\s\w]', text, flags=re.UNICODE)
    contexts = []
    for i, word in enumerate(words):
        # Normalize word (strip punctuation, lowercase)
        clean_word = re.sub(r'[^\w]', '', word.lower())
        if 'prezident' in clean_word or 'president' in clean_word:
            # Only keep the match if a colon appears shortly after
            if ":" in words[i+1:i+7]:
                start = max(0, i - 2)
                end = min(len(words), i + 3)
                context = words[start:end]
                contexts.append(' '.join(context))
    return contexts

def process_folder(folder_path):
    """
    Processes all `.txt` files in a folder, looking for qualified mentions of 'prezident'
    and writes them (along with filename) to a summary file.

    Args:
        folder_path (str): Directory containing plain text meeting transcripts.
    """
    output_path = os.path.join(folder_path, "records_president.txt")
    records = []

    for filename in sorted(os.listdir(folder_path)):
        if filename.endswith(".txt") and filename != "records_president.txt":
            file_path = os.path.join(folder_path, filename)
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
                contexts = find_president_contexts(text)

                # For each context found, record its source file
                for context in contexts:
                    records.append(f"{filename} | {context}")

    # Write all findings to output file
    with open(output_path, "w", encoding="utf-8") as out:
        for record in records:
            out.write(record + "\n")

# Only for snr_zaznamy
process_folder("snr_zaznamy")
