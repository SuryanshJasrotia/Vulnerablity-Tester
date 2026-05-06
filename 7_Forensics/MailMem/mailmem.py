import argparse
import re
import csv
import os
from pathlib import Path
import sys
import subprocess
from datetime import datetime

def get_patterns():
    """Define regex patterns for Gmail artifacts."""
    return {
        'email': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
        'header': re.compile(r'\["ms","[0-9a-f]{16}",.*?\]', re.DOTALL),
        'body': re.compile(r'(?:Subject:.*?\n.*?)([\s\S]*?)(?=\n\n|\Z)', re.DOTALL),
        'access': re.compile(r'last access:.*?from IP "(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"'),
        'contact': re.compile(r'"contacts":\s*\[\s*\{.*?\}\s*\]', re.DOTALL)
    }

def extract_strings(dump_file):
    """Extract strings from memory dump using 'strings' command."""
    strings_file = dump_file + '.strings'
    try:
        subprocess.run(['strings', '-el', dump_file, '>', strings_file], shell=True, check=True)
        return strings_file
    except subprocess.CalledProcessError as e:
        print(f"[!] Error extracting strings: {e}")
        sys.exit(1)

def scan_strings(strings_file, patterns, chunk_size=8192):
    """Scan strings file for Gmail artifacts."""
    results = []
    offset = 0
    try:
        with open(strings_file, 'r', encoding='utf-8', errors='ignore') as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                for artifact_type, pattern in patterns.items():
                    for match in pattern.finditer(chunk):
                        start = match.start()
                        value = match.group().strip()
                        results.append({
                            'type': artifact_type,
                            'value': value[:500],  # Limit length for safety
                            'offset': offset + start
                        })
                offset += len(chunk)
    except Exception as e:
        print(f"[!] Error scanning {strings_file}: {e}")
    return results

def save_results(results, output_dir, input_file):
    """Save results to CSV file."""
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'mailmem_results.csv')
    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['input_file', 'type', 'value', 'offset'])
            writer.writeheader()
            for result in results:
                writer.writerow({
                    'input_file': input_file,
                    'type': result['type'],
                    'value': result['value'],
                    'offset': result['offset']
                })
        print(f"[*] Results saved to {output_file}")
    except Exception as e:
        print(f"[!] Error saving results: {e}")

def generate_summary(results, output_dir):
    """Generate a summary report."""
    summary = {'email': 0, 'header': 0, 'body': 0, 'access': 0, 'contact': 0}
    for result in results:
        summary[result['type']] += 1
    
    summary_file = os.path.join(output_dir, 'summary.txt')
    try:
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"MailMem Summary Report - {datetime.now().isoformat()}\n")
            f.write("-" * 50 + "\n")
            for artifact_type, count in summary.items():
                f.write(f"{artifact_type.capitalize()}: {count}\n")
            f.write("-" * 50 + "\n")
            f.write(f"Total artifacts found: {len(results)}\n")
        print(f"[*] Summary report saved to {summary_file}")
    except Exception as e:
        print(f"[!] Error saving summary: {e}")

def main():
    parser = argparse.ArgumentParser(description="MailMem: Extract Gmail artifacts from memory dumps.")
    parser.add_argument('-f', '--file', required=True, help="Input memory dump file.")
    parser.add_argument('-o', '--output', default='mailmem_output', help="Output directory for results (default: mailmem_output).")
    parser.add_argument('-v', '--verbose', action='store_true', help="Print verbose output of artifacts.")
    args = parser.parse_args()

    # Validate input
    input_path = Path(args.file)
    if not input_path.is_file():
        print(f"[!] Input file {args.file} does not exist.")
        sys.exit(1)

    print(f"[*] Starting analysis of {args.file}...")
    
    # Extract strings
    strings_file = extract_strings(args.file)
    
    # Scan for artifacts
    patterns = get_patterns()
    results = scan_strings(strings_file, patterns)
    
    # Clean up strings file
    try:
        os.remove(strings_file)
    except Exception:
        pass

    if not results:
        print("[!] No Gmail artifacts found.")
        sys.exit(0)

    # Print verbose output
    if args.verbose:
        for result in results:
            print(f"\nType: {result['type']}")
            print(f"Offset: 0x{result['offset']:x}")
            print(f"Value: {result['value'][:100]}...")

    # Save results and summary
    save_results(results, args.output, args.file)
    generate_summary(results, args.output)
    print(f"[*] Analysis complete. Total artifacts found: {len(results)}")

if __name__ == "__main__":
    main()