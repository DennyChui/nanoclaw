---
name: read-tencent-docs
description: Read and extract data from Tencent Docs (腾讯文档) shared spreadsheets. Use when the user wants to fetch data from a public/shared Tencent Docs link (docs.qq.com), convert online sheets to CSV/JSON, or analyze data from shared 腾讯文档表格. Triggers on "腾讯文档", "Tencent Docs", "docs.qq.com", "读取腾讯文档", "导出腾讯表格", or shared spreadsheet links.
---

# Read Tencent Docs (腾讯文档)

Read data from publicly shared Tencent Docs spreadsheets without requiring API authentication.

## Supported URLs

- Standard sheet links: `https://docs.qq.com/sheet/DV2RHaXR5cGJERkRJ?tab=BB08J2`
- Links without explicit tab: `https://docs.qq.com/sheet/DYkNJRlp0cWRWZUlH`

## Requirements

- Document must be **publicly shared** (anyone with link can view)
- Python 3.7+ with `urllib` (built-in, no pip install needed)

## Usage

### Quick Fetch

```bash
# Pretty-printed table (default)
python3 .claude/skills/read-tencent-docs/scripts/fetch_sheet.py "https://docs.qq.com/sheet/DV2RHaXR5cGJERkRJ?tab=BB08J2"

# Export to CSV
python3 .claude/skills/read-tencent-docs/scripts/fetch_sheet.py "URL" --format csv --output data.csv

# Export to JSON (first row as headers)
python3 .claude/skills/read-tencent-docs/scripts/fetch_sheet.py "URL" --format json --output data.json

# Raw API response (for debugging)
python3 .claude/skills/read-tencent-docs/scripts/fetch_sheet.py "URL" --raw
```

### Python Usage

```python
import sys
sys.path.insert(0, '.claude/skills/read-tencent-docs/scripts')
from fetch_sheet import parse_docs_url, fetch_sheet_data, extract_cells

# Parse URL
doc_id, tab_id = parse_docs_url("https://docs.qq.com/sheet/DV2RHaXR5cGJERkRJ?tab=BB08J2")

# Fetch data
data = fetch_sheet_data(doc_id, tab_id)

# Extract cells as 2D grid
grid = extract_cells(data)  # List of rows, each row is list of cell values
```

## Output Formats

| Format | Description | Best For |
|--------|-------------|----------|
| `table` | Pretty-printed aligned text | Quick viewing, analysis |
| `csv` | Comma-separated values | Data export, Excel import |
| `json` | Array of objects | API consumption, programming |

## Common Tasks

### Analyze Sheet Data

```python
# Fetch and analyze
python3 .claude/skills/read-tencent-docs/scripts/fetch_sheet.py "URL" --format json --output /tmp/data.json

# Then process in Python
import json
with open('/tmp/data.json') as f:
    rows = json.load(f)
    
# Calculate statistics, filter, etc.
```

### Convert to Excel

```bash
# Export as CSV then convert
python3 .claude/skills/read-tencent-docs/scripts/fetch_sheet.py "URL" --format csv --output sheet.csv

# If LibreOffice is available
libreoffice --headless --convert-to xlsx sheet.csv
```

### Compare Two Sheets

```bash
python3 .claude/skills/read-tencent-docs/scripts/fetch_sheet.py "$URL1" --format csv > /tmp/sheet1.csv
python3 .claude/skills/read-tencent-docs/scripts/fetch_sheet.py "$URL2" --format csv > /tmp/sheet2.csv
diff /tmp/sheet1.csv /tmp/sheet2.csv
```

## Troubleshooting

### "HTTP Error 403: Forbidden"
- The document is not publicly shared
- Ask the owner to set sharing to "Anyone with link can view"

### "No data found in sheet"
- The sheet might be empty
- The tab ID might be incorrect (check the URL)
- Try `--raw` to see the raw API response

### Parse Errors
- Some complex formatting may not parse correctly
- Use `--raw` flag to inspect the raw response structure

## Limitations

- Only works with **publicly shared** documents (no login/auth support)
- Does not support password-protected shares
- Complex formatting (merged cells, formulas) may be simplified
- Large sheets (>10MB) may timeout

## Technical Details

This skill uses the undocumented but publicly accessible `dop-api/opendoc` endpoint that powers the Tencent Docs web interface. It extracts:

1. Document ID and Tab ID from the share URL
2. Cell data from the `clientVars.collab_client_vars.initialAttributedText` structure
3. Reconstructs the 2D grid from flattened cell indices

The API returns a deeply nested JSON structure; the `extract_cells()` function handles the complex parsing.
