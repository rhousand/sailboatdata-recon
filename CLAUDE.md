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

# PDF export
python sailboat_compare.py "Catalina 30" "Hunter 33" --pdf comparison.pdf

# Help
python sailboat_compare.py --help
```

### Without Nix

```bash
# Using pip
pip install -r requirements.txt

# Using conda
conda env create -f environment.yml
conda activate sailboat-compare

# Using uv
uv venv && source .venv/bin/activate
uv pip install -r requirements.txt

# Run tool
python sailboat_compare.py "boat1" "boat2"
```

## Architecture

### Core Components

- **SailboatScraper**: Handles web scraping from sailboatdata.com
  - Normalizes boat names to URL-friendly format
  - Intelligent boat name search with automatic variations (number-word conversions, spacing, etc.)
  - Fetches and parses HTML using BeautifulSoup with lxml parser
  - Extracts specifications from various HTML structures (tables, divs, definition lists)
  - Filters out unwanted specifications (e.g., "View All Topics", "Create Topic")

- **CLI Interface**: Built with Click framework
  - Accepts multiple boat names as arguments
  - Supports table, JSON, and PDF output formats
  - Includes --pdf flag for PDF export

- **Display Layer**: Uses Rich library for formatted output
  - Creates comparison tables with proper styling
  - Handles console output with colors and formatting
  - Includes attribution to sailboatdata.com in all outputs

- **PDF Export**: Uses ReportLab library for PDF generation
  - Professional table formatting with headers and styling
  - Uses Times New Roman font family (Times-Roman, Times-Bold)
  - Automatic page orientation based on boat count
  - Includes attribution header and generation timestamp

### URL Pattern

Boats are accessed via: `https://sailboatdata.com/sailboat/{normalized-boat-name}`
- Boat names are normalized: lowercase, spaces→hyphens, special chars removed
- Example: "Catalina 30" → "catalina-30"

### Data Extraction

The scraper uses multiple strategies to extract specifications:
1. Table rows (`<tr>` with `<th>`/`<td>` pairs)
2. Definition lists (`<dt>`/`<dd>` pairs)
3. Divs with `<strong>`/`<b>` tags containing label:value patterns

### Boat Name Search Intelligence

When a boat name is not found directly, the tool automatically tries variations:
- Number-to-word conversions (e.g., "30" ↔ "thirty")
- Spacing variations before numbers (e.g., "Catalina30" ↔ "Catalina 30")
- Decimal point handling (e.g., "40.1" → "401")
- Brand/model reordering (e.g., "Beneteau Oceanis 40.1" → "Oceanis 401 Beneteau")

This fuzzy matching ensures users can find boats even when the exact naming convention is unclear.

### Nix Flake Structure

- Python 3.13 base environment
- Dependencies: requests, beautifulsoup4, click, rich, lxml, reportlab, black
- Includes both development shell and package outputs
- Compatible with direnv via `.envrc`

### Code Formatting

The project uses Black formatter with Python 3.13 target for consistent code formatting:

- **Automatic Formatting**: Claude Code is configured with PostToolUse hooks that automatically run `black -t py313` on all Python files after editing or writing
- **Manual Formatting**: Run `black -t py313 <filename>.py` to format a specific file
- **Hook Configuration**: Defined in `.claude/settings.local.json` under `hooks.PostToolUse`
- **Permissions**: `Bash(black:*)` is pre-approved in the settings for automatic execution

The hooks ensure all Python code maintains consistent formatting without manual intervention.

## Important Notes

- The tool respects standard web scraping practices (User-Agent headers, reasonable requests)
- HTML structure parsing is resilient to multiple format variations
- Intelligent boat name search tries multiple variations automatically when direct lookup fails
- The scraper handles missing data gracefully with "-" placeholders
- Unwanted UI elements are filtered from specifications (e.g., forum topics, navigation links)
- Provides clear feedback when boats are found under alternative names
- All outputs (CLI, JSON, PDF) include proper attribution to sailboatdata.com
- PDF exports automatically adjust orientation based on the number of boats being compared
