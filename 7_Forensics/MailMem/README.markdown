# MailMem

## Overview
MailMem is a command-line tool for forensic analysts to extract Gmail artifacts (e.g., contacts, email headers, bodies, last access times, IP addresses) from browser process memory dumps, designed for Kali Linux. It is a simplified alternative to `pdgmail`, suitable for digital forensics and incident response.

## Features
- Extracts Gmail contacts, email headers, bodies, last access times, and IP addresses.
- Supports memory dumps from Firefox and Chrome browsers.
- Uses regex to identify Gmail-specific patterns in memory strings.
- Outputs results to CSV files with metadata (type, value, offset).
- Generates a summary report with counts of extracted artifacts.
- Handles large memory dumps efficiently with chunked reading.
- Lightweight and optimized for Kali Linux.

## Prerequisites
- Kali Linux (or similar environment)
- Python 3.6 or higher
- `strings` command (pre-installed on Kali)
- No external Python libraries required (uses standard libraries)
- Input memory dump file (e.g., from `gcore` or `pd`)

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
python mailmem.py -f <file> [-o <output>] [-v]
```

- **-f, --file**: Input memory dump file (e.g., `fire.dmp.1446`).
- **-o, --output**: Output directory for results (default: `mailmem_output`).
- **-v, --verbose**: Print detailed artifact information.

### Generating a Memory Dump
1. Open Firefox or Chrome and log into Gmail.
2. Find the browser process ID:
   ```bash
   ps -ef | grep firefox
   ```
   or
   ```bash
   ps -ef | grep chrome
   ```
3. Dump the process memory (e.g., PID 1446):
   ```bash
   gcore -o fire.dmp 1446
   ```
4. Analyze the dump:
   ```bash
   python mailmem.py -f fire.dmp.1446 -o results -v
   ```

### Examples
1. **Analyze a memory dump**:
   ```bash
   python mailmem.py -f fire.dmp.1446 -o results
   ```
   Output:
   ```
   [*] Starting analysis of fire.dmp.1446...
   [*] Results saved to results/mailmem_results.csv
   [*] Summary report saved to results/summary.txt
   [*] Analysis complete. Total artifacts found: 15
   ```

2. **Analyze with verbose output**:
   ```bash
   python mailmem.py -f fire.dmp.1446 -o results -v
   ```
   Output:
   ```
   [*] Starting analysis of fire.dmp.1446...
   Type: email
   Offset: 0x1a2b3c
   Value: user@example.com...
   Type: access
   Offset: 0x1b4c5d
   Value: last access: "5:51 am" from IP "192.168.1.1"...
   [*] Results saved to results/mailmem_results.csv
   [*] Summary report saved to results/summary.txt
   [*] Analysis complete. Total artifacts found: 15
   ```

### Output Files
- **Results CSV** (`mailmem_results.csv`):
  ```csv
  input_file,type,value,offset
  fire.dmp.1446,email,user@example.com,1717052
  fire.dmp.1446,access,last access: "5:51 am" from IP "192.168.1.1",1812589
  ```
- **Summary report** (`summary.txt`):
  ```
  MailMem Summary Report - 2025-05-15T15:35:00
  --------------------------------------------------
  Email: 5
  Header: 3
  Body: 2
  Access: 1
  Contact: 4
  --------------------------------------------------
  Total artifacts found: 15
  ```

## Limitations
- Simplified compared to `pdgmail`; lacks advanced parsing for complex Gmail data structures or non-standard memory formats.
- Limited to predefined regex patterns; may miss obfuscated or fragmented artifacts.
- Assumes UTF-8 encoded strings; may struggle with other encodings.
- Requires manual memory dump generation using tools like `gcore` or `pd`.
- Best results with Firefox; Chrome support may vary due to memory structure differences.

## License
MIT License

## Warning
MailMem is for ethical forensic analysis and authorized security assessments only. Unauthorized use against systems or data you do not own or have permission to analyze is illegal and unethical. Always obtain explicit permission before analyzing memory dumps. The author is not responsible for misuse.