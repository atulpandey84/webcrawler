# AI Local Web Crawler & Chat

An advanced AI tool to extract insights from websites and PDFs using local Ollama models. Featuring recursive crawling, multi-turn chat history, and streaming responses.

## Key Features

-   **True Recursive Crawling**: Follow internal links to analyze entire websites.
-   **Conversational Chat**: Multi-turn interface to ask follow-up questions about the extracted content.
-   **Streaming Responses**: Character-by-character response delivery for a snappy feel.
-   **Multi-format Support**: Extracts text from both websites and PDF files.
-   **Local History**: Persistent chat sessions stored in a local SQLite database.
-   **Enhanced Extraction**: Uses `trafilatura` for clean, noise-free text extraction.

## Prerequisites

1.  **Ollama**: Install and run [Ollama](https://ollama.com/).
2.  **Python**: Python 3.x required.

## Installation

```bash
pip install -r requirements.txt
playwright install chromium
```

## Usage

### Web Interface (Recommended)

```bash
python3 app.py
```
Access the interface at `http://localhost:5000`.

### Command-Line Interface

```bash
python3 crawler.py https://example.com --recursive --pages 5
```

## Testing

Run the enhanced test suite:
```bash
python3 test_crawler_enhanced.py
```
