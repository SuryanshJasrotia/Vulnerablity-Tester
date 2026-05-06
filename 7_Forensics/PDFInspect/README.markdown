# PDFInspect

## Overview
PDFInspect is a command-line tool for forensic analysts and penetration testers to parse and analyze PDF files, extract objects, streams, and metadata, and detect potentially malicious content, designed for Kali Linux. It is a simplified alternative to `pdf-parser`, suitable for digital forensics and security assessments.

## Features
- Parses PDF structure (objects, xrefs, trailers) and extracts metadata (e.g., /Creator, /Producer).
- Extracts streams (decoded if flate-encoded) and embedded objects (e.g., JavaScript, fonts).
- Detects potentially malicious elements (e.g., /JS, /OpenAction, /AA).
- Outputs detailed object information in a human-readable format.
- Saves extracted data and metadata to CSV files.
- Supports raw stream dumping for manual analysis.
- Lightweight and optimized for Kali Linux.

## Prerequisites
- Kali Linux (or similar environment)
- Python 3.6 or higher
- No external Python libraries required (uses standard libraries)
- Input PDF file

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
python pdfinspect.py -f <file> [-o <output>] [-s] [-v]
```

- **-f, --file**: Input PDF file to parse (e.g., `sample.pdf`).
- **-o, --output**: Output directory for results (default: `pdfinspect_output`).
- **-s, --streams**: Dump raw streams to files.
- **-v, --verbose**: Print detailed object information.

### Examples
1. **Parse a PDF**:
   ```bash
   python pdfinspect.py -f sample.pdf -o results
   ```
   Output:
   ```
   [*] Starting analysis of sample.pdf...
   [*] Object results saved to results/objects.csv
   [*] Metadata saved to results/metadata.csv
   [*] Summary report saved to results/summary.txt
   [*] Analysis complete. Total objects: 10
   ```

2. **Parse with verbose output and stream dumping**:
   ```bash
   python pdfinspect.py -f sample.pdf -o results -s -v
   ```
   Output:
   ```
   [*] Starting analysis of sample.pdf...
   Object 1:
     Streams: 0
     Suspicious Tags: None
     Content Preview: << /Type /Catalog /Pages 2 0 R >>...
   Object 3:
     Streams: 1
     Suspicious Tags: /JS
     Content Preview: << /Length 100 /Filter /FlateDecode >> stream...
   [*] Stream dumped to results/streams/obj_3_stream_0.bin
   [*] Object results saved to results/objects.csv
   [*] Metadata saved to results/metadata.csv
   [*] Summary report saved to results/summary.txt
   [*] Analysis complete. Total objects: 10
   ```

### Output Files
- **Objects CSV** (`objects.csv`):
  ```csv
  input_file,object_id,stream_count,suspicious_tags,content_preview
  sample.pdf,1,0,,<< /Type /Catalog /Pages 2 0 R >>
  sample.pdf,3,1,/JS,<< /Length 100 /Filter /FlateDecode >> stream
  ```
- **Metadata CSV** (`metadata.csv`):
  ```csv
  input_file,key,value
  sample.pdf,Creator,Adobe Acrobat
  sample.pdf,Producer,PDFlib 9.0
  ```
- **Summary report** (`summary.txt`):
  ```
  PDFInspect Summary Report - 2025-05-15T15:35:00
  --------------------------------------------------
  Total Objects: 10
  Objects with Streams: 3
  Total Streams: 4
  Suspicious Objects: 1
  Metadata Entries: 5
  Suspicious Tags Found:
    Object 3: /JS
  --------------------------------------------------
  ```
- **Streams** (if `-s` is used):
  ```
  results/streams/obj_3_stream_0.bin
  ```

## Limitations
- Simplified compared to `pdf-parser`; lacks advanced features like full cross-reference table reconstruction or indirect object resolution.
- Limited stream decoding (only FlateDecode); no support for other filters (e.g., LZW, ASCII85).
- Basic suspicious tag detection; may miss obfuscated malicious content.
- Assumes well-formed PDFs; may struggle with corrupted or malformed files.
- No support for password-protected PDFs without external tools.

## License
MIT License

## Warning
PDFInspect is for ethical forensic analysis and authorized security assessments only. Unauthorized use against systems or data you do not own or have permission to analyze is illegal and unethical. Always obtain explicit permission before analyzing PDFs. The author is not responsible for misuse.