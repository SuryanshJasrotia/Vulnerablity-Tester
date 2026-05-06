import argparse
import csv
import os
from pathlib import Path
import sys
from datetime import datetime
from scapy.all import rdpcap, sniff, TCP, IP, Raw
from scapy.layers.http import HTTPRequest, HTTPResponse
from scapy.layers.inet import TCP
import re

class ProtocolDissector:
    """Base class for protocol dissectors."""
    def dissect(self, packet):
        return None

class HTTPDissector(ProtocolDissector):
    """Dissector for HTTP protocol."""
    def dissect(self, packet):
        if packet.haslayer(HTTPRequest):
            http = packet[HTTPRequest]
            return {
                'protocol': 'HTTP',
                'method': http.Method.decode() if http.Method else 'N/A',
                'host': http.Host.decode() if http.Host else 'N/A',
                'path': http.Path.decode() if http.Path else 'N/A',
                'src_ip': packet[IP].src,
                'dst_ip': packet[IP].dst,
                'src_port': packet[TCP].sport,
                'dst_port': packet[TCP].dport,
                'timestamp': packet.time
            }
        return None

class SMTPDissector(ProtocolDissector):
    """Dissector for SMTP protocol."""
    def dissect(self, packet):
        if packet.haslayer(Raw):
            payload = packet[Raw].load.decode('utf-8', errors='ignore')
            if re.search(r'^(MAIL FROM:|RCPT TO:|DATA)', payload, re.MULTILINE):
                return {
                    'protocol': 'SMTP',
                    'command': payload.split('\n')[0].strip(),
                    'content': payload[:500],  # Limit for safety
                    'src_ip': packet[IP].src,
                    'dst_ip': packet[IP].dst,
                    'src_port': packet[TCP].sport,
                    'dst_port': packet[TCP].dport,
                    'timestamp': packet.time
                }
        return None

class SIPDissector(ProtocolDissector):
    """Dissector for SIP protocol."""
    def dissect(self, packet):
        if packet.haslayer(Raw):
            payload = packet[Raw].load.decode('utf-8', errors='ignore')
            if re.search(r'^(INVITE|REGISTER|BYE)', payload, re.MULTILINE):
                return {
                    'protocol': 'SIP',
                    'method': payload.split('\n')[0].strip(),
                    'content': payload[:500],  # Limit for safety
                    'src_ip': packet[IP].src,
                    'dst_ip': packet[IP].dst,
                    'src_port': packet[TCP].sport,
                    'dst_port': packet[TCP].dport,
                    'timestamp': packet.time
                }
        return None

def reassemble_tcp_streams(packets):
    """Reassemble TCP streams from packets."""
    streams = {}
    for pkt in packets:
        if pkt.haslayer(TCP) and pkt.haslayer(IP):
            key = (pkt[IP].src, pkt[IP].dst, pkt[TCP].sport, pkt[TCP].dport)
            if key not in streams:
                streams[key] = []
            streams[key].append(pkt)
    return streams

def process_pcap(pcap_file, dissectors):
    """Process PCAP file and extract artifacts."""
    results = []
    try:
        packets = rdpcap(pcap_file)
        streams = reassemble_tcp_streams(packets)
        for stream_key, stream_packets in streams.items():
            for pkt in stream_packets:
                for dissector in dissectors:
                    result = dissector.dissect(pkt)
                    if result:
                        results.append(result)
    except Exception as e:
        print(f"[!] Error processing PCAP {pcap_file}: {e}")
    return results

def process_live(interface, dissectors, count=100):
    """Capture and process live traffic."""
    results = []
    try:
        packets = sniff(iface=interface, count=count, filter="tcp")
        streams = reassemble_tcp_streams(packets)
        for stream_key, stream_packets in streams.items():
            for pkt in stream_packets:
                for dissector in dissectors:
                    result = dissector.dissect(pkt)
                    if result:
                        results.append(result)
    except Exception as e:
        print(f"[!] Error capturing live traffic on {interface}: {e}")
    return results

def save_results(results, output_dir, input_source):
    """Save extracted artifacts to CSV."""
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'netextract_results.csv')
    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['input_source', 'protocol', 'src_ip', 'dst_ip', 'src_port', 'dst_port', 'timestamp', 'method', 'host', 'path', 'command', 'content']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for result in results:
                row = {
                    'input_source': input_source,
                    'protocol': result.get('protocol', ''),
                    'src_ip': result.get('src_ip', ''),
                    'dst_ip': result.get('dst_ip', ''),
                    'src_port': result.get('src_port', ''),
                    'dst_port': result.get('dst_port', ''),
                    'timestamp': result.get('timestamp', ''),
                    'method': result.get('method', ''),
                    'host': result.get('host', ''),
                    'path': result.get('path', ''),
                    'command': result.get('command', ''),
                    'content': result.get('content', '')
                }
                writer.writerow(row)
        print(f"[*] Results saved to {output_file}")
    except Exception as e:
        print(f"[!] Error saving results: {e}")

def generate_summary(results, output_dir):
    """Generate a summary report."""
    summary = {'HTTP': 0, 'SMTP': 0, 'SIP': 0}
    for result in results:
        summary[result['protocol']] += 1
    
    summary_file = os.path.join(output_dir, 'summary.txt')
    try:
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"NetExtract Summary Report - {datetime.now().isoformat()}\n")
            f.write("-" * 50 + "\n")
            for protocol, count in summary.items():
                f.write(f"{protocol}: {count}\n")
            f.write("-" * 50 + "\n")
            f.write(f"Total artifacts found: {len(results)}\n")
        print(f"[*] Summary report saved to {summary_file}")
    except Exception as e:
        print(f"[!] Error saving summary: {e}")

def main():
    parser = argparse.ArgumentParser(description="NetExtract: Network Forensic Analysis Tool.")
    parser.add_argument('-m', '--mode', choices=['pcap', 'live'], required=True, help="Input mode: 'pcap' for file, 'live' for interface.")
    parser.add_argument('-f', '--file', help="Input PCAP file (required for pcap mode).")
    parser.add_argument('-i', '--interface', default='eth0', help="Network interface for live capture (default: eth0).")
    parser.add_argument('-o', '--output', default='netextract_output', help="Output directory (default: netextract_output).")
    parser.add_argument('-v', '--verbose', action='store_true', help="Print verbose output of artifacts.")
    parser.add_argument('-c', '--count', type=int, default=100, help="Number of packets to capture in live mode (default: 100).")
    args = parser.parse_args()

    # Validate input
    if args.mode == 'pcap' and not args.file:
        print("[!] PCAP file required for pcap mode.")
        sys.exit(1)
    if args.mode == 'pcap':
        input_path = Path(args.file)
        if not input_path.is_file():
            print(f"[!] Input file {args.file} does not exist.")
            sys.exit(1)
        input_source = args.file
    else:
        input_source = args.interface

    print(f"[*] Starting analysis in {args.mode} mode...")
    
    # Initialize dissectors
    dissectors = [HTTPDissector(), SMTPDissector(), SIPDissector()]
    
    # Process input
    if args.mode == 'pcap':
        results = process_pcap(args.file, dissectors)
    else:
        results = process_live(args.interface, dissectors, args.count)

    if not results:
        print("[!] No artifacts found.")
        sys.exit(0)

    # Print verbose output
    if args.verbose:
        for result in results:
            print(f"\nProtocol: {result['protocol']}")
            print(f"Source: {result['src_ip']}:{result['src_port']}")
            print(f"Destination: {result['dst_ip']}:{result['dst_port']}")
            print(f"Timestamp: {result['timestamp']}")
            if result['protocol'] == 'HTTP':
                print(f"Method: {result['method']}")
                print(f"Host: {result['host']}")
                print(f"Path: {result['path']}")
            else:
                print(f"Content: {result.get('content', result.get('command', ''))[:100]}...")

    # Save results and summary
    save_results(results, args.output, input_source)
    generate_summary(results, args.output)
    print(f"[*] Analysis complete. Total artifacts found: {len(results)}")

if __name__ == "__main__":
    main()