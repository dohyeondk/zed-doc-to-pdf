# Zed Documentation to PDF

A Python script that downloads the entire [Zed editor documentation](https://zed.dev/docs) and merges it into a single PDF file with a working table of contents.

## Features

- Downloads all Zed documentation pages as individual PDFs
- Merges them into a single PDF file with clickable bookmarks
- Preserves document structure with a complete table of contents
- Custom CSS styling for clean, readable output

## Requirements

- Python 3.10+
- uv (recommended) or pip

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd zed-doc-to-pdf
```

2. Install dependencies:
```bash
uv sync
```

3. Install Playwright browsers:
```bash
playwright install chromium
```

## Usage

Run the script:
```bash
python main.py
```

The script will:
1. Fetch the table of contents from Zed documentation
2. Download each page as a PDF to `zed-docs-pdf/` directory
3. Merge all PDFs into `Zed.pdf` with working TOC links

## License

MIT
