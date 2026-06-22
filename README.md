# AI Local Web Crawler with Ollama

This tool allows you to crawl a website and generate insights using a local Ollama instance.

## Prerequisites

1.  **Ollama**: Ensure you have [Ollama](https://ollama.com/) installed and running on your machine.
2.  **Python**: Ensure you have Python 3.x installed.

## Installation

Install the required Python dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run the crawler by providing a URL:

```bash
python3 crawler.py https://example.com
```

### Options

-   `--model`: Specify the Ollama model to use (default: `llama3`).
    ```bash
    python3 crawler.py https://example.com --model mistral
    ```
-   `--prompt`: Provide a custom prompt for generating insights.
    ```bash
    python3 crawler.py https://example.com --prompt "Summarize this content in 3 bullet points"
    ```

## Testing

You can run the included tests to verify the tool's logic:

```bash
python3 test_crawler.py
```
