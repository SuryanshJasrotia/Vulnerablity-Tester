# DataSift

## Overview
DataSift is a command-line tool for forensic analysts and penetration testers to extract structured data (e.g., emails, URLs, credit card numbers, phone numbers) from unstructured sources like disk images, memory dumps, or files, designed for Kali Linux. It uses regular expressions to identify patterns and outputs results to CSV files with metadata (offset, context), making it suitable for digital forensics and security assessments.

## Features
- Extracts emails, URLs, credit card numbers, and phone numbers.
- Supports scanning files or directories recursively.
- Outputs results to CSV files by data type with metadata (file, offset, context).
- Generates a summary report with counts of extracted items.
- Handles large files efficiently with chunked reading.
- Lightweight and optimized for Kali Linux.

## Prerequisites
- Kali Linux (or similar environment)
- Python 3.6 or higher
- No external Python libraries required (uses standard libraries)
- Input files or directories (e.g., disk images, memory dumps, text files)

## Installation

### Setup
1. Clone or download the repository.
2. Run the setup script to create a virtual environment:
   ```bash
   chmod +x set_upfile.sh
   ./set_upfile.sh
   ```
3. Activate the virtual environment:
   ```bash
   source venv/bin/activate
   ```

## Usage
Run the tool with:
```bash
python datasift.py -i <input> [-o <output>] [-c <chunk_size>]
```

- **-i, --input**: Input file or directory to scan (e.g., `dump.bin`, `/path/to/dir`).
- **-o, --output**: Output directory for results (default: `datasift_output`).
- **-c, --chunk-size**: Chunk size for reading files (default: 8192).

### Examples
1. **Scan a single file**:
   ```bash
   python datasift.py -i dump.bin -o results
   ```
   Output:
   ```
   [*] Starting data extraction...
   [*] Saved 10 email results to results/email_results.csv
   [*] Saved 5 url results to results/url_results.csv
   [*] Summary report saved to results/summary.txt
   [*] Extraction complete. Total items found: 15
   ```

2. **Scan a directory**:
   ```bash
   python datasift.py -i /path/to/dumps -o forensic_results -c 16384
   ```

### Output Files
- **CSV files** (e.g., `email_results.csv`):
  ```csv
  type,value,file,offset,context
  email,user@example.com,/path/to/dump.bin,1234,Contact: user@example.com for details
  ```
- **Summary report** (`summary.txt`):
  ```
  DataSift Summary Report - 2025-05-15T15:35:00
  --------------------------------------------------
  Email: 10
  Url: 5
  Credit_card: 0
  Phone: 2
  --------------------------------------------------
  Total items extracted: 17
  ```

## Limitations
- Simplified compared to `bulk-extractor`; lacks advanced features like compressed file handling, parallel processing, or built-in decoders (e.g., PDF, ZIP).
- Limited to predefined patterns (email, URL, credit card, phone); custom patterns require code modification.
- Basic context extraction; may miss complex data in binary files.
- Assumes UTF-8 or Latin1 decoding; may struggle with other encodings.
- No support for encrypted or obfuscated data.

## License
MIT License

## Warning
DataSift is for ethical forensic analysis and authorized security assessments only. Unauthorized use against systems or data you do not own or have permission to analyze is illegal and unethical. Always obtain explicit permission before processing data. The author is not responsible for misuse.