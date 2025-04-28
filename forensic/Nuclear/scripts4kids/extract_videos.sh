#!/bin/bash
# extract_videos.sh - Extract MP4 videos from a pcap file

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <pcap_file>"
    exit 1
fi

PCAP_FILE="$1"
HTTP_OUTPUT_DIR="http_objects"
VIDEO_OUTPUT_DIR="extracted_videos"

# Create output directories
mkdir -p "$HTTP_OUTPUT_DIR"
mkdir -p "$VIDEO_OUTPUT_DIR"

echo "[+] Extracting HTTP objects from $PCAP_FILE..."
# This command extracts all HTTP objects into the HTTP_OUTPUT_DIR directory.
tshark -r "$PCAP_FILE" --export-objects http,"$HTTP_OUTPUT_DIR"

echo "[+] Filtering extracted objects for MP4 videos..."
# Loop through each extracted object and check its file type.
for file in "$HTTP_OUTPUT_DIR"/*; do
    if [ -f "$file" ]; then
        # The 'file' command should identify MP4 files (look for "ISO Media" and "MP4")
        if file "$file" | grep -qi "ISO Media, MP4"; then
            echo "[*] Found video: $(basename "$file")"
            cp "$file" "$VIDEO_OUTPUT_DIR"/
        fi
    fi
done

echo "[+] Extraction complete. Videos saved in $VIDEO_OUTPUT_DIR."

