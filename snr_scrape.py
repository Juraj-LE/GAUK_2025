import os
import requests
from bs4 import BeautifulSoup

OUTPUT_DIR = "snr_zaznamy"
os.makedirs(OUTPUT_DIR, exist_ok=True)

base_url = "https://www.psp.cz/eknih/1990snr/stenprot"

def extract_clean_text(html):
    """Extract and clean text from HTML content."""

    soup = BeautifulSoup(html, "html.parser")
    
    # Remove script and style tags as they do not contain visible content
    for tag in soup(["script", "style"]):
        tag.decompose()
    
    # Extract all visible text, preserving structure with line breaks
    text = soup.get_text(separator="\n")
    lines = [line.strip() for line in text.splitlines()]

    # Remove empty lines and return joined result
    return "\n".join(line for line in lines if line)

def download_schuz_text(schuz_number):
    """
    Downloads and combines all HTML transcript parts for a given 'schůze' (parliamentary session)
    from the Slovak National Council archive (1990). Each session consists of multiple numbered `.htm` files.

    Args:
        schuz_number (int): The session number to download (1–25 expected).
    """
    schuz_str = f"{schuz_number:03d}"
    schuz_folder = f"{schuz_str}schuz"
    all_text = []

    # Attempt to download files named like s001001.htm, s001002.htm, ..., up to s001999.htm
    for part in range(1, 1000):  # unlikely to exceed 999 parts
        part_str = f"{part:03d}"
        file_name = f"s{schuz_str}{part_str}.htm"
        url = f"{base_url}/{schuz_folder}/{file_name}"

        response = requests.get(url)
        if response.status_code != 200:
            break  # end of .htm files for this schuz

        response.encoding = 'windows-1250' # Ensure correct Czech/Slovak character decoding
        clean_text = extract_clean_text(response.text)
        all_text.append(clean_text)
        print(f"Downloaded: {file_name}")

    if all_text:
        output_file = os.path.join(OUTPUT_DIR, f"snr_{schuz_str}.txt")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n\n".join(all_text))
        print(f"Saved combined file: snr_{schuz_str}.txt")
    else:
        print(f"No files found for schuz {schuz_str}")

# Run for all 25 schuze
for i in range(1, 26):
    download_schuz_text(i)
