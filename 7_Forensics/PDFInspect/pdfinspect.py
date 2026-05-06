import argparse
import re
import csv
import os
from pathlib import Path
import sys
import zlib
from datetime import datetime

def read_pdf(file_path):
    """Read PDF file content."""
    try:
        with open(file_path, 'rb') as f:
            return f.read()
    except Exception as e:
        print(f"[!] Error reading {file_path}: {e}")
        sys.exit(1)

def parse_pdf(data):
    """Parse PDF structure and extract objects."""
    objects = []
    xref = None
    trailer = None
    metadata = {}
    
    # Regex patterns
    obj_pattern = re.compile(rb'(\d+)\s+0\s+obj\b(.*?)\bendobj\b', re.DOTALL)
    stream_pattern = re.compile(rb'\bstream\b(.*?)\bendstream\b', re.DOTALL)
    xref_pattern = re.compile(rb'\bxref\b(.*?)\btrailer\b', re.DOTALL)
    trailer_pattern = re.compile(rb'\btrailer\b\s*<<\s*(.*?)\s*>>', re.DOTALL)
    metadata_pattern = re.compile(rb'\b/(\w+)(?:\s*=\s*|\s+)([^/\n>]+)(?=\s*/|\s*>>)', re.DOTALL)
    
    # Extract objects
    for match in obj_pattern.finditer(data):
        obj_id = int(match.group(1))
        content = match.group(2)
        obj = {'id': obj_id, 'content': content, 'streams': [], 'suspicious': []}
        
        # Check for streams
        for stream_match in stream_pattern.finditer(content):
            stream_data = stream_match.group(1).strip()
            try:
                # Attempt to decompress if flate encoded
                if b'/Filter /FlateDecode' in content:
                    stream_data = zlib.decompress(stream_data)
                obj['streams'].append(stream_data)
            except Exception:
                obj['streams'].append(stream_data)  # Store raw if decompression fails
        
        # Check for suspicious elements
        suspicious_tags = [b'/JS', b'/JavaScript', b'/OpenAction', b'/AA', b'/Launch']
        for tag in suspicious_tags:
            if tag in content:
                obj['suspicious'].append(tag.decode())
        
        objects.append(obj)
    
    # Extract xref
    xref_match = xref_pattern.search(data)
    if xref_match:
        xref = xref_match.group(1).decode('utf-8', errors='ignore').strip()
    
    # Extract trailer
    trailer_match = trailer_pattern.search(data)
    if trailer_match:
        trailer = trailer_match.group(1).decode('utf-8', errors='ignore').strip()
    
    # Extract metadata
    for match in metadata_pattern.finditer(data):
        key, value = match.group(1).decode(), match.group(2).decode('utf-8', errors='ignore').strip()
        metadata[key] = value
    
    return objects, xref, trailer, metadata

def save_results(objects, metadata, output_dir, input_file):
    """Save parsed objects and metadata to CSV."""
    os.makedirs(output_dir, exist_ok=True)
    
    # Save objects
    objects_file = os.path.join(output_dir, 'objects.csv')
    try:
        with open(objects_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['input_file', 'object_id', 'stream_count', 'suspicious_tags', 'content_preview'])
            writer.writeheader()
            for obj in objects:
                writer.writerow({
                    'input_file': input_file,
                    'object_id': obj['id'],
                    'stream_count': len(obj['streams']),
                    'suspicious_tags': ', '.join(obj['suspicious']),
                    'content_preview': obj['content'][:100].decode('utf-8', errors='ignore').replace('\n', ' ')
                })
        print(f"[*] Object results saved to {objects_file}")
    except Exception as e:
        print(f"[!] Error saving objects: {e}")
    
    # Save metadata
    metadata_file = os.path.join(output_dir, 'metadata.csv')
    try:
        with open(metadata_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['input_file', 'key', 'value'])
            writer.writeheader()
            for key, value in metadata.items():
                writer.writerow({'input_file': input_file, 'key': key, 'value': value})
        print(f"[*] Metadata saved to {metadata_file}")
    except Exception as e:
        print(f"[!] Error saving metadata: {e}")

def dump_streams(objects, output_dir):
    """Dump raw streams to files."""
    stream_dir = os.path.join(output_dir, 'streams')
    os.makedirs(stream_dir, exist_ok=True)
    
    for obj in objects:
        for i, stream in enumerate(obj['streams']):
            stream_file = os.path.join(stream_dir, f"obj_{obj['id']}_stream_{i}.bin")
            try:
                with open(stream_file, 'wb') as f:
                    f.write(stream)
                print(f"[*] Stream dumped to {stream_file}")
            except Exception as e:
                print(f"[!] Error dumping stream for object {obj['id']}: {e}")

def generate_summary(objects, metadata, output_dir):
    """Generate a summary report."""
    suspicious_count = sum(1 for obj in objects if obj['suspicious'])
    stream_count = sum(len(obj['streams']) for obj in objects)
    
    summary_file = os.path.join(output_dir, 'summary.txt')
    try:
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"PDFInspect Summary Report - {datetime.now().isoformat()}\n")
            f.write("-" * 50 + "\n")
            f.write(f"Total Objects: {len(objects)}\n")
            f.write(f"Objects with Streams: {sum(1 for obj in objects if obj['streams'])}\n")
            f.write(f"Total Streams: {stream_count}\n")
            f.write(f"Suspicious Objects: {suspicious_count}\n")
            f.write(f"Metadata Entries: {len(metadata)}\n")
            if suspicious_count:
                f.write("\nSuspicious Tags Found:\n")
                for obj in objects:
                    if obj['suspicious']:
                        f.write(f"  Object {obj['id']}: {', '.join(obj['suspicious'])}\n")
            f.write("-" * 50 + "\n")
        print(f"[*] Summary report saved to {summary_file}")
    except Exception as e:
        print(f"[!] Error saving summary: {e}")

def main():
    parser = argparse.ArgumentParser(description="PDFInspect: Parse and analyze PDF files.")
    parser.add_argument('-f', '--file', required=True, help="Input PDF file to parse.")
    parser.add_argument('-o', '--output', default='pdfinspect_output', help="Output directory for results (default: pdfinspect_output).")
    parser.add_argument('-s', '--streams', action='store_true', help="Dump raw streams to files.")
    parser.add_argument('-v', '--verbose', action='store_true', help="Print detailed object information.")
    args = parser.parse_args()

    # Validate input
    input_path = Path(args.file)
    if not input_path.is_file():
        print(f"[!] Input file {args.file} does not exist.")
        sys.exit(1)
    if not args.file.lower().endswith('.pdf'):
        print(f"[!] Input file {args.file} is not a PDF.")
        sys.exit(1)

    print(f"[*] Starting analysis of {args.file}...")
    data = read_pdf(args.file)
    
    # Parse PDF
    objects, xref, trailer, metadata = parse_pdf(data)
    if not objects:
        print("[!] No objects found in PDF.")
        sys.exit(0)

    # Print verbose output
    if args.verbose:
        for obj in objects:
            print(f"\nObject {obj['id']}:")
            print(f"  Streams: {len(obj['streams'])}")
            print(f"  Suspicious Tags: {', '.join(obj['suspicious']) if obj['suspicious'] else 'None'}")
            print(f"  Content Preview: {obj['content'][:100].decode('utf-8', errors='ignore').replace('\n', ' ')[:50]}...")

    # Save results
    save_results(objects, metadata, args.output, args.file)
    
    # Dump streams if requested
    if args.streams:
        dump_streams(objects, args.output)
    
    # Generate summary
    generate_summary(objects, metadata, args.output)
    print(f"[*] Analysis complete. Total objects: {len(objects)}")

if __name__ == "__main__":
    main()