# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Python CLI tool for comparing sailboat specifications scraped from sailboatdata.com. The tool allows users to input multiple boat names and displays a side-by-side comparison of their specifications in a formatted table.

## Development Commands

### Environment Setup

```bash
# Enter Nix development shell (recommended)
nix develop

# Or use direnv for automatic loading
direnv allow
```

### Running the Tool

```bash
# Basic comparison
python sailboat_compare.py "Catalina 30" "Hunter 33"

# Multiple boats
python sailboat_compare.py "J/24" "J/80" "J/70"

# JSON output
python sailboat_compare.py "Catalina 30" "Hunter 33" --format json

# Help
python sailboat_compare.py --help
```

### Without Nix

```bash
# Install dependencies
pip install requests beautifulsoup4 click rich lxml

# Run tool
python sailboat_compare.py "boat1" "boat2"
```

## Architecture

### Core Components

- **SailboatScraper**: Handles web scraping from sailboatdata.com
  - Normalizes boat names to URL-friendly format
  - Fetches and parses HTML using BeautifulSoup
  - Extracts specifications from various HTML structures (tables, divs, definition lists)

- **CLI Interface**: Built with Click framework
  - Accepts multiple boat names as arguments
  - Supports table and JSON output formats

- **Display Layer**: Uses Rich library for formatted output
  - Creates comparison tables with proper styling
  - Handles console output with colors and formatting

### URL Pattern

Boats are accessed via: `https://sailboatdata.com/sailboat/{normalized-boat-name}`
- Boat names are normalized: lowercase, spaces→hyphens, special chars removed
- Example: "Catalina 30" → "catalina-30"

### Data Extraction

The scraper uses multiple strategies to extract specifications:
1. Table rows (`<tr>` with `<th>`/`<td>` pairs)
2. Definition lists (`<dt>`/`<dd>` pairs)
3. Divs with spec-related classes

### Nix Flake Structure

- Python 3.11 base environment
- Dependencies: requests, beautifulsoup4, click, rich, lxml
- Includes both development shell and package outputs
- Compatible with direnv via `.envrc`

## Important Notes

- The tool respects standard web scraping practices (User-Agent headers, reasonable requests)
- HTML structure parsing is resilient to multiple format variations
- Some boats may not be found if name normalization doesn't match URL format
- The scraper handles missing data gracefully with "-" placeholders
