import json
import csv
import re
import os
import glob

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "agent_outputs")   # directory containing .output files from agent runs
RESULT_CSV = os.path.join(BASE_DIR, "audit.csv")

HEADER = [
    "Call Identifier", "Call or Text", "Call/Text Date", "Call/Text Time",
    "Call Direction", "Speaker 1", "Speaker 2",
    "Buildings Mentioned", "Zone Names Mentioned", "Device ID",
    "Equipment Type", "Issue Category", "AI Classification", "Upstream Trigger",
    "Upstream Root Cause", "Complexity", "Knowledge Domain",
    "Knowledge Assessment", "Resolution Path", "Resolution Data",
    "Emotional Delta", "Actionable Insight"
]
NUM_FIELDS = 22

def extract_pipe_rows(text):
    """Extract pipe-delimited data rows from text, skipping headers and separators."""
    rows = []
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        # Skip header rows, separator rows, markdown artifacts
        if line.startswith("Call Identifier"):
            continue
        if line.startswith("---"):
            continue
        if line.startswith("```"):
            continue
        if line.startswith("**"):
            continue
        if line.startswith("- "):
            continue
        # Must have pipes to be a data row
        if "|" not in line:
            continue
        # Split on pipe
        fields = [f.strip() for f in line.split("|")]
        # Filter out empty leading/trailing fields from pipe formatting
        if fields and fields[0] == "":
            fields = fields[1:]
        if fields and fields[-1] == "":
            fields = fields[:-1]
        # Skip if too few fields (not a data row)
        if len(fields) < 15:
            continue
        # Skip summary/non-data rows
        if any(skip in fields[0].lower() for skip in ["summary", "total", "most common", "key pattern"]):
            continue
        rows.append(fields)
    return rows

def read_output_file(filepath):
    """Read a task output file and extract the final result text."""
    lines = []
    with open(filepath) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                # Look for assistant messages with text content
                if obj.get("type") == "assistant":
                    msg = obj.get("message", {})
                    content = msg.get("content", [])
                    for block in content:
                        if isinstance(block, dict) and block.get("type") == "text":
                            lines.append(block["text"])
                        elif isinstance(block, str):
                            lines.append(block)
            except json.JSONDecodeError:
                continue
    return "\n".join(lines)

# Process only the v2 batch output files (the 10 re-analyzed batches)
NEW_BATCH_IDS = [
    "aa1d49f99e77b9371",  # v3 batch 1
    "a2cf2b6d730f930e4",  # v3 batch 2
    "abefe6bbc47a50f91",  # v3 batch 3
    "a9c71d1cd8b1d0d0d",  # v3 batch 4
    "a341811b787ee2660",  # v3 batch 5
    "abff6fc5d49b3353a",  # v3 batch 6
    "a4a5295bbcbb1207c",  # v3 batch 7
    "a2ca0c51dfce2e796",  # v3 batch 8
]
all_rows = []
output_files = [os.path.join(OUTPUT_DIR, f"{bid}.output") for bid in NEW_BATCH_IDS]

print(f"Found {len(output_files)} output files")

for fpath in output_files:
    fname = os.path.basename(fpath)
    text = read_output_file(fpath)
    rows = extract_pipe_rows(text)
    if rows:
        print(f"  {fname}: {len(rows)} rows extracted")
        all_rows.extend(rows)
    else:
        print(f"  {fname}: no pipe-delimited rows found (skipping)")

print(f"\nTotal rows: {len(all_rows)}")

# Normalize rows to NUM_FIELDS fields (pad or truncate)
normalized = []
for row in all_rows:
    if len(row) > NUM_FIELDS:
        row = row[:NUM_FIELDS]
    elif len(row) < NUM_FIELDS:
        row = row + ["N/A"] * (NUM_FIELDS - len(row))
    normalized.append(row)

# Write CSV
with open(RESULT_CSV, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(HEADER)
    writer.writerows(normalized)

print(f"\nCSV written: {RESULT_CSV}")
print(f"Total data rows: {len(normalized)}")
