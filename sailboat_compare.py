#!/usr/bin/env python3
"""
Sailboat Data Comparison CLI Tool

Scrapes and compares sailboat specifications from sailboatdata.com
"""

import sys
import re
from typing import Dict, List, Optional
from urllib.parse import quote
from datetime import datetime

import click
import requests
from bs4 import BeautifulSoup
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

console = Console()

BASE_URL = "https://sailboatdata.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}


class SailboatScraper:
    """Scraper for sailboatdata.com"""

    # Specifications to exclude from the output
    EXCLUDED_SPECS = {"View All Topics", "Create Topic", "Latest Topics"}

    @staticmethod
    def should_exclude_spec(label: str, value: str = "") -> bool:
        """Check if a specification should be excluded from output"""
        if label in SailboatScraper.EXCLUDED_SPECS:
            return True
        # Check both label and value for topic-related forum UI (case-insensitive)
        combined_text = (label + " " + value).lower()
        if "topic +" in combined_text or "create a topic" in combined_text:
            return True
        return False

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)

    def normalize_boat_name(self, name: str) -> str:
        """Convert boat name to URL-friendly format"""
        # Remove special characters, convert to lowercase, replace spaces with hyphens
        normalized = name.lower().strip()
        normalized = re.sub(r"[^\w\s-]", "", normalized)
        normalized = re.sub(r"[\s_]+", "-", normalized)
        return normalized

    def search_boat_name(self, query: str) -> Optional[tuple[str, str]]:
        """
        Try common variations of boat name to find the correct one
        Returns: (correct_name, normalized_url_name) or None if not found
        """
        console.print(f"[dim]Searching for variations of: {query}...[/dim]")

        # Generate common variations of the boat name
        variations = []

        # Original query
        variations.append(query)

        # Bidirectional number-word mapping
        number_words = {
            "20": "twenty", "21": "twenty-one", "22": "twenty-two", "23": "twenty-three",
            "24": "twenty-four", "25": "twenty-five", "26": "twenty-six", "27": "twenty-seven",
            "28": "twenty-eight", "29": "twenty-nine", "30": "thirty", "31": "thirty-one",
            "32": "thirty-two", "33": "thirty-three", "34": "thirty-four", "35": "thirty-five",
            "36": "thirty-six", "37": "thirty-seven", "38": "thirty-eight", "39": "thirty-nine",
            "40": "forty", "41": "forty-one", "42": "forty-two", "43": "forty-three",
            "44": "forty-four", "45": "forty-five", "46": "forty-six", "47": "forty-seven",
            "48": "forty-eight", "49": "forty-nine", "50": "fifty"
        }

        # Create reverse mapping (words to numbers)
        word_numbers = {word: num for num, word in number_words.items()}

        # Try replacing numbers with words (e.g., "30" -> "thirty")
        for num, word in number_words.items():
            if num in query:
                variations.append(query.replace(num, word))
                break

        # Try replacing words with numbers (e.g., "thirty" -> "30")
        query_lower = query.lower()
        for word, num in word_numbers.items():
            if word in query_lower:
                variations.append(query_lower.replace(word, num))
                break

        # Try with/without spaces before numbers
        if re.search(r'\d', query):
            # Add version with space before number if there isn't one
            spaced = re.sub(r'([a-zA-Z])(\d)', r'\1 \2', query)
            if spaced != query:
                variations.append(spaced)
            # Add version without space before number
            no_space = re.sub(r'\s+(\d)', r'\1', query)
            if no_space != query:
                variations.append(no_space)

        # Handle decimal points in model numbers (e.g., "40.1" -> "401")
        if '.' in query:
            variations.append(query.replace('.', ''))

        # Try reversing brand and model order for boats like "Beneteau Oceanis 40.1"
        # which might be stored as "Oceanis 401 Beneteau"
        parts = query.split()
        if len(parts) >= 2:
            # Try moving first word to the end
            reordered = ' '.join(parts[1:] + [parts[0]])
            variations.append(reordered)
            # Also try with decimals removed
            if '.' in reordered:
                variations.append(reordered.replace('.', ''))

        # Try each variation
        for variation in variations:
            try:
                normalized = self.normalize_boat_name(variation)
                url = f"{BASE_URL}/sailboat/{normalized}"

                response = self.session.get(url, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, "lxml")
                    title_elem = soup.find("h1")
                    if title_elem:
                        display_name = title_elem.get_text(strip=True)
                        return (display_name, normalized)

            except requests.exceptions.RequestException:
                continue

        return None

    def fetch_boat_data(self, boat_name: str) -> Optional[Dict[str, str]]:
        """Fetch boat specifications from sailboatdata.com"""
        normalized_name = self.normalize_boat_name(boat_name)
        url = f"{BASE_URL}/sailboat/{normalized_name}"
        original_boat_name = boat_name  # Keep track of original name

        try:
            console.print(f"[dim]Fetching data for: {boat_name}...[/dim]")
            response = self.session.get(url, timeout=10)

            # If we get 404 or no title found, try searching for variations
            soup = None
            title_elem = None

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, "lxml")
                title_elem = soup.find("h1")

            # If page not found or no title, try searching for the correct name
            if response.status_code != 200 or not title_elem:
                search_result = self.search_boat_name(boat_name)
                if search_result:
                    correct_name, correct_normalized = search_result
                    console.print(
                        f"[yellow]'{boat_name}' not found. Using '{correct_name}' instead.[/yellow]"
                    )
                    # Fetch with the correct name
                    normalized_name = correct_normalized
                    url = f"{BASE_URL}/sailboat/{normalized_name}"
                    response = self.session.get(url, timeout=10)
                    response.raise_for_status()
                    soup = BeautifulSoup(response.content, "lxml")
                    title_elem = soup.find("h1")

            if not title_elem:
                console.print(f"[yellow]Warning: Could not find boat '{original_boat_name}'[/yellow]")
                return None

            response.raise_for_status()  # Raise error if final response failed

            boat_data = {
                "name": title_elem.get_text(strip=True),
                "url": url,
            }

            # Extract specifications from tables
            tables = soup.find_all("table")
            for table in tables:
                rows = table.find_all("tr")
                for row in rows:
                    cells = row.find_all(["th", "td"])
                    if len(cells) >= 2:
                        label = cells[0].get_text(strip=True).rstrip(":")
                        value = cells[1].get_text(strip=True)
                        if label and value and not self.should_exclude_spec(label, value):
                            boat_data[label] = value

            # Also look for definition lists (dt/dd pairs)
            for dt in soup.find_all("dt"):
                dd = dt.find_next_sibling("dd")
                if dd:
                    label = dt.get_text(strip=True).rstrip(":")
                    value = dd.get_text(strip=True)
                    if label and value and not self.should_exclude_spec(label, value):
                        boat_data[label] = value

            # Extract from divs with strong/b tags (for calculated values)
            for strong in soup.find_all(["strong", "b"]):
                text = strong.get_text(strip=True)
                if ":" in text or text.endswith("."):
                    # This might be a label, look for value nearby
                    parent = strong.parent
                    if parent:
                        parent_text = parent.get_text(strip=True)
                        # Try to extract label:value pattern
                        match = re.search(r"(.+?):\s*(.+)", parent_text)
                        if match:
                            label = match.group(1).strip()
                            value = match.group(2).strip()
                            if label and value and len(value) < 200 and not self.should_exclude_spec(label, value):
                                boat_data[label] = value

            if len(boat_data) <= 2:  # Only name and url
                console.print(f"[yellow]Warning: No specifications found for '{boat_name}'[/yellow]")
                return None

            return boat_data

        except requests.exceptions.RequestException as e:
            console.print(f"[red]Error fetching data for '{boat_name}': {e}[/red]")
            return None


def create_comparison_table(boats_data: List[Dict[str, str]], show_attribution: bool = True) -> Table:
    """Create a rich table comparing boat specifications"""

    if not boats_data:
        return None

    # Get all unique specification keys (excluding name and url)
    all_specs = set()
    for boat in boats_data:
        all_specs.update(k for k in boat.keys() if k not in ["name", "url"])

    all_specs = sorted(all_specs)

    # Create table with attribution in title if requested
    title = "⛵ Sailboat Comparison"
    if show_attribution:
        title = "⛵ Sailboat Comparison\nData obtained from sailboatdata.com"

    table = Table(
        title=title,
        box=box.ROUNDED,
        show_header=True,
        header_style="bold cyan",
        border_style="blue",
    )

    # Add columns
    table.add_column("Specification", style="bold yellow", no_wrap=False)
    for boat in boats_data:
        table.add_column(boat["name"], style="green", no_wrap=False)

    # Add rows
    for spec in all_specs:
        row = [spec]
        for boat in boats_data:
            value = boat.get(spec, "-")
            row.append(value)
        table.add_row(*row)

    return table


def create_pdf(boats_data: List[Dict[str, str]], filename: str) -> bool:
    """Create a PDF comparison of boat specifications"""
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter, landscape
        from reportlab.platypus import SimpleDocTemplate, Table as PDFTable, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib.enums import TA_CENTER
    except ImportError:
        console.print("[red]Error: reportlab is required for PDF export. Install it with: pip install reportlab[/red]")
        return False

    if not boats_data:
        return False

    # Get all unique specification keys
    all_specs = set()
    for boat in boats_data:
        all_specs.update(k for k in boat.keys() if k not in ["name", "url"])
    all_specs = sorted(all_specs)

    # Create PDF
    doc = SimpleDocTemplate(
        filename,
        pagesize=landscape(letter) if len(boats_data) > 2 else letter,
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch,
    )

    # Container for elements
    elements = []
    styles = getSampleStyleSheet()

    # Add title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName='Times-Bold',
        fontSize=16,
        textColor=colors.HexColor('#1f77b4'),
        spaceAfter=6,
        alignment=TA_CENTER,
    )
    title = Paragraph("Sailboat Comparison", title_style)
    elements.append(title)

    # Add attribution
    attribution_style = ParagraphStyle(
        'Attribution',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=10,
        textColor=colors.grey,
        spaceAfter=12,
        alignment=TA_CENTER,
    )
    attribution = Paragraph("Data obtained from sailboatdata.com", attribution_style)
    elements.append(attribution)

    # Add generation date
    date_text = Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", attribution_style)
    elements.append(date_text)
    elements.append(Spacer(1, 0.2*inch))

    # Prepare table data
    table_data = []

    # Header row
    header = ["Specification"] + [boat["name"] for boat in boats_data]
    table_data.append(header)

    # Data rows
    for spec in all_specs:
        row = [spec]
        for boat in boats_data:
            value = boat.get(spec, "-")
            row.append(value)
        table_data.append(row)

    # Create table
    pdf_table = PDFTable(table_data, repeatRows=1)

    # Style the table
    table_style = TableStyle([
        # Header styling
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),

        # Specification column styling
        ('BACKGROUND', (0, 1), (0, -1), colors.HexColor('#f0f0f0')),
        ('FONTNAME', (0, 1), (0, -1), 'Times-Bold'),
        ('FONTSIZE', (0, 1), (0, -1), 9),

        # Data cells styling
        ('FONTNAME', (1, 1), (-1, -1), 'Times-Roman'),
        ('FONTSIZE', (1, 1), (-1, -1), 8),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),

        # Grid
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),

        # Padding
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ])

    pdf_table.setStyle(table_style)
    elements.append(pdf_table)

    # Add footer
    elements.append(Spacer(1, 0.3*inch))
    footer = Paragraph(
        f"Visit <a href='https://sailboatdata.com'>sailboatdata.com</a> for more information",
        attribution_style
    )
    elements.append(footer)

    # Build PDF
    try:
        doc.build(elements)
        return True
    except Exception as e:
        console.print(f"[red]Error creating PDF: {e}[/red]")
        return False


@click.command()
@click.argument("boats", nargs=-1, required=True)
@click.option("--format", "-f", type=click.Choice(["table", "json"]), default="table", help="Output format")
@click.option("--pdf", type=click.Path(), default=None, help="Export comparison to PDF file")
def compare(boats: tuple, format: str, pdf: Optional[str]):
    """
    Compare specifications for multiple sailboats from sailboatdata.com

    BOATS: Two or more boat names to compare (e.g., "Catalina 30" "Hunter 33")

    Examples:
        sailboat_compare.py "Catalina 30" "Hunter 33"
        sailboat_compare.py "J/24" "J/80" "J/70" --format json
        sailboat_compare.py "Catalina 30" "Hunter 33" --pdf comparison.pdf
    """
    if len(boats) < 2:
        console.print("[red]Error: Please provide at least two boat names to compare[/red]")
        sys.exit(1)

    console.print(Panel.fit(
        f"[bold cyan]Comparing {len(boats)} sailboats[/bold cyan]\n" +
        "\n".join(f"  • {boat}" for boat in boats),
        title="🌊 Sailboat Data Comparison",
        border_style="blue"
    ))

    scraper = SailboatScraper()
    boats_data = []

    for boat_name in boats:
        data = scraper.fetch_boat_data(boat_name)
        if data:
            boats_data.append(data)

    if not boats_data:
        console.print("[red]Error: No boat data could be fetched[/red]")
        sys.exit(1)

    if len(boats_data) < len(boats):
        console.print(f"[yellow]Warning: Only {len(boats_data)} of {len(boats)} boats found[/yellow]\n")

    # Handle PDF export
    if pdf:
        console.print(f"[dim]Generating PDF: {pdf}...[/dim]")
        if create_pdf(boats_data, pdf):
            console.print(f"[green]✓ PDF created successfully: {pdf}[/green]")
        else:
            console.print("[red]✗ Failed to create PDF[/red]")
            sys.exit(1)

    # Handle output format
    if format == "json":
        import json
        # Add attribution to JSON output
        output = {
            "attribution": "Data obtained from sailboatdata.com",
            "generated": datetime.now().isoformat(),
            "boats": boats_data
        }
        console.print_json(json.dumps(output, indent=2))
    else:
        table = create_comparison_table(boats_data, show_attribution=True)
        if table:
            console.print()
            console.print(table)
            console.print()
        else:
            console.print("[red]Error: Could not create comparison table[/red]")


if __name__ == "__main__":
    compare()
