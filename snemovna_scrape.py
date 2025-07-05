import requests
import os
import time
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import re
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SnemovnaScraper:
    def __init__(self):
        self.base_url = "https://www.psp.cz"
        self.years = [2021, 2017, 2013, 2010, 2006]
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Create main directory
        os.makedirs("snemovna_zaznamy", exist_ok=True)
        
        # Initialize records file
        self.records_file = "snemovna_zaznamy/records.txt"
        with open(self.records_file, 'w', encoding='utf-8') as f:
            f.write("Date\tYear\tFilename\tURL\n")
    
    def get_page_content(self, url, max_retries=3):
        """
    Attempts to retrieve the HTML content of a web page using a retry mechanism.

    Args:
        url (str): The URL of the web page to fetch.
        max_retries (int): Maximum number of retry attempts upon failure.

    Returns:
        str or None: The page content as a UTF-8 string if successful, otherwise None.
    """
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, timeout=30)
                response.raise_for_status() # Raise error for HTTP errors (4xx, 5xx)
                response.encoding = 'utf-8'
                return response.text
            except requests.RequestException as e:
                logger.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error(f"Failed to get {url} after {max_retries} attempts")
                    return None
    
    def download_pdf(self, pdf_url, filepath, max_retries=3):
        """
    Downloads a PDF file from a given URL to a specified local path, using retries on failure.

    Args:
        pdf_url (str): The URL of the PDF to download.
        filepath (str): Local path where the PDF should be saved.
        max_retries (int): Maximum number of retry attempts upon failure.

    Returns:
        bool: True if the download was successful, False otherwise.
    """
        for attempt in range(max_retries):
            try:
                response = self.session.get(pdf_url, timeout=60)
                response.raise_for_status()
                
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                
                logger.info(f"Downloaded: {os.path.basename(filepath)}")
                return True
                
            except requests.RequestException as e:
                logger.warning(f"Download attempt {attempt + 1} failed for {pdf_url}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    logger.error(f"Failed to download {pdf_url} after {max_retries} attempts")
                    return False
    
    def extract_date_from_filename(self, filename):
        """Extract date from filename if possible"""
        date_patterns = [
            r'(\d{4})-(\d{1,2})-(\d{1,2})',  # YYYY-MM-DD
            r'(\d{1,2})-(\d{1,2})-(\d{4})',  # DD-MM-YYYY
            r'(\d{2})(\d{2})(\d{4})',        # DDMMYYYY
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, filename)
            if match:
                groups = match.groups()
                if len(groups[0]) == 4:  # Year first
                    year, month, day = groups
                else:  # Day first
                    day, month, year = groups
                
                try:
                    date_obj = datetime(int(year), int(month), int(day))
                    return date_obj.strftime('%Y-%m-%d')
                except ValueError:
                    continue
        
        return "Unknown"
    
    def scrape_year(self, year):
        """Scrape all PDF files for a specific year"""
        logger.info(f"Starting to scrape year {year}")
        
        # Create year directory
        year_dir = f"snemovna_zaznamy/{year}"
        os.makedirs(year_dir, exist_ok=True)
        
        # Construct URL for the year
        year_url = f"https://www.psp.cz/eknih/{year}ps/tesnopis/index.htm"
        
        # Get the main page content
        content = self.get_page_content(year_url)
        if not content:
            logger.error(f"Could not access page for year {year}")
            return
        
        # Parse the HTML
        soup = BeautifulSoup(content, 'html.parser')
        
        # Find all PDF links
        pdf_links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.endswith('.pdf'):
                full_url = urljoin(year_url, href)
                pdf_links.append((full_url, href))
        
        logger.info(f"Found {len(pdf_links)} PDF files for year {year}")
        
        # Download each PDF
        for pdf_url, relative_path in pdf_links:
            filename = os.path.basename(relative_path)
            filepath = os.path.join(year_dir, filename)
            
            # Skip if file already exists
            if os.path.exists(filepath):
                logger.info(f"File already exists, skipping: {filename}")
                continue
            
            # Download the PDF
            success = self.download_pdf(pdf_url, filepath)
            
            if success:
                # Extract date from filename
                date_str = self.extract_date_from_filename(filename)
                
                # Write to records file
                with open(self.records_file, 'a', encoding='utf-8') as f:
                    f.write(f"{date_str}\t{year}\t{filename}\t{pdf_url}\n")
            
            # Be respectful with requests
            time.sleep(1)
    
    def scrape_all_years(self):
        """Scrape all years"""
        logger.info("Starting Sněmovna scraping process")
        
        for year in self.years:
            try:
                self.scrape_year(year)
                logger.info(f"Completed scraping for year {year}")
                
                # Longer pause between years
                time.sleep(3)
                
            except Exception as e:
                logger.error(f"Error scraping year {year}: {e}")
                continue
        
        logger.info("Scraping process completed")
    
    def get_statistics(self):
        """
    Calculates and logs statistics about the downloaded PDF files.

    For each year in self.years:
    - Counts the number of .pdf files in the corresponding directory
    - Sums their total size in bytes
    - Logs the number of files and their total size (in MB) per year
    - Logs overall totals across all years
    """
        total_files = 0  # Total number of PDF files across all years
        total_size = 0  # Total size of all PDF files in bytes
        
        for year in self.years:
            year_dir = f"snemovna_zaznamy/{year}"
            if os.path.exists(year_dir):
                # Filter all .pdf files in the directory
                files = [f for f in os.listdir(year_dir) if f.endswith('.pdf')]
                year_size = sum(os.path.getsize(os.path.join(year_dir, f)) for f in files)
                
                logger.info(f"Year {year}: {len(files)} files, {year_size / (1024*1024):.1f} MB")
                total_files += len(files)
                total_size += year_size
        
        # Log overall total statistics across all years
        logger.info(f"Total: {total_files} files, {total_size / (1024*1024):.1f} MB")

def main():
    scraper = SnemovnaScraper()
    
    try:
        scraper.scrape_all_years()
        scraper.get_statistics()
        
    except KeyboardInterrupt:
        logger.info("Scraping interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()
