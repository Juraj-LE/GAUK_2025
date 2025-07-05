import re
import os
from pathlib import Path
import PyPDF2
import pdfplumber
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SnemovnaPresidentSearch:
    def __init__(self, input_dir="snemovna_zaznamy"):
        self.input_dir = Path(input_dir)
        self.output_file = Path("snemovna_zaznamy") / "snemovna_prezident.txt"
        self.record_map = self.load_record_links()
        self.results = []
        
        # Create output directory if it doesn't exist
        self.output_file.parent.mkdir(exist_ok=True)

    def load_record_links(self):
        """Load record links from records.txt file"""
        record_path = Path("snemovna_zaznamy") / "records.txt"
        mapping = {}
        
        if not record_path.exists():
            print("⚠️ records.txt not found.")
            return mapping
            
        with open(record_path, "r", encoding="utf-8") as f:
            # Skip header line
            next(f, None)
            for line in f:
                line = line.strip()
                if "\t" in line:
                    parts = line.split("\t")
                    if len(parts) >= 4:
                        date, year, filename, url = parts[:4]
                        # Use filename as key since we might not have exact dates
                        mapping[filename] = {
                            'date': date,
                            'year': year, 
                            'url': url
                        }
        return mapping

    def extract_text_from_pdf_pypdf2(self, file_path):
        """Extract text from PDF using PyPDF2"""
        try:
            text = ""
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
            return text
        except Exception as e:
            logger.warning(f"PyPDF2 failed for {file_path.name}: {e}")
            return ""

    def extract_text_from_pdf_pdfplumber(self, file_path):
        """Extract text from PDF using pdfplumber (fallback method)"""
        try:
            text = ""
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text
        except Exception as e:
            logger.warning(f"pdfplumber failed for {file_path.name}: {e}")
            return ""

    def extract_text_from_pdf(self, file_path):
        """Extract text from PDF using multiple methods"""
        # Try PyPDF2 first
        text = self.extract_text_from_pdf_pypdf2(file_path)
        
        # If PyPDF2 fails or returns empty text, try pdfplumber
        if not text.strip():
            text = self.extract_text_from_pdf_pdfplumber(file_path)
        
        return text

    def find_president_contexts(self, text):
        """Find all occurrences of 'prezident/president' with 2 words before and after"""
        words = re.findall(r'\w+|[^\s\w]', text, flags=re.UNICODE)
        contexts = []
        
        for i, word in enumerate(words):
            clean_word = re.sub(r'[^\w]', '', word.lower())

            if 'prezident' in clean_word or 'president' in clean_word:
                # if ":" in words[i+1:i+7] and 'č' in words[i+1]:
                if ":" in words[i+1:i+7]:
                    start = max(0, i - 2)
                    end = min(len(words), i + 3)
                    context = words[start:end]
                    contexts.append(' '.join(context))
                    break  # Only take the first occurrence in each text block
        
        return contexts

    def search_files(self):
        """Search for 'prezident/president' in all PDF files"""
        print("Searching for 'prezident/president' in PDF files...")
        
        total_files = 0
        processed_files = 0
        
        for year_folder in self.input_dir.glob("*"):
            if year_folder.is_dir() and year_folder.name.isdigit():
                print(f"Searching in {year_folder.name}...")
                
                year_files = list(year_folder.glob("*.pdf"))
                total_files += len(year_files)
                
                for file_path in year_files:
                    try:
                        processed_files += 1
                        if processed_files % 10 == 0:
                            print(f"Processed {processed_files}/{total_files} files...")
                        
                        filename = file_path.name
                        
                        # Get record info from mapping
                        record_info = self.record_map.get(filename, {})
                        date = record_info.get('date', 'Unknown')
                        url = record_info.get('url', 'NO_LINK')
                        
                        # Extract text from PDF
                        text = self.extract_text_from_pdf(file_path)
                        
                        if not text.strip():
                            logger.warning(f"No text extracted from {filename}")
                            continue
                        
                        # Find president contexts
                        contexts = self.find_president_contexts(text)
                        
                        if contexts:
                            logger.info(f"Found {len(contexts)} occurrences in {filename}")
                            self.results.append({
                                'date': date,
                                'year': year_folder.name,
                                'filename': filename,
                                'url': url,
                                'contexts': contexts
                            })
                    
                    except Exception as e:
                        logger.error(f"Error processing {file_path}: {e}")
                        continue

    def save_results(self):
        """Save results to snemovna_prezident.txt"""
        print(f"Saving results to {self.output_file}...")
        
        # Sort results by date (handle 'Unknown' dates)
        def sort_key(x):
            if x['date'] == 'Unknown':
                return '9999-99-99'  # Put unknown dates at the end
            return x['date']
        
        self.results.sort(key=sort_key)
        
        with open(self.output_file, 'w', encoding='utf-8') as f:
            # Write header
            f.write("Date\tYear\tFilename\tURL\tContexts\n")
            
            for result in self.results:
                contexts_str = ' | '.join(result['contexts'])
                f.write(f"{result['date']}\t{result['year']}\t{result['filename']}\t{result['url']}\t{contexts_str}\n")
        
        print(f"Saved {len(self.results)} files with prezident mentions")

    def get_statistics(self):
        """Print statistics about the search results"""
        if not self.results:
            print("No results to show statistics for.")
            return
        
        # Count by year
        year_counts = {}
        total_contexts = 0
        
        for result in self.results:
            year = result['year']
            contexts_count = len(result['contexts'])
            
            if year not in year_counts:
                year_counts[year] = {'files': 0, 'contexts': 0}
            
            year_counts[year]['files'] += 1
            year_counts[year]['contexts'] += contexts_count
            total_contexts += contexts_count
        
        print("\n--- SEARCH STATISTICS ---")
        print(f"Total files with 'prezident' mentions: {len(self.results)}")
        print(f"Total contexts found: {total_contexts}")
        print("\nBy year:")
        
        for year in sorted(year_counts.keys()):
            stats = year_counts[year]
            print(f"  {year}: {stats['files']} files, {stats['contexts']} contexts")

    def run(self):
        """Main search function"""
        print("Starting Sněmovna president search...")
        
        if not self.input_dir.exists():
            print(f"Error: Input directory {self.input_dir} does not exist!")
            print("Please run snemovna_scrape.py first to download the PDF files.")
            return
        
        self.search_files()
        
        if self.results:
            self.save_results()
            self.get_statistics()
            print(f"\n✅ Complete: Found prezident mentions in {len(self.results)} files")
            print(f"Results saved to: {self.output_file}")
        else:
            print("❌ No occurrences of 'prezident/president' found")

def main():
    try:
        import PyPDF2
        import pdfplumber
    except ImportError as e:
        print("Missing required libraries. Please install them:")
        print("pip install PyPDF2 pdfplumber")
        return
    
    searcher = SnemovnaPresidentSearch()
    
    try:
        searcher.run()
    except KeyboardInterrupt:
        print("\nSearch interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()