#!/usr/bin/env python3
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager
from bs4 import BeautifulSoup
from pathlib import Path
import time
import re
import requests

class SenatScraper:
    def __init__(self, output_dir="senat_zaznamy"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.records_file = self.output_dir / "records.txt"
        
        # Selenium only for navigation
        options = Options()
        options.headless = True
        service = Service(GeckoDriverManager().install())
        self.driver = webdriver.Firefox(service=service, options=options)

    def collect_urls(self):
        """Phase 1: Use Selenium to collect all URLs"""
        print("Collecting URLs...")
        self.driver.get("https://www.senat.cz/xqw/xervlet/pssenat/finddoc?typdok=steno")
        time.sleep(3)
        
        all_records = []
        page = 1
        
        while True:
            print(f"Page {page}")
            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            
            # Extract records from current page
            for row in soup.find_all("tr"):
                cells = row.find_all(["td", "th"])
                if len(cells) < 5:
                    continue
                
                date = None
                url = None
                
                for cell in cells:
                    # Find date
                    text = cell.get_text(strip=True)
                    date_match = re.search(r'(\d{1,2})\.(\d{1,2})\.(\d{4})', text)
                    if date_match:
                        d, m, y = date_match.groups()
                        date = f"{y}-{m.zfill(2)}-{d.zfill(2)}"
                    
                    # Find original link
                    for link in cell.find_all("a"):
                        if "originál" in link.get_text().lower() and link.get("href"):
                            url = f"https://www.senat.cz{link['href']}"
                            break
                
                if date and url:
                    all_records.append(f"{date} {url}")
            
            # Try next page
            try:
                next_btn = WebDriverWait(self.driver, 3).until(
                    EC.element_to_be_clickable((By.XPATH, "//input[@name='navigator.button.next']"))
                )
                next_btn.click()
                time.sleep(2)
                page += 1
            except:
                break
        
        # Save to records.txt
        with open(self.records_file, "w", encoding="utf-8") as f:
            for record in sorted(set(all_records)):
                f.write(f"{record}\n")
        
        self.driver.quit()
        print(f"Collected {len(set(all_records))} URLs")
        return len(set(all_records))

    def clean_czech_text(self, html_content):
        """Clean Czech text from HTML with proper encoding"""
        try:
            # Parse HTML
            soup = BeautifulSoup(html_content, "html.parser")
            
            # Remove unwanted elements
            for element in soup(["script", "style", "head", "meta", "link"]):
                element.decompose()
            
            # Remove audio/video links
            for element in soup.find_all("div", class_=["audioVystoupeni", "videoVystoupeni", "audioSchuze", "videoSchuze", "audioBodSchuze", "videoBodSchuze"]):
                element.decompose()
            
            # Get text content
            text = soup.get_text(separator='\n', strip=True)
            
            # Fix Czech encoding issues
            czech_fixes = {
                'È': 'Č', 'è': 'č',
                'Ø': 'Ř', 'ø': 'ř', 
                'Ý': 'Ý', 'ý': 'ý',
                'Ù': 'Ů', 'ù': 'ů',
                'Ì': 'Í', 'ì': 'í',
                'À': 'Á', 'à': 'á',
                'É': 'É', 'é': 'é',
                'Ò': 'Ň', 'ò': 'ň',
                'Ó': 'Ó', 'ó': 'ó',
                'Ô': 'Ô', 'ô': 'ô',
                'Õ': 'Õ', 'õ': 'õ',
                'Ö': 'Ö', 'ö': 'ö',
                'Ú': 'Ú', 'ú': 'ú',
                'Û': 'Û', 'û': 'û',
                'Ü': 'Ü', 'ü': 'ü',
                'Ä': 'Ä', 'ä': 'ä',
                'Å': 'Å', 'å': 'å',
                'Æ': 'Æ', 'æ': 'æ',
                'Ç': 'Ç', 'ç': 'ç',
                'Ð': 'Ď', 'ð': 'ď',
                'Ñ': 'Ň', 'ñ': 'ň',
                'Þ': 'Ť', 'þ': 'ť',
                'Ë': 'Ë', 'ë': 'ë',
                '¥': 'Ž', '¾': 'ž',
                '©': 'Š', '¹': 'š',
                # More common ones
                'PÈR': 'PČR',
                'bøeznu': 'března',
                'køíení': 'křížení',
                'øeè': 'řeč',
                'dùleitý': 'důležitý',
                'zvlátì': 'zvláště',
                'vìc': 'věc',
                'vìcí': 'věcí',
                'vechno': 'všechno',
                'vichni': 'všichni',
                'koneènì': 'konečně',
                'jetì': 'ještě',
                'dìkuji': 'děkuji',
                'dìlá': 'dělá',
                'dìlají': 'dělají',
                'schùze': 'schůze',
                'schùzi': 'schůzi',
                'poøád': 'pořád',
                'øád': 'řád',
                'øádu': 'řádu',
                'jakoukoli': 'jakoukoli',
                'øeènitì': 'řečniště',
                '&nbsp;': ' ',
                '&amp;': '&',
                '&lt;': '<',
                '&gt;': '>',
                '&quot;': '"'
            }
            
            # Apply fixes
            for wrong, correct in czech_fixes.items():
                text = text.replace(wrong, correct)
            
            # Clean up whitespace and empty lines
            lines = []
            for line in text.split('\n'):
                line = line.strip()
                if line and len(line) > 1:
                    lines.append(line)
            
            return '\n'.join(lines)
            
        except Exception as e:
            print(f"Error cleaning text: {e}")
            return html_content

    def download_files(self):
        """Phase 2: Use requests to download files"""
        print("Downloading files...")
        
        if not self.records_file.exists():
            print("No records.txt found")
            return 0
        
        with open(self.records_file, 'r', encoding='utf-8') as f:
            records = [line.strip().split(' ', 1) for line in f if line.strip()]
        
        successful = 0
        for i, (date, url) in enumerate(records, 1):
            print(f"Processing {i}/{len(records)}: {date}")
            
            # Create year folder
            year = date[:4]
            year_dir = self.output_dir / year
            year_dir.mkdir(exist_ok=True)
            
            file_id = url.split('/')[-1]
            filepath = year_dir / f"{date}_{file_id}.txt"
            
            if filepath.exists():
                print(f"Exists: {filepath}")
                successful += 1
                continue
            
            try:
                response = requests.get(url, timeout=20)
                content_type = response.headers.get("Content-Type", "").lower()
                
                # Check if it's a binary file
                if any(t in content_type for t in ["pdf", "msword", "vnd", "octet-stream"]):
                    # Save as binary
                    ext = ".pdf" if "pdf" in content_type else ".doc"
                    binary_path = year_dir / f"{date}_{file_id}{ext}"
                    with open(binary_path, "wb") as f:
                        f.write(response.content)
                    print(f"Downloaded binary: {binary_path}")
                else:
                    # Clean HTML content and save as text
                    cleaned_text = self.clean_czech_text(response.text)
                    
                    header = f"Stenozáznam ze schůze Senátu\n"
                    header += f"Datum: {date}\n"
                    header += f"Zdroj: {url}\n"
                    header += f"Staženo: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                    header += "=" * 60 + "\n\n"
                    
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(header + cleaned_text)
                    print(f"Saved clean text: {filepath}")
                
                successful += 1
                
            except Exception as e:
                print(f"Error downloading {url}: {e}")
                continue
            
            time.sleep(1)
        
        print(f"Downloaded {successful}/{len(records)} files")
        return successful

def main():
    scraper = SenatScraper()
    
    # Phase 1: Collect URLs with Selenium
    scraper.collect_urls()
    
    # Phase 2: Download files with requests
    downloaded = scraper.download_files()
    print(f"Complete: {downloaded} files downloaded")

if __name__ == "__main__":
    main()