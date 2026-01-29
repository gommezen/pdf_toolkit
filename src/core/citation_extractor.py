"""
Citation/metadata extraction from academic PDFs.
Extracts bibliographic information and exports to BibTeX or CSL-JSON format.
"""

import re
import json
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional
from datetime import datetime

import fitz  # PyMuPDF


@dataclass
class CitationMetadata:
    """Bibliographic metadata extracted from a PDF."""
    title: str = ""
    authors: list[str] = field(default_factory=list)
    year: Optional[int] = None
    doi: str = ""
    abstract: str = ""
    journal: str = ""
    volume: str = ""
    issue: str = ""
    pages: str = ""
    publisher: str = ""
    keywords: list[str] = field(default_factory=list)

    @property
    def author_string(self) -> str:
        """Get authors as a formatted string."""
        if not self.authors:
            return ""
        if len(self.authors) == 1:
            return self.authors[0]
        return ", ".join(self.authors[:-1]) + " and " + self.authors[-1]

    @property
    def bibtex_key(self) -> str:
        """Generate a BibTeX citation key."""
        # Use first author's last name + year
        if self.authors:
            first_author = self.authors[0]
            # Extract last name (handle "First Last" or "Last, First" format)
            if "," in first_author:
                last_name = first_author.split(",")[0].strip()
            else:
                parts = first_author.split()
                last_name = parts[-1] if parts else "unknown"
            # Clean up for BibTeX key
            last_name = re.sub(r'[^a-zA-Z]', '', last_name).lower()
        else:
            last_name = "unknown"

        year = str(self.year) if self.year else "0000"
        return f"{last_name}{year}"


@dataclass
class CitationResult:
    """Result of a citation extraction operation."""
    success: bool
    metadata: CitationMetadata
    confidence: float = 0.0  # 0-1 indicating extraction confidence
    warnings: list[str] = field(default_factory=list)
    error_message: str = ""
    source_file: str = ""


def extract_citation(pdf_path: str) -> CitationResult:
    """
    Extract citation metadata from a PDF file.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        CitationResult with extracted metadata
    """
    path = Path(pdf_path)
    if not path.exists():
        return CitationResult(
            success=False,
            metadata=CitationMetadata(),
            error_message=f"Filen findes ikke: {pdf_path}"
        )

    warnings = []
    confidence_scores = []

    try:
        doc = fitz.open(pdf_path)

        # Extract from PDF metadata
        pdf_metadata = doc.metadata or {}

        # Title
        title = pdf_metadata.get("title", "").strip()
        # Skip useless title values
        if title and title.lower() not in ("untitled", "unknown", ""):
            confidence_scores.append(0.9)
        else:
            # Try to extract from first page text
            title = _extract_title_from_text(doc)
            if title:
                confidence_scores.append(0.6)
                warnings.append("Titel udtrukket fra tekst (kan være upræcis)")
            else:
                warnings.append("Kunne ikke finde titel")

        # Authors
        author_string = pdf_metadata.get("author", "").strip()
        authors = _parse_authors(author_string)
        if authors:
            confidence_scores.append(0.85)
        else:
            # Try to extract from first page
            authors = _extract_authors_from_text(doc)
            if authors:
                confidence_scores.append(0.5)
                warnings.append("Forfattere udtrukket fra tekst (kan være upræcise)")
            else:
                warnings.append("Kunne ikke finde forfattere")

        # Year
        year = None
        creation_date = pdf_metadata.get("creationDate", "")
        if creation_date:
            year = _extract_year_from_date(creation_date)
            if year:
                confidence_scores.append(0.8)

        if not year:
            year = _extract_year_from_text(doc)
            if year:
                confidence_scores.append(0.5)

        if not year:
            warnings.append("Kunne ikke finde udgivelsesår")

        # DOI
        doi = _extract_doi(doc)
        if doi:
            confidence_scores.append(0.95)
        else:
            warnings.append("Ingen DOI fundet")

        # Abstract
        abstract = _extract_abstract(doc)
        if abstract:
            confidence_scores.append(0.7)
        else:
            warnings.append("Kunne ikke finde abstract")

        # Journal/Publisher
        journal = pdf_metadata.get("subject", "").strip()
        publisher = _clean_publisher(pdf_metadata.get("creator", "").strip())

        # Keywords
        keywords_str = pdf_metadata.get("keywords", "")
        keywords = [k.strip() for k in keywords_str.split(",") if k.strip()]

        doc.close()

        # Calculate overall confidence
        confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0

        metadata = CitationMetadata(
            title=title,
            authors=authors,
            year=year,
            doi=doi,
            abstract=abstract,
            journal=journal,
            publisher=publisher,
            keywords=keywords
        )

        return CitationResult(
            success=True,
            metadata=metadata,
            confidence=confidence,
            warnings=warnings,
            source_file=str(path.name)
        )

    except Exception as e:
        return CitationResult(
            success=False,
            metadata=CitationMetadata(),
            error_message=f"Fejl ved læsning af PDF: {str(e)}",
            source_file=str(path.name)
        )


def _extract_title_from_text(doc: fitz.Document) -> str:
    """Extract title from first page text (usually largest font at top)."""
    if len(doc) == 0:
        return ""

    first_page = doc[0]
    blocks = first_page.get_text("dict")["blocks"]

    # Look for text in the upper portion of the page with larger font
    candidates = []
    page_height = first_page.rect.height

    for block in blocks:
        if "lines" not in block:
            continue

        for line in block["lines"]:
            # Combine all spans in the same line
            line_text = ""
            max_font_size = 0
            y_pos = 0

            for span in line["spans"]:
                y_pos = span["bbox"][1]
                line_text += span["text"]
                max_font_size = max(max_font_size, span["size"])

            line_text = line_text.strip()

            # Only consider text in upper third of page
            if y_pos < page_height / 3:
                if len(line_text) > 5 and max_font_size > 12:
                    candidates.append((line_text, max_font_size, y_pos))

    if not candidates:
        return ""

    # Sort by font size (descending), then by position (ascending)
    candidates.sort(key=lambda x: (-x[1], x[2]))

    # Get the largest font texts - they might be multi-line title
    if candidates:
        largest_font = candidates[0][1]
        # Collect all lines with similar large font (within 2pt)
        title_parts = []
        for text, font_size, y_pos in candidates:
            if font_size >= largest_font - 2:
                title_parts.append((text, y_pos))
            else:
                break

        # Sort by vertical position and join
        title_parts.sort(key=lambda x: x[1])
        title = " ".join([t[0] for t in title_parts])

        # Clean up
        title = re.sub(r'\s+', ' ', title).strip()
        return title

    return ""


def _parse_authors(author_string: str) -> list[str]:
    """Parse author string into list of author names."""
    if not author_string:
        return []

    # Common separators
    separators = ["; ", " and ", " & ", ", and ", ","]

    authors = [author_string]

    for sep in separators:
        new_authors = []
        for author in authors:
            if sep in author:
                new_authors.extend(author.split(sep))
            else:
                new_authors.append(author)
        authors = new_authors

    # Clean up each author name
    authors = [a.strip() for a in authors if a.strip()]

    return authors


def _extract_authors_from_text(doc: fitz.Document) -> list[str]:
    """Try to extract authors from first page text."""
    if len(doc) == 0:
        return []

    first_page = doc[0]
    blocks = first_page.get_text("dict")["blocks"]
    page_height = first_page.rect.height

    # First, find the title font size to skip title-like text
    title_font_size = 0
    for block in blocks:
        if "lines" not in block:
            continue
        for line in block["lines"]:
            for span in line["spans"]:
                if span["bbox"][1] < page_height / 4:  # Upper quarter
                    title_font_size = max(title_font_size, span["size"])

    # Look for author-like text below title area with smaller font
    candidates = []

    for block in blocks:
        if "lines" not in block:
            continue

        for line in block["lines"]:
            line_text = ""
            max_font_size = 0
            y_pos = 0

            for span in line["spans"]:
                y_pos = span["bbox"][1]
                line_text += span["text"]
                max_font_size = max(max_font_size, span["size"])

            line_text = line_text.strip()

            # Skip if empty, too short, or in title area with title-size font
            if len(line_text) < 3:
                continue
            if max_font_size >= title_font_size - 1 and y_pos < page_height / 4:
                continue  # Skip title-size text in header

            # Look for author patterns in upper half of page
            if y_pos < page_height / 2:
                if _looks_like_author_line(line_text, max_font_size, title_font_size):
                    candidates.append((line_text, y_pos, max_font_size))

    if not candidates:
        return []

    # Sort by position (top first)
    candidates.sort(key=lambda x: x[1])

    # Collect all author names from consecutive author-like lines
    all_authors = []
    last_y = -100
    author_font_size = None

    for text, y_pos, font_size in candidates:
        # Check if this line is close to previous author line (within ~50 pixels or same font)
        if author_font_size is None:
            author_font_size = font_size

        # Allow gaps for affiliation lines between authors
        if last_y > 0 and y_pos - last_y > 100:
            # Too far apart, might be different section
            if len(all_authors) >= 1:
                break

        # Parse authors from this line
        authors = _parse_authors(text)
        for author in authors:
            # Validate: authors should have reasonable name patterns
            author_lower = author.lower()

            # Skip if looks like affiliation or institution
            skip_words = ['university', 'institute', 'department', 'college',
                          'laboratory', 'research', 'center', 'school', '@']
            if any(word in author_lower for word in skip_words):
                continue

            # Skip if too long or too short
            if len(author) > 40 or len(author) < 5:
                continue

            # Skip if doesn't look like a name (should have First Last pattern)
            if not re.search(r'^[A-Z][a-z]+\.?\s+[A-Z]', author):
                continue

            # Skip duplicates
            if author not in all_authors:
                all_authors.append(author)
                last_y = y_pos

    return all_authors


def _looks_like_author_line(text: str, font_size: float = 0, title_font_size: float = 0) -> bool:
    """Check if a text line looks like an author listing."""
    # Skip if contains common non-author words
    skip_words = ["abstract", "introduction", "university", "department",
                  "keywords", "email", "http", "www", "doi", "figure",
                  "table", "copyright", "received", "accepted", "published",
                  "proceedings", "conference", "journal", "vol.", "pp.",
                  "symposium", "ieee", "acm", "computing", "international",
                  "workshop", "transactions", "letters", "annual", "edition"]

    lower_text = text.lower()
    if any(word in lower_text for word in skip_words):
        return False

    # Skip if contains year pattern at start (likely conference/journal line)
    if re.match(r'^\d{4}\s', text):
        return False

    # Skip if font is too large (likely a title)
    if title_font_size > 0 and font_size >= title_font_size - 1:
        return False

    # Check for author-like patterns (names with possible separators)
    # Should contain mostly letters, spaces, commas, periods
    clean = re.sub(r'[a-zA-Z\s,.\-\'\*\d]', '', text)
    if len(clean) > len(text) * 0.3:  # More than 30% non-name characters
        return False

    # Should have at least one capital letter (name start)
    if not re.search(r'[A-Z]', text):
        return False

    # Should have multiple capital letters (multiple names or name parts)
    capitals = re.findall(r'[A-Z]', text)
    if len(capitals) < 2:
        return False

    # Good sign: contains common author separators
    if any(sep in text for sep in [', ', ' and ', ' & ']):
        return True

    # Good sign: looks like "First Last" or "F. Last" pattern
    if re.search(r'[A-Z][a-z]+\s+[A-Z][a-z]+', text):
        return True
    if re.search(r'[A-Z]\.\s*[A-Z][a-z]+', text):
        return True

    return False


def _clean_publisher(publisher: str) -> str:
    """Clean up publisher/creator metadata, removing garbage values."""
    if not publisher:
        return ""

    # Skip common garbage patterns
    garbage_patterns = [
        r'certified by',
        r'pdfeXpress',
        r'acrobat',
        r'adobe',
        r'microsoft',
        r'word',
        r'latex',
        r'pdflatex',
        r'dvips',
        r'ghostscript',
        r'distiller',
    ]

    lower_pub = publisher.lower()
    for pattern in garbage_patterns:
        if re.search(pattern, lower_pub, re.IGNORECASE):
            return ""

    return publisher


def _extract_year_from_date(date_string: str) -> Optional[int]:
    """Extract year from PDF date string (format: D:YYYYMMDDHHmmSS)."""
    match = re.search(r'D:(\d{4})', date_string)
    if match:
        year = int(match.group(1))
        current_year = datetime.now().year
        if 1900 <= year <= current_year + 1:
            return year
    return None


def _extract_year_from_text(doc: fitz.Document) -> Optional[int]:
    """Extract publication year from document text."""
    if len(doc) == 0:
        return None

    # Check first two pages
    text = ""
    for i in range(min(2, len(doc))):
        text += doc[i].get_text()

    # Look for year patterns
    current_year = datetime.now().year

    # Pattern: 4-digit year in common contexts
    patterns = [
        r'(?:published|received|accepted|copyright|©|\(c\)).*?(\d{4})',
        r'(\d{4})(?:\s*[-–]\s*\d{4})?\s*(?:by|copyright|©)',
        r'(?:vol\.?|volume).*?(\d{4})',
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            year = int(match.group(1))
            if 1950 <= year <= current_year + 1:
                return year

    # Fallback: find any reasonable year
    years = re.findall(r'\b(19\d{2}|20\d{2})\b', text[:5000])
    valid_years = [int(y) for y in years if 1950 <= int(y) <= current_year + 1]

    if valid_years:
        # Return most common year, or most recent if tie
        from collections import Counter
        year_counts = Counter(valid_years)
        return year_counts.most_common(1)[0][0]

    return None


def _extract_doi(doc: fitz.Document) -> str:
    """Extract DOI from document."""
    # Check first 2 pages
    text = ""
    for i in range(min(2, len(doc))):
        text += doc[i].get_text()

    # DOI pattern: 10.XXXX/... (until whitespace or end of string)
    pattern = r'(?:doi[:\s]*)?10\.\d{4,}/[^\s\]>)"}]+'
    match = re.search(pattern, text, re.IGNORECASE)

    if match:
        doi = match.group()
        # Clean up common trailing characters
        doi = re.sub(r'^(?:doi[:\s]*)', '', doi, flags=re.IGNORECASE)
        doi = doi.rstrip('.,;:')
        return doi

    return ""


def _extract_abstract(doc: fitz.Document) -> str:
    """Extract abstract from document."""
    if len(doc) == 0:
        return ""

    # Check first 3 pages
    text = ""
    for i in range(min(3, len(doc))):
        text += doc[i].get_text() + "\n"

    # Look for Abstract section
    patterns = [
        r'(?:^|\n)\s*Abstract\s*[:\-—]?\s*\n?(.*?)(?:\n\s*(?:Keywords|Introduction|1\.|1\s|Background|I\.)|\Z)',
        r'(?:^|\n)\s*ABSTRACT\s*\n?(.*?)(?:\n\s*(?:KEYWORDS|INTRODUCTION|1\.|1\s)|\Z)',
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            abstract = match.group(1).strip()
            # Fix hyphenation artifacts (e.g., "differ- ent" -> "different")
            abstract = re.sub(r'-\s+', '', abstract)
            # Clean up whitespace
            abstract = re.sub(r'\s+', ' ', abstract)
            # Limit length
            if len(abstract) > 50:  # Reasonable abstract length
                return abstract[:2000] if len(abstract) > 2000 else abstract

    return ""


def to_bibtex(metadata: CitationMetadata) -> str:
    """
    Convert citation metadata to BibTeX format.

    Args:
        metadata: CitationMetadata object

    Returns:
        BibTeX formatted string
    """
    lines = [f"@article{{{metadata.bibtex_key},"]

    if metadata.authors:
        # BibTeX uses "and" between authors
        author_str = " and ".join(metadata.authors)
        lines.append(f'    author = {{{author_str}}},')

    if metadata.title:
        lines.append(f'    title = {{{metadata.title}}},')

    if metadata.year:
        lines.append(f'    year = {{{metadata.year}}},')

    if metadata.journal:
        lines.append(f'    journal = {{{metadata.journal}}},')

    if metadata.volume:
        lines.append(f'    volume = {{{metadata.volume}}},')

    if metadata.issue:
        lines.append(f'    number = {{{metadata.issue}}},')

    if metadata.pages:
        lines.append(f'    pages = {{{metadata.pages}}},')

    if metadata.doi:
        lines.append(f'    doi = {{{metadata.doi}}},')

    if metadata.publisher:
        lines.append(f'    publisher = {{{metadata.publisher}}},')

    if metadata.abstract:
        # Escape special characters for BibTeX
        abstract = metadata.abstract.replace('{', '\\{').replace('}', '\\}')
        lines.append(f'    abstract = {{{abstract}}},')

    if metadata.keywords:
        lines.append(f'    keywords = {{{", ".join(metadata.keywords)}}},')

    # Remove trailing comma from last entry
    if lines[-1].endswith(','):
        lines[-1] = lines[-1][:-1]

    lines.append('}')

    return '\n'.join(lines)


def to_json(metadata: CitationMetadata) -> str:
    """
    Convert citation metadata to CSL-JSON format (compatible with Zotero).

    Args:
        metadata: CitationMetadata object

    Returns:
        JSON formatted string
    """
    csl_item = {
        "type": "article-journal",
        "id": metadata.bibtex_key,
    }

    if metadata.title:
        csl_item["title"] = metadata.title

    if metadata.authors:
        csl_item["author"] = []
        for author in metadata.authors:
            # Try to parse first/last name
            if "," in author:
                parts = author.split(",", 1)
                csl_item["author"].append({
                    "family": parts[0].strip(),
                    "given": parts[1].strip() if len(parts) > 1 else ""
                })
            else:
                parts = author.split()
                if len(parts) >= 2:
                    csl_item["author"].append({
                        "family": parts[-1],
                        "given": " ".join(parts[:-1])
                    })
                else:
                    csl_item["author"].append({"literal": author})

    if metadata.year:
        csl_item["issued"] = {"date-parts": [[metadata.year]]}

    if metadata.journal:
        csl_item["container-title"] = metadata.journal

    if metadata.volume:
        csl_item["volume"] = metadata.volume

    if metadata.issue:
        csl_item["issue"] = metadata.issue

    if metadata.pages:
        csl_item["page"] = metadata.pages

    if metadata.doi:
        csl_item["DOI"] = metadata.doi

    if metadata.publisher:
        csl_item["publisher"] = metadata.publisher

    if metadata.abstract:
        csl_item["abstract"] = metadata.abstract

    # Return as array (CSL-JSON is typically an array of items)
    return json.dumps([csl_item], indent=2, ensure_ascii=False)
