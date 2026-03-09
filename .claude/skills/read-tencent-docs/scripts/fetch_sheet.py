#!/usr/bin/env python3
"""
Fetch Tencent Docs (腾讯文档) shared sheet data from public share links.
Supports converting to CSV, JSON, or pretty-printed table format.

Usage:
    python fetch_sheet.py <docs_url> [--format csv|json|table] [--output FILE]

Example:
    python fetch_sheet.py "https://docs.qq.com/sheet/DV2RHaXR5cGJERkRJ?tab=BB08J2" --format csv
"""

import argparse
import csv
import json
import re
import sys
import urllib.request
from typing import Any


def parse_docs_url(url: str) -> tuple[str, str] | None:
    """
    Parse Tencent Docs URL to extract document ID and tab ID.
    
    Args:
        url: Tencent Docs share URL
        
    Returns:
        Tuple of (doc_id, tab_id) or None if invalid
    """
    # Pattern 1: https://docs.qq.com/sheet/DV2RHaXR5cGJERkRJ?tab=BB08J2
    pattern1 = r'https?://docs\.qq\.com/sheet/([A-Za-z0-9]+)\?(?:.*&)?tab=([A-Za-z0-9]+)'
    match = re.search(pattern1, url)
    if match:
        return match.group(1), match.group(2)
    
    # Pattern 2: https://docs.qq.com/sheet/DYkNJRlp0cWRWZUlH (without tab, use default)
    pattern2 = r'https?://docs\.qq\.com/sheet/([A-Za-z0-9]+)'
    match = re.search(pattern2, url)
    if match:
        return match.group(1), "BB08J2"  # Default tab
    
    return None


def fetch_sheet_data(doc_id: str, tab_id: str) -> dict[str, Any]:
    """
    Fetch sheet data from Tencent Docs public API.
    
    Args:
        doc_id: Document ID from URL
        tab_id: Tab/Sheet ID from URL
        
    Returns:
        Raw JSON data from API
        
    Raises:
        Exception: If request fails or data cannot be parsed
    """
    api_url = f"https://docs.qq.com/dop-api/opendoc?tab={tab_id}&id={doc_id}&outformat=1&normal=1"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    
    req = urllib.request.Request(api_url, headers=headers)
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data
    except urllib.error.HTTPError as e:
        raise Exception(f"HTTP Error {e.code}: {e.reason}. The document might not be publicly accessible.")
    except json.JSONDecodeError as e:
        raise Exception(f"Failed to parse response: {e}")


def extract_cells(data: dict[str, Any]) -> list[list[Any]]:
    """
    Extract cell data from Tencent Docs API response.
    
    The data structure is nested deeply:
    clientVars -> collab_client_vars -> initialAttributedText -> text[0][2][0][c][1]
    
    Args:
        data: Raw API response
        
    Returns:
        2D list representing sheet cells
    """
    try:
        client_vars = data.get('clientVars', {})
        collab = client_vars.get('collab_client_vars', {})
        
        # Get grid dimensions
        max_col = collab.get('maxCol', 0)
        max_row = collab.get('maxRow', 0)
        
        if max_col == 0 or max_row == 0:
            return []
        
        # Extract cell data from nested structure
        initial_text = collab.get('initialAttributedText', {})
        text_array = initial_text.get('text', [])
        
        if not text_array or len(text_array) < 1:
            return []
        
        # Navigate nested structure: text[0][2][0][c][1]
        level1 = text_array[0]
        if len(level1) < 3:
            return []
        
        level2 = level1[2]
        if not level2 or len(level2) < 1:
            return []
        
        level3 = level2[0]
        cell_data = level3.get('c', {})
        
        if not cell_data or len(cell_data) < 2:
            return []
        
        # Second element contains the cells
        cells_container = cell_data[1]
        if not cells_container:
            return []
        
        # Build 2D grid
        grid: list[list[Any]] = [[None for _ in range(max_col)] for _ in range(max_row)]
        
        for cell_key, cell_value in cells_container.items():
            try:
                cell_index = int(cell_key)
                row = cell_index // max_col
                col = cell_index % max_col
                
                if row < max_row and col < max_col:
                    # Extract cell text from [2][1] or similar structure
                    if isinstance(cell_value, list) and len(cell_value) > 2:
                        text_content = cell_value[2]
                        if isinstance(text_content, list) and len(text_content) > 1:
                            grid[row][col] = text_content[1]
                        else:
                            grid[row][col] = str(text_content)
                    else:
                        grid[row][col] = str(cell_value)
            except (ValueError, IndexError, TypeError):
                continue
        
        return grid
    
    except Exception as e:
        raise Exception(f"Failed to extract cell data: {e}")


def trim_empty_rows(grid: list[list[Any]]) -> list[list[Any]]:
    """Remove trailing empty rows from the grid."""
    while grid and all(cell is None or cell == '' for cell in grid[-1]):
        grid.pop()
    return grid


def trim_empty_cols(grid: list[list[Any]]) -> list[list[Any]]:
    """Remove trailing empty columns from the grid."""
    if not grid:
        return grid
    
    max_col = len(grid[0])
    col_has_data = [False] * max_col
    
    for row in grid:
        for col_idx, cell in enumerate(row):
            if cell is not None and cell != '':
                col_has_data[col_idx] = True
    
    # Find last column with data
    last_data_col = -1
    for i, has_data in enumerate(col_has_data):
        if has_data:
            last_data_col = i
    
    if last_data_col >= 0:
        for i, row in enumerate(grid):
            grid[i] = row[:last_data_col + 1]
    
    return grid


def format_csv(grid: list[list[Any]]) -> str:
    """Format grid as CSV."""
    output = []
    for row in grid:
        # Replace None with empty string
        clean_row = ['' if cell is None else str(cell) for cell in row]
        output.append(','.join(f'"{c.replace(chr(34), chr(34)+chr(34))}"' if ',' in c or '"' in c or '\n' in c else c for c in clean_row))
    return '\n'.join(output)


def format_json(grid: list[list[Any]]) -> str:
    """Format grid as JSON array of objects (using first row as headers)."""
    if not grid:
        return '[]'
    
    headers = [str(cell or f'Column_{i}') for i, cell in enumerate(grid[0])]
    rows = []
    
    for row in grid[1:]:
        row_dict = {}
        for i, header in enumerate(headers):
            value = row[i] if i < len(row) else None
            row_dict[header] = value
        rows.append(row_dict)
    
    return json.dumps(rows, ensure_ascii=False, indent=2)


def format_table(grid: list[list[Any]]) -> str:
    """Format grid as a pretty-printed text table."""
    if not grid:
        return "Empty sheet"
    
    # Calculate column widths
    col_widths = []
    for row in grid:
        for col_idx, cell in enumerate(row):
            cell_str = str(cell) if cell is not None else ''
            if col_idx >= len(col_widths):
                col_widths.append(len(cell_str))
            else:
                col_widths[col_idx] = max(col_widths[col_idx], len(cell_str))
    
    # Build table
    lines = []
    separator = '+' + '+'.join('-' * (w + 2) for w in col_widths) + '+'
    
    for i, row in enumerate(grid):
        if i == 1:  # Header separator
            lines.append(separator.replace('-', '='))
        
        cells = []
        for col_idx, cell in enumerate(row):
            cell_str = str(cell) if cell is not None else ''
            cells.append(f' {cell_str:<{col_widths[col_idx]}} ')
        
        # Pad missing columns
        while len(cells) < len(col_widths):
            idx = len(cells)
            cells.append(f' {"":<{col_widths[idx]}} ')
        
        lines.append('|' + '|'.join(cells[:len(col_widths)]) + '|')
        
        if i == 0 or i == len(grid) - 1:
            lines.append(separator)
    
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(
        description='Fetch Tencent Docs sheet data from public share links'
    )
    parser.add_argument('url', help='Tencent Docs share URL')
    parser.add_argument(
        '--format', '-f',
        choices=['csv', 'json', 'table'],
        default='table',
        help='Output format (default: table)'
    )
    parser.add_argument(
        '--output', '-o',
        help='Output file (default: stdout)'
    )
    parser.add_argument(
        '--raw',
        action='store_true',
        help='Output raw API response (for debugging)'
    )
    
    args = parser.parse_args()
    
    # Parse URL
    parsed = parse_docs_url(args.url)
    if not parsed:
        print(f"Error: Invalid Tencent Docs URL: {args.url}", file=sys.stderr)
        print("Expected format: https://docs.qq.com/sheet/DOC_ID?tab=TAB_ID", file=sys.stderr)
        sys.exit(1)
    
    doc_id, tab_id = parsed
    
    try:
        # Fetch data
        data = fetch_sheet_data(doc_id, tab_id)
        
        if args.raw:
            output = json.dumps(data, ensure_ascii=False, indent=2)
        else:
            # Extract and format cells
            grid = extract_cells(data)
            grid = trim_empty_rows(grid)
            grid = trim_empty_cols(grid)
            
            if not grid:
                print("Warning: No data found in sheet", file=sys.stderr)
                sys.exit(0)
            
            if args.format == 'csv':
                output = format_csv(grid)
            elif args.format == 'json':
                output = format_json(grid)
            else:  # table
                output = format_table(grid)
        
        # Output
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"Output written to: {args.output}")
        else:
            print(output)
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
