# NetExtract

## Overview
NetExtract is a command-line Network Forensic Analysis Tool (NFAT) for forensic analysts and penetration testers to extract and reconstruct application data (e.g., HTTP sessions, emails, VoIP calls) from PCAP files or live network traffic, designed for Kali Linux. It is a simplified alternative to `Xplico`, suitable for network forensics and incident response.

## Features
- Extracts data from protocols (HTTP, SMTP, POP, IMAP, SIP).
- Reconstructs HTTP sessions, emails, and VoIP call metadata.
- Supports TCP stream reassembly for fragmented data.
- Outputs extracted data to CSV files with metadata (protocol, source, destination, content).
- Generates a summary report with artifact counts and protocol statistics.
- Modular design for adding new protocol dissectors.
- Handles large PCAP files efficiently with chunked processing.
- Supports live traffic capture on specified interfaces.

## Prerequisites
- Kali Linux (or similar environment)
- Python 3.6 or higher
- `libpcap` (pre-installed on Kali)
- Python library: `scapy` (installed via setup script)
- Input PCAP file or network interface for live capture

## Installation

### Setup
1. Clone or download the repository.
2. Run the setup script to create a virtual environment and install dependencies:
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
python netextract.py -m <mode> [-f <file> | -i <interface>] [-o <output>] [-v] [-c <count>]
```

- **-m, --mode**: Input mode (`pcap` for file, `live` for interface).
- **-f, --file**: Input PCAP file (required for `pcap` mode).
- **-i, --interface**: Network interface for live capture (default: `eth0`).
- **-o, --output**: Output directory (default: `netextract_output`).
- **-v, --verbose**: Print detailed artifact information.
- **-c, --count**: Number of packets to capture in live mode (default: 100).

### Generating a PCAP File
1. Capture traffic using `tcpdump` or Wireshark:
   ```bash
   tcpdump -i eth0 -w capture.pcap
   ```
2. Analyze the PCAP:
   ```bash
   python netextract.py -m pcap -f capture.pcap -o results -v
   ```

### Examples
1. **Analyze a PCAP file**:
   ```bash
   python netextract.py -m pcap -f capture.pcap -o results
   ```
   Output:
   ```
   [*] Starting analysis in pcap mode...
   [*] Results saved to results/netextract_results.csv
   [*] Summary report saved to results/summary.txt
   [*] Analysis complete. Total artifacts found: 10
   ```

2. **Analyze live traffic with verbose output**:
   ```bash
   python netextract.py -m live -i eth0 -o results -v -c 200
   ```
   Output:
   ```
   [*] Starting analysis in live mode...
   Protocol: HTTP
   Source: 192.168.1.2:51234
   Destination: 93.184.216.34:80
   Timestamp: 1736963872.123456
   Method: GET
   Host: example.com
   Path: /index.html
   [*] Results saved to results/netextract_results.csv
   [*] Summary report saved to results/summary.txt
   [*] Analysis complete. Total artifacts found: 5
   ```

### Output Files
- **Results CSV** (`netextract_results.csv`):
  ```csv
  input_source,protocol,src_ip,dst_ip,src_port,dst_port,timestamp,method,host,path,command,content
  capture.pcap,HTTP,192.168.1.2,93.184.216.34,51234,80,1736963872.123456,GET,example.com,/index.html,,
  capture.pcap,SMTP,192.168.1.3,172.217.167.26,54321,25,1736963873.456789,MAIL FROM:,<user@example.com>,,
  ```
- **Summary report** (`summary.txt`):
  ```
  NetExtract Summary Report - 2025-05-15T15:35:00
  --------------------------------------------------
  HTTP: 6
  SMTP: 3
  SIP: 1
  --------------------------------------------------
  Total artifacts found: 10
  ```

## Limitations
- Simplified compared to `Xplico`; supports fewer protocols (HTTP, SMTP, SIP) and lacks advanced features like VoIP audio decoding or database output (MySQL/SQLite).
- Limited to TCP-based protocols; no UDP support (e.g., DNS, RTP).
- Basic stream reassembly; may miss fragmented or out-of-order packets.
- Live capture requires root privileges and depends on `libpcap`.
- No web interface; command-line only for simplicity.

## License
MIT License

## Warning
NetExtract is for ethical forensic analysis and authorized security assessments only. Unauthorized use against networks or data you do not own or have permission to analyze is illegal and unethical. Always obtain explicit permission before analyzing traffic. The author is not responsible for misuse.