# GAUK_2025

This repository contains code and data for analyzing presidential participation in various Czech parliamentary and government meetings from 1990-2025. The research examines mentions and attendance of Czech presidents across different legislative bodies and government sessions.

## 📋 Project Overview

The project scrapes and analyzes transcripts from:
- **Federal Assembly** (1990-1992): Both chambers and joint sessions
- **Chamber of Deputies** (Sněmovna): 2006-2021 periods  
- **Senate** (Senát): 1996-2025 records
- **Slovak National Council** (1990): 25 parliamentary sessions
- **Government Meetings** (Vláda): 1991-2025 meeting records

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Windows OS (for Word document processing)
- Microsoft Word installed (for .doc to .docx conversion)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/GAUK_2025
cd GAUK_2025
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

### Required Python Packages

```
requests
beautifulsoup4
selenium
webdriver-manager
tqdm
python-docx
PyPDF2
pdfplumber
win32com.client
chardet
matplotlib
pandas
```

## 📊 Data Collection

### Step 1: Data Collection (Scraping)
```bash
# Scrape all parliamentary data sources
python federace_scrape.py      # Federal Assembly (1990-1992)
python snemovna_scrape.py      # Chamber of Deputies (2006-2021) 
python senat_scraper.py        # Senate (1996-2025)
python snr_scrape.py           # Slovak National Council (1990)
```

### Step 2: Presidential Analysis
```bash
# Analyze presidential mentions across all sources
python federace_prezident.py   # Search Federal Assembly transcripts
python snemovna_prezident.py   # Search Chamber of Deputies PDFs
python senat_prezident.py      # Search Senate documents
python snr_prezident.py        # Search Slovak National Council records
```

After running each `*_prezident.py` script, a `records_president.txt` file is created in the respective data folders with results in tab-separated format:
```
filename | context1 | context2 | context3
date    url    contexts
```
Context extraction captures 2-3 words before and after "prezident" for each found match. Later filtering only mentions followed by colons (speaker identification) in the next few following words can be to remove majority of junk results.

### Presidential Terms Covered
- **Václav Havel**: 1993-2003
- **Václav Klaus**: 2003-2013  
- **Miloš Zeman**: 2013-2023
- **Petr Pavel**: 2023-present


### Data Sources Breakdown:
- **Federal Assembly**: Joint sessions, Chamber of People, and Chamber of Nations (HTML format)
- **Chamber of Deputies**: PDF stenographic records with multi-library text extraction
- **Senate**: Pagination with DOCX conversion and date-based filtering
- **Slovak National Council**: 25 parliamentary sessions with combined HTML parts

### Government Meetings (1991-2025)
Run the Jupyter notebook:
```bash
jupyter notebook vlada_scrape_prezident.ipynb
```
- Comprehensive scraping of government meeting records
- Two-phase approach: 2009-2025 (modern) and 1991-2008 (legacy)
- Statistical analysis and visualization

## ⚙️ Technical Notes

### File Format Handling
- **HTML**: BeautifulSoup parsing with encoding detection
- **PDF**: Multiple extraction methods (PyPDF2, pdfplumber)
- **DOC/DOCX**: COM automation for legacy format conversion
- **Encoding**: Automatic detection for Czech characters

### Error Handling
- Robust retry mechanisms for network requests
- Graceful handling of missing or corrupted files
- Comprehensive logging of processing errors

### Performance Considerations
- Respectful scraping with delays between requests
- Progress tracking with tqdm
- Efficient text processing for large document sets

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Commit your changes (`git commit -am 'Add new analysis'`)
4. Push to the branch (`git push origin feature/improvement`)
5. Create a Pull Request

## 📚 Citation

If you use this data or code in your research, please cite:

```bibtex
@misc{czech_presidential_meetings_2025,
  title={Presidential Participation in Czech Parliamentary and Government Meetings: A Comprehensive Dataset (1990-2025)},
  author={[Your Name]},
  year={2025},
  howpublished={\url{https://github.com/yourusername/GAUK%ľéľť}},
  note={Dataset and analysis scripts for presidential participation research}
}
```

## 📞 Contact

For questions about the dataset or methodology, please open an issue or contact [jurajzilt@gmail.com].

## 🔗 Data Sources

- [Senate](https://www.senat.cz/) - Senate stenographic records  
- [Government Office](https://www.odok.gov.cz/) - Government meeting records
- [Chamber of Deputies](https://www.psp.cz/) - All the other records

---

**Note**: This research was conducted for academic purposes. All data sources are publicly available government records.
