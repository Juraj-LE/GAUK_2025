import os
import requests
from bs4 import BeautifulSoup

OUTPUT_DIR = "federace_zaznamy"
os.makedirs(OUTPUT_DIR, exist_ok=True)

base_url = "https://www.psp.cz/eknih"

datasets = [
    ("1990fs", "slsn"),  # Společné schůze
    ("1990fs", "sl"),    # Sněmovna lidu
    ("1990fs", "sn"),    # Sněmovna národů
    ("1992fs", "slsn"),
    ("1992fs", "sl"),
    ("1992fs", "sn"),
]

def get_schuz_links(index_url):
    """
    Extracts links to individual meetings ("schůz") from a given index URL.

    Args:
        index_url (str): URL pointing to the index of all meetings for a chamber and year.

    Returns:
        list[str]: List of relative URLs to schůz folders.
    """
    response = requests.get(index_url)
    response.encoding = 'windows-1250'  # Czech encoding
    soup = BeautifulSoup(response.text, "html.parser")
    links = soup.select("a[href*='schuz']")  # Select all <a> tags containing "schuz" in their href
    return [link.get("href") for link in links if "schuz" in link.get("href")]

def download_obsah(fs_year, fs_type, schuz_path):
    """
    Downloads and extracts clean text from the 'obsah.htm' file for a given meeting.

    Args:
        fs_year (str): Year string (e.g., "1992fs").
        fs_type (str): Chamber shortcut ("slsn", "sl", or "sn").
        schuz_path (str): Relative path (e.g., "003schuz").
    """
    schuz_number = schuz_path.strip("/").split("/")[-1]
    url = f"{base_url}/{fs_year}/{fs_type}/stenprot/{schuz_number}/obsah.htm"
    response = requests.get(url)
    if response.status_code == 200:
        response.encoding = 'windows-1250'
        soup = BeautifulSoup(response.text, "html.parser")

        # Remove script/style and get clean text
        for tag in soup(["script", "style"]):
            tag.decompose()
        text = soup.get_text(separator="\n")

        # Clean up excess whitespace
        lines = [line.strip() for line in text.splitlines()]
        text_clean = "\n".join(line for line in lines if line)

        filename = f"{fs_year}_{fs_type}_{schuz_number}.txt"
        filepath = os.path.join(OUTPUT_DIR, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(text_clean)

        print(f"Saved clean text: {filename}")
    else:
        print(f"Failed to download: {url} (status {response.status_code})")

# Loop over all datasets and extract 'obsah' for each schůze
for fs_year, fs_type in datasets:
    index_url = f"{base_url}/{fs_year}/{fs_type}/stenprot/index.htm"
    try:
        schuz_links = get_schuz_links(index_url)
        for schuz_link in schuz_links:
            download_obsah(fs_year, fs_type, schuz_link)
    except Exception as e:
        print(f"Error processing {fs_year}/{fs_type}: {e}")
