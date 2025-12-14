# Public Notices Scraper & Analyzer

A Python-based tool for scraping, processing, and analyzing public notices from the Hattiesburg American newspaper using LLMs (Large Language Models). The project fetches public notices via API, processes them with AI to extract structured information, and provides a web-based viewer for browsing and filtering results.

## Features

- **Automated Scraping**: Fetches public notices from Hattiesburg American's public notices API with pagination support
- **Duplicate Detection**: Tracks previously downloaded notices to avoid redundant API calls
- **AI-Powered Analysis**: Uses Claude (Haiku 4.5) to extract structured information from unstructured notice text
- **Interactive Web Viewer**: HTML-based interface for browsing, filtering, and analyzing processed notices
- **Incremental Processing**: Supports batch processing with `--limit` flag for testing

## Components

### 1. `notices.py`
Scrapes public notices from the Hattiesburg American website:
- Searches for notices containing "request for bids"
- Date range: October 1, 2025 onwards
- Handles pagination automatically
- Saves raw results to `notices_results.json`
- Tracks existing notices to avoid duplicates

### 2. `process_notices.py`
Processes raw notices using LLM analysis:
- Extracts structured information from each notice:
  - Agency/organization issuing the notice
  - Docket or case number
  - Brief description
  - Category (e.g., "Construction Bid", "Oil & Gas", "Legal Summons")
  - Key dates and events
  - Newsworthiness score (1-10)
- Saves analyzed data to `processed_notices.json`
- Supports `--limit` flag for testing (e.g., `--limit 10`)

### 3. `index.html`
Interactive web viewer for browsing processed notices:
- Filter by date range, category, and newsworthiness score
- Sort by newsworthiness or date
- View agency information, descriptions, and key dates
- Responsive design for desktop and mobile viewing

## Installation

```bash
# Install dependencies using uv (recommended) or pip
uv pip install -e .
# or
pip install -e .
```

Dependencies:
- `requests-html` - Web scraping and session management
- `llm` - LLM integration for AI analysis
- `lxml-html-clean` - HTML parsing

## Usage

### Step 1: Scrape Public Notices

```bash
python notices.py
```

This will fetch all public notices matching the search criteria and save them to `notices_results.json`. Subsequent runs will only add new notices.

### Step 2: Process with LLM

```bash
# Process all notices
python process_notices.py

# Or process a limited batch for testing
python process_notices.py --limit 10
```

This analyzes each notice and saves structured data to `processed_notices.json`.

### Step 3: View Results

Open `index.html` in a web browser to browse and filter the processed notices.

## Data Structure

### Raw Notices (`notices_results.json`)
Contains raw API responses with:
- Notice ID
- Publication information
- Start and end dates
- Full text of the notice

### Processed Notices (`processed_notices.json`)
Contains structured analysis:
```json
{
  "_id": "notice-id",
  "publication": "Hattiesburg American",
  "date_start": "2025-12-01",
  "date_end": "2025-12-15",
  "agency": "City of Hattiesburg",
  "docket_no": "RFB-2025-123",
  "description": "Request for bids for road construction project on Main Street",
  "category": "Construction Bid",
  "key_dates": [
    {"date": "2025-12-20", "event": "Bid submission deadline"}
  ],
  "newsworthiness": 6
}
```

## Requirements

- Python 3.12+
- Active internet connection for scraping
- API access to an LLM service (configured via `llm` package)

## License

This project is for research and educational purposes.
