# Sailboat Data Comparison Tool

A Python CLI tool for comparing sailboat specifications scraped from [sailboatdata.com](https://sailboatdata.com).

## Features

- 🔍 Scrape sailboat specifications from sailboatdata.com
- 📊 Compare multiple boats side-by-side
- 🎨 Beautiful table output with Rich library
- 🔧 Nix flake for reproducible development environment
- 📋 JSON export option

## Prerequisites

- [Nix](https://nixos.org/download.html) with flakes enabled
- Or Python 3.11+ with pip

## Installation & Setup

### Using Nix (Recommended)

1. Enable Nix flakes (if not already enabled):
```bash
# Add to ~/.config/nix/nix.conf or /etc/nix/nix.conf
experimental-features = nix-command flakes
```

2. Enter the development environment:
```bash
nix develop
```

Or use direnv for automatic environment loading:
```bash
direnv allow
```

### Using pip

```bash
pip install requests beautifulsoup4 click rich lxml
```

## Usage

Compare two or more sailboats:

```bash
python sailboat_compare.py "Catalina 30" "Hunter 33"
```

Compare multiple boats:

```bash
python sailboat_compare.py "J/24" "J/80" "J/70"
```

Export to JSON:

```bash
python sailboat_compare.py "Catalina 30" "Hunter 33" --format json
```

Get help:

```bash
python sailboat_compare.py --help
```

## How It Works

1. The tool normalizes boat names to URL-friendly format
2. Fetches boat pages from sailboatdata.com using pattern: `/sailboat/{normalized-name}`
3. Parses HTML to extract specifications using BeautifulSoup
4. Displays results in a formatted comparison table using Rich

## Example Output

```
╭────────────────── ⛵ Sailboat Comparison ──────────────────╮
│ Specification     │ Catalina 30      │ Hunter 33         │
├───────────────────┼──────────────────┼───────────────────┤
│ LOA               │ 29.92 ft         │ 33.17 ft          │
│ Beam              │ 10.83 ft         │ 11.50 ft          │
│ Displacement      │ 10,200 lbs       │ 11,500 lbs        │
│ ...               │ ...              │ ...               │
╰───────────────────┴──────────────────┴───────────────────╯
```

## Development

### Project Structure

```
.
├── flake.nix              # Nix flake configuration
├── sailboat_compare.py    # Main CLI application
├── README.md              # This file
├── .gitignore            # Git ignore patterns
└── .envrc                # Direnv configuration
```

### Nix Development Shell

The flake provides a complete Python development environment with all dependencies:

- Python 3.11
- requests (HTTP client)
- beautifulsoup4 (HTML parsing)
- click (CLI framework)
- rich (terminal formatting)
- lxml (fast XML/HTML parser)

## Notes

- The tool respects robots.txt and uses appropriate User-Agent headers
- Rate limiting is handled by the requests session
- Some boats may not be found if the name doesn't match the URL format
- Specifications extracted depend on the HTML structure of sailboatdata.com

## License

MIT

## Disclaimer

This tool is for educational and research purposes. Please respect sailboatdata.com's terms of service and use responsibly.
