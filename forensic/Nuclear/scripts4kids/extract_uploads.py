#!/usr/bin/env python3
"""
extract_uploads.py - Extract files (e.g. MP4 uploads) from HTTP POST requests in a PCAP file.
This script reassembles TCP flows and looks for multipart/form-data POST requests.
"""

import dpkt
import socket
import sys
import re
import os

def is_mp4(data):
    # Check for common MP4 marker in the first 32 bytes.
    return b'ftyp' in data[:32]

def parse_multipart(body, boundary):
    # boundary should be bytes; add leading '--'
    boundary = b'--' + boundary
    parts = body.split(boundary)
    extracted_files = []
    for part in parts:
        if b'Content-Disposition' in part and b'filename=' in part:
            # Find the end of the headers (double CRLF)
            header_end = part.find(b'\r\n\r\n')
            if header_end == -1:
                continue
            headers = part[:header_end].decode('utf-8', errors='replace')
            file_data = part[header_end+4:]
            # Remove trailing boundary markers (if any)
            file_data = file_data.strip(b'\r\n-')
            # Parse the filename from the headers
            m = re.search(r'filename="([^"]+)"', headers)
            if m:
                filename = m.group(1)
            else:
                filename = "upload_extract.bin"
            extracted_files.append((filename, file_data))
    return extracted_files

def extract_http_post_files(pcap_file):
    # Dictionary to store reassembled TCP streams per flow key
    flows = {}

    with open(pcap_file, 'rb') as f:
        pcap = dpkt.pcap.Reader(f)
        for ts, buf in pcap:
            try:
                eth = dpkt.ethernet.Ethernet(buf)
                if not isinstance(eth.data, dpkt.ip.IP):
                    continue
                ip = eth.data
                if not isinstance(ip.data, dpkt.tcp.TCP):
                    continue
                tcp = ip.data
                # Only consider flows with data
                if len(tcp.data) == 0:
                    continue

                # Use a tuple of (src, sport, dst, dport) as flow key.
                # Use sorted order for request flows (assume client -> server is the direction we want).
                key = (socket.inet_ntoa(ip.src), tcp.sport, socket.inet_ntoa(ip.dst), tcp.dport)
                flows.setdefault(key, b"")
                flows[key] += tcp.data
            except Exception:
                continue

    extracted = []

    # Iterate through flows and look for HTTP POST requests with multipart content.
    for key, data in flows.items():
        try:
            # dpkt may fail if data isn't complete HTTP header.
            req = dpkt.http.Request(data)
        except (dpkt.UnpackError, dpkt.NeedData):
            continue

        if req.method != 'POST':
            continue

        content_type = req.headers.get('content-type', '')
        if 'multipart/form-data' not in content_type:
            continue

        # Extract boundary string from content-type header
        m = re.search(r'boundary=(.+)', content_type)
        if not m:
            continue
        boundary = m.group(1).strip()
        if boundary.startswith('"') and boundary.endswith('"'):
            boundary = boundary[1:-1]
        boundary = boundary.encode()

        # req.body may be empty if not already reassembled; try using the remainder of data.
        # In many cases dpkt's Request already parsed req.body.
        body = req.body if req.body else data.split(b'\r\n\r\n', 1)[-1]
        parts = parse_multipart(body, boundary)
        for filename, file_data in parts:
            if is_mp4(file_data):
                # Ensure filename ends with .mp4
                if not filename.lower().endswith('.mp4'):
                    filename += '.mp4'
                # If file exists, append a numeric suffix.
                base, ext = os.path.splitext(filename)
                outname = filename
                counter = 1
                while os.path.exists(outname):
                    outname = f"{base}_{counter}{ext}"
                    counter += 1
                with open(outname, "wb") as fout:
                    fout.write(file_data)
                print(f"Extracted MP4 file: {outname} (size: {len(file_data)} bytes)")
                extracted.append(outname)
    return extracted

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python extract_uploads.py <pcap_file>")
        sys.exit(1)
    pcap_file = sys.argv[1]
    files = extract_http_post_files(pcap_file)
    if files:
        print(f"Extraction complete. {len(files)} file(s) extracted.")
    else:
        print("No uploaded MP4 files were extracted from the PCAP.")

