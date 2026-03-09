#!/usr/bin/env python3
"""
Fetch Tencent Docs (腾讯文档) private/shared sheets using browser automation.
Supports login via QR code, cookies, or stored credentials.

Requirements:
    pip install playwright
    playwright install chromium

Usage:
    # First time: Login with QR code and save session
    python fetch_private_sheet.py login --save-session

    # Read sheet using saved session
    python fetch_private_sheet.py fetch "https://docs.qq.com/sheet/xxxxx" --output data.csv

    # Or use email/phone + password (not recommended for security)
    python fetch_private_sheet.py fetch "URL" --username "138xxxx" --password "xxx"

Author: Claude Code
"""

import argparse
import asyncio
import json
import os
import re
import sys
from pathlib import Path
from typing import Optional
from urllib.parse import parse_qs, urlparse

# Session storage
SESSION_DIR = Path.home() / ".config" / "nanoclaw" / "tencent-docs"
SESSION_FILE = SESSION_DIR / "session.json"
COOKIES_FILE = SESSION_DIR / "cookies.json"


def ensure_session_dir():
    """Ensure session directory exists."""
    SESSION_DIR.mkdir(parents=True, exist_ok=True)
    os.chmod(SESSION_DIR, 0o700)


def extract_doc_info(url: str) -> tuple[str, Optional[str]]:
    """Extract document ID and optional sheet ID from URL."""
    # Pattern: https://docs.qq.com/sheet/Dxxxxx?tab=xxxxx
    match = re.search(r'/sheet/([A-Za-z0-9]+)', url)
    if not match:
        raise ValueError(f"Invalid Tencent Docs URL: {url}")
    
    doc_id = match.group(1)
    
    # Extract tab/sheet ID from query params
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    tab_id = params.get('tab', [None])[0]
    
    return doc_id, tab_id


async def login_with_qr(save_session: bool = True, headless: bool = False):
    """
    Login to Tencent Docs using QR code authentication.
    
    Args:
        save_session: Whether to save session for future use
        headless: If False, opens browser window for QR scanning
    """
    from playwright.async_api import async_playwright
    
    ensure_session_dir()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 800}
        )
        
        page = await context.new_page()
        
        # Navigate to docs.qq.com
        print("Opening Tencent Docs...")
        await page.goto("https://docs.qq.com")
        
        # Wait for login button or already logged in
        try:
            # Check if already logged in
            await page.wait_for_selector('.user-info, .nickname, [data-testid="user-avatar"]', timeout=5000)
            print("Already logged in!")
        except:
            # Need to login
            print("\n" + "="*60)
            print("Please login to Tencent Docs")
            print("="*60)
            
            # Click login button if present
            try:
                login_btn = await page.wait_for_selector('.login-btn, .btn-login, [data-testid="login-btn"]', timeout=3000)
                if login_btn:
                    await login_btn.click()
            except:
                pass
            
            # Wait for QR code or login form
            print("\nWaiting for login...")
            print("- If QR code appears, scan it with QQ/WeChat")
            print("- Or use phone/email + password login")
            print("- Waiting up to 120 seconds...\n")
            
            # Wait for successful login
            await page.wait_for_selector(
                '.user-info, .nickname, [data-testid="user-avatar"], .workspace-sidebar, .doc-list',
                timeout=120000
            )
            print("✓ Login successful!")
        
        # Save session
        if save_session:
            # Save cookies
            cookies = await context.cookies()
            with open(COOKIES_FILE, 'w') as f:
                json.dump(cookies, f, indent=2)
            os.chmod(COOKIES_FILE, 0o600)
            print(f"✓ Session saved to {COOKIES_FILE}")
            
            # Save storage state (localStorage, sessionStorage)
            storage = await context.storage_state()
            with open(SESSION_FILE, 'w') as f:
                json.dump(storage, f, indent=2)
            os.chmod(SESSION_FILE, 0o600)
            print(f"✓ Storage state saved to {SESSION_FILE}")
        
        await browser.close()
        return True


async def fetch_sheet_data(
    url: str,
    output_format: str = 'csv',
    output_file: Optional[str] = None,
    username: Optional[str] = None,
    password: Optional[str] = None,
    headless: bool = True
) -> str:
    """
    Fetch sheet data from private Tencent Docs.
    
    Args:
        url: Tencent Docs sheet URL
        output_format: Output format (csv, json, html)
        output_file: Optional output file path
        username: Optional username/phone for login
        password: Optional password for login
        headless: Run browser in headless mode
        
    Returns:
        Extracted data as string
    """
    from playwright.async_api import async_playwright
    
    ensure_session_dir()
    doc_id, tab_id = extract_doc_info(url)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)
        
        # Try to load saved session
        context_options = {}
        if SESSION_FILE.exists():
            print(f"Loading saved session from {SESSION_FILE}")
            context_options['storage_state'] = str(SESSION_FILE)
        
        context = await browser.new_context(**context_options)
        
        # Load cookies if available
        if COOKIES_FILE.exists():
            with open(COOKIES_FILE) as f:
                cookies = json.load(f)
            await context.add_cookies(cookies)
        
        page = await context.new_page()
        
        try:
            print(f"Navigating to {url}...")
            await page.goto(url, wait_until='networkidle', timeout=60000)
            
            # Check if we need to login
            login_indicators = [
                '.login-btn',
                '.btn-login', 
                '[data-testid="login-btn"]',
                '.login-form',
                '.qr-code',  # QR code for login
            ]
            
            needs_login = False
            for indicator in login_indicators:
                try:
                    await page.wait_for_selector(indicator, timeout=2000)
                    needs_login = True
                    break
                except:
                    continue
            
            if needs_login:
                if username and password:
                    print("Attempting auto-login...")
                    # Try to fill login form
                    try:
                        await page.fill('input[type="text"], input[name="phone"], input[name="email"]', username)
                        await page.fill('input[type="password"]', password)
                        await page.click('button[type="submit"], .btn-submit')
                        await page.wait_for_load_state('networkidle')
                    except Exception as e:
                        print(f"Auto-login failed: {e}")
                        needs_login = True
                else:
                    print("\n" + "="*60)
                    print("Session expired or not logged in!")
                    print("="*60)
                    print("\nOptions:")
                    print("1. Run: python fetch_private_sheet.py login --save-session")
                    print("2. Or provide --username and --password")
                    print("\nOpening browser for manual login...")
                    
                    if headless:
                        await browser.close()
                        # Re-run without headless for manual login
                        return await fetch_sheet_data(
                            url, output_format, output_file, username, password, headless=False
                        )
                    else:
                        # Wait for manual login
                        await page.wait_for_selector(
                            '.user-info, .nickname, .workspace-sidebar',
                            timeout=120000
                        )
                        print("✓ Login successful!")
                        
                        # Save the new session
                        cookies = await context.cookies()
                        with open(COOKIES_FILE, 'w') as f:
                            json.dump(cookies, f, indent=2)
                        
                        storage = await context.storage_state()
                        with open(SESSION_FILE, 'w') as f:
                            json.dump(storage, f, indent=2)
            
            # Wait for sheet to load
            print("Waiting for sheet to load...")
            
            # Different selectors for different sheet views
            sheet_selectors = [
                '.sheet-container',
                '.sheet-grid',
                '.data-grid',
                '[data-testid="sheet-container"]',
                '.online-sheet',
                '#sheet-container',
            ]
            
            sheet_loaded = False
            for selector in sheet_selectors:
                try:
                    await page.wait_for_selector(selector, timeout=5000)
                    sheet_loaded = True
                    print(f"✓ Sheet loaded (found: {selector})")
                    break
                except:
                    continue
            
            if not sheet_loaded:
                print("Warning: Could not detect sheet container, continuing anyway...")
            
            # Give extra time for data to render
            await asyncio.sleep(2)
            
            # Extract data using JavaScript
            print("Extracting sheet data...")
            
            data = await page.evaluate('''() => {
                // Try multiple methods to extract data
                
                // Method 1: Look for data in window objects
                for (let key in window) {
                    if (key.toLowerCase().includes('sheet') || key.toLowerCase().includes('data')) {
                        let val = window[key];
                        if (val && typeof val === 'object' && val.cells) {
                            return {source: key, data: val};
                        }
                    }
                }
                
                // Method 2: Extract from DOM table structure
                const tables = document.querySelectorAll('table, .sheet-table, .data-grid');
                if (tables.length > 0) {
                    const result = [];
                    tables.forEach(table => {
                        const rows = [];
                        table.querySelectorAll('tr').forEach(tr => {
                            const row = [];
                            tr.querySelectorAll('td, th').forEach(cell => {
                                row.push(cell.textContent.trim());
                            });
                            if (row.length > 0) rows.push(row);
                        });
                        if (rows.length > 0) result.push(rows);
                    });
                    if (result.length > 0) {
                        return {source: 'dom-tables', data: result[0]}; // Return first table
                    }
                }
                
                // Method 3: Extract from grid cells
                const cells = document.querySelectorAll('.cell, .grid-cell, [role="gridcell"]');
                if (cells.length > 0) {
                    // Group cells by row
                    const rows = {};
                    cells.forEach(cell => {
                        const row = cell.getAttribute('data-row') || cell.parentElement?.getAttribute('data-row');
                        const col = cell.getAttribute('data-col') || cell.getAttribute('data-column');
                        if (row !== null) {
                            if (!rows[row]) rows[row] = {};
                            rows[row][col || Object.keys(rows[row]).length] = cell.textContent.trim();
                        }
                    });
                    
                    const result = Object.keys(rows).sort().map(r => 
                        Object.keys(rows[r]).sort().map(c => rows[r][c])
                    );
                    
                    if (result.length > 0) {
                        return {source: 'grid-cells', data: result};
                    }
                }
                
                return {source: 'none', data: null};
            }''')
            
            if not data['data']:
                # Fallback: Try to export via UI
                print("Attempting to export via UI...")
                
                # Look for export/download button
                export_selectors = [
                    '.export-btn',
                    '.download-btn',
                    '[data-testid="export"]',
                    '.file-menu',
                    'button:has-text("导出")',
                    'button:has-text("下载")',
                ]
                
                for selector in export_selectors:
                    try:
                        btn = await page.wait_for_selector(selector, timeout=2000)
                        if btn:
                            await btn.click()
                            await asyncio.sleep(1)
                            
                            # Look for Excel/CSV export option
                            excel_option = await page.wait_for_selector(
                                'text="Excel", text="CSV", .export-excel, .export-csv',
                                timeout=3000
                            )
                            if excel_option:
                                await excel_option.click()
                                print("Export initiated. Please check your downloads folder.")
                                break
                    except:
                        continue
                
                return "Could not extract data automatically. Please use export feature."
            
            # Format output
            grid = data['data']
            
            if output_format == 'json':
                # Convert to array of objects using first row as headers
                if len(grid) > 0:
                    headers = grid[0]
                    rows = []
                    for row in grid[1:]:
                        row_dict = {}
                        for i, header in enumerate(headers):
                            row_dict[header or f'Column_{i}'] = row[i] if i < len(row) else None
                        rows.append(row_dict)
                    result = json.dumps(rows, ensure_ascii=False, indent=2)
                else:
                    result = json.dumps([], ensure_ascii=False)
            
            elif output_format == 'html':
                # Generate HTML table
                rows_html = ''
                for i, row in enumerate(grid):
                    cells = ''.join(f'<td>{cell or ""}</td>' for cell in row)
                    tag = 'th' if i == 0 else 'td'
                    cells = ''.join(f'<{tag}>{cell or ""}</{tag}>' for cell in row)
                    rows_html += f'<tr>{cells}</tr>\n'
                result = f'<table border="1">\n{rows_html}</table>'
            
            else:  # csv
                import csv
                import io
                output = io.StringIO()
                writer = csv.writer(output)
                for row in grid:
                    writer.writerow(row)
                result = output.getvalue()
            
            # Save to file if specified
            if output_file:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(result)
                print(f"✓ Data saved to: {output_file}")
            
            await browser.close()
            return result
            
        except Exception as e:
            await browser.close()
            raise Exception(f"Failed to fetch sheet: {e}")


def main():
    parser = argparse.ArgumentParser(
        description='Fetch Tencent Docs private sheets via browser automation'
    )
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Login command
    login_parser = subparsers.add_parser('login', help='Login and save session')
    login_parser.add_argument(
        '--save-session', '-s',
        action='store_true',
        default=True,
        help='Save session for future use'
    )
    login_parser.add_argument(
        '--headless',
        action='store_true',
        help='Run in headless mode (no browser window)'
    )
    
    # Fetch command
    fetch_parser = subparsers.add_parser('fetch', help='Fetch sheet data')
    fetch_parser.add_argument('url', help='Tencent Docs sheet URL')
    fetch_parser.add_argument(
        '--format', '-f',
        choices=['csv', 'json', 'html'],
        default='csv',
        help='Output format'
    )
    fetch_parser.add_argument(
        '--output', '-o',
        help='Output file path'
    )
    fetch_parser.add_argument(
        '--username', '-u',
        help='Username/phone for login'
    )
    fetch_parser.add_argument(
        '--password', '-p',
        help='Password for login'
    )
    fetch_parser.add_argument(
        '--headless',
        action='store_true',
        default=True,
        help='Run in headless mode'
    )
    fetch_parser.add_argument(
        '--no-headless',
        dest='headless',
        action='store_false',
        help='Show browser window'
    )
    
    args = parser.parse_args()
    
    if args.command == 'login':
        result = asyncio.run(login_with_qr(
            save_session=args.save_session,
            headless=args.headless
        ))
        sys.exit(0 if result else 1)
    
    elif args.command == 'fetch':
        try:
            result = asyncio.run(fetch_sheet_data(
                url=args.url,
                output_format=args.format,
                output_file=args.output,
                username=args.username,
                password=args.password,
                headless=args.headless
            ))
            if not args.output:
                print(result)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
