---
name: read-tencent-docs-private
description: Read private or login-required Tencent Docs (腾讯文档) spreadsheets using browser automation. Use when the user wants to access sheets that require login (private docs, access-controlled sheets), or when public sheet reading fails with authentication errors. Triggers on "private 腾讯文档", "需要登录的表格", "login required", "access denied", or when the public skill fails.
---

# Read Private Tencent Docs (腾讯文档)

Access private or login-required Tencent Docs sheets using browser automation with Playwright.

## Prerequisites

Install Playwright:
```bash
pip install playwright
playwright install chromium
```

## Authentication Methods

### Method 1: QR Code Login (Recommended)

First, login and save your session:

```bash
# Open browser for QR code scanning
python3 .claude/skills/read-tencent-docs-private/scripts/fetch_private_sheet.py login

# Or headless mode if you're already logged in elsewhere
python3 .claude/skills/read-tencent-docs-private/scripts/fetch_private_sheet.py login --headless
```

This will:
1. Open Tencent Docs in a browser
2. Show QR code for QQ/WeChat scan
3. Save session cookies after successful login
4. Reuse session for future requests

### Method 2: Username/Password (Not Recommended)

```bash
python3 .claude/skills/read-tencent-docs-private/scripts/fetch_private_sheet.py fetch "URL" \
  --username "138xxxxxxxx" \
  --password "your-password"
```

**Security Note**: Passwords may be logged in shell history. Clear with `history -c` after use.

## Usage

### Fetch Sheet Data

```bash
# Using saved session (after login)
python3 .claude/skills/read-tencent-docs-private/scripts/fetch_private_sheet.py fetch \
  "https://docs.qq.com/sheet/Dxxxxxxxx?tab=xxxxx" \
  --format csv \
  --output data.csv

# Export as JSON
python3 .claude/skills/read-tencent-docs-private/scripts/fetch_private_sheet.py fetch \
  "URL" \
  --format json \
  --output data.json

# Show browser window for debugging
python3 .claude/skills/read-tencent-docs-private/scripts/fetch_private_sheet.py fetch \
  "URL" \
  --no-headless
```

### Python API

```python
import asyncio
import sys
sys.path.insert(0, '.claude/skills/read-tencent-docs-private/scripts')
from fetch_private_sheet import fetch_sheet_data

# Fetch data
result = asyncio.run(fetch_sheet_data(
    url="https://docs.qq.com/sheet/Dxxxxxxxx",
    output_format='csv',
    headless=True
))
print(result)
```

## Output Formats

| Format | Description |
|--------|-------------|
| `csv` | Comma-separated values (default) |
| `json` | Array of objects with headers as keys |
| `html` | HTML table for viewing in browser |

## Session Management

Session files are stored securely:
- Location: `~/.config/nanoclaw/tencent-docs/`
- Permissions: 700 (directory), 600 (files)
- Files: `session.json`, `cookies.json`

### Clear Session

```bash
rm -rf ~/.config/nanoclaw/tencent-docs/
```

## Troubleshooting

### "Session expired"

Re-run login command:
```bash
python3 .claude/skills/read-tencent-docs-private/scripts/fetch_private_sheet.py login
```

### "Could not extract data automatically"

Some complex sheets may require manual export:
1. Open sheet in browser with `--no-headless`
2. Use File → Export → Excel/CSV
3. Check downloads folder

### QR Code Not Appearing

Try without headless mode:
```bash
python3 .claude/skills/read-tencent-docs-private/scripts/fetch_private_sheet.py login --no-headless
```

### Rate Limiting / CAPTCHA

If you see CAPTCHA:
1. Use `--no-headless` to solve it manually
2. Wait a few minutes between requests
3. Use saved session to reduce login frequency

## Security Considerations

- Session files contain authentication tokens - keep them secure
- Don't commit session files to version control
- The script sets restrictive permissions (600) on session files
- Consider using QR code login instead of password for better security

## How It Works

1. **Browser Automation**: Uses Playwright to control Chromium browser
2. **Session Persistence**: Saves cookies and localStorage after login
3. **Data Extraction**: Uses JavaScript evaluation to read sheet data from:
   - Window object data structures
   - DOM table elements
   - Grid cell components
4. **Fallback**: Attempts UI-based export if automatic extraction fails

## Limitations

- Requires Playwright and Chromium (~150MB download)
- Slower than API-based methods (browser startup time)
- Complex formatted sheets may not extract perfectly
- Tencent may change their UI and break the script
- Not suitable for high-frequency automated tasks

## Comparison: Public vs Private Skill

| Feature | Public Skill | Private Skill (This) |
|---------|-------------|---------------------|
| Works with public sheets | ✅ | ✅ |
| Works with private sheets | ❌ | ✅ |
| Setup complexity | Low | Medium |
| Speed | Fast (API call) | Slower (browser) |
| Requires login | No | Yes |
| Dependencies | None | Playwright |

## When to Use This Skill

Use this skill when:
- The document requires login to access
- You see "Access Denied" or "Please login" errors
- The sheet is shared privately with specific users
- You need to access your own private documents

Use the public skill (`read-tencent-docs`) when:
- The document is publicly shared
- Anyone with the link can view it
- You want faster, simpler access
