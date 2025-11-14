#!/usr/bin/env python3
"""
Sailboat Data Comparison CLI Tool

Scrapes and compares sailboat specifications from sailboatdata.com
"""

import sys
import re
from typing import Dict, List, Optional
from urllib.parse import quote

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

    def fetch_boat_data(self, boat_name: str) -> Optional[Dict[str, str]]:
        """Fetch boat specifications from sailboatdata.com"""
        normalized_name = self.normalize_boat_name(boat_name)
        url = f"{BASE_URL}/sailboat/{normalized_name}"

        try:
            console.print(f"[dim]Fetching data for: {boat_name}...[/dim]")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "lxml")

            # Extract boat title - h1 tag without class
            title_elem = soup.find("h1")
            if not title_elem:
                console.print(f"[yellow]Warning: Could not find boat '{boat_name}'[/yellow]")
                return None

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
                        if label and value:
                            boat_data[label] = value

            # Also look for definition lists (dt/dd pairs)
            for dt in soup.find_all("dt"):
                dd = dt.find_next_sibling("dd")
                if dd:
                    label = dt.get_text(strip=True).rstrip(":")
                    value = dd.get_text(strip=True)
                    if label and value:
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
                            if label and value and len(value) < 200:
                                boat_data[label] = value

            if len(boat_data) <= 2:  # Only name and url
                console.print(f"[yellow]Warning: No specifications found for '{boat_name}'[/yellow]")
                return None

            return boat_data

        except requests.exceptions.RequestException as e:
            console.print(f"[red]Error fetching data for '{boat_name}': {e}[/red]")
            return None


def create_comparison_table(boats_data: List[Dict[str, str]]) -> Table:
    """Create a rich table comparing boat specifications"""

    if not boats_data:
        return None

    # Get all unique specification keys (excluding name and url)
    all_specs = set()
    for boat in boats_data:
        all_specs.update(k for k in boat.keys() if k not in ["name", "url"])

    all_specs = sorted(all_specs)

    # Create table
    table = Table(
        title="⛵ Sailboat Comparison",
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


@click.command()
@click.argument("boats", nargs=-1, required=True)
@click.option("--format", "-f", type=click.Choice(["table", "json"]), default="table", help="Output format")
def compare(boats: tuple, format: str):
    """
    Compare specifications for multiple sailboats from sailboatdata.com

    BOATS: Two or more boat names to compare (e.g., "Catalina 30" "Hunter 33")

    Examples:
        sailboat_compare.py "Catalina 30" "Hunter 33"
        sailboat_compare.py "J/24" "J/80" "J/70" --format json
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

    if format == "json":
        import json
        console.print_json(json.dumps(boats_data, indent=2))
    else:
        table = create_comparison_table(boats_data)
        if table:
            console.print()
            console.print(table)
            console.print()
            console.print("[dim]Data source: https://sailboatdata.com[/dim]")
        else:
            console.print("[red]Error: Could not create comparison table[/red]")


if __name__ == "__main__":
    compare()
