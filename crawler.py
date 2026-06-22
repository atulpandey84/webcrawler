import requests
from bs4 import BeautifulSoup
import argparse
import ollama
import sys
import trafilatura
from urllib.parse import urljoin, urlparse
import io
from pypdf import PdfReader
import re
import json

# Optional: Playwright for dynamic scraping
try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

def is_valid_url(url, base_domain):
    parsed = urlparse(url)
    return bool(parsed.netloc) and parsed.netloc == base_domain

def crawl_website(url, recursive=False, max_pages=5, use_playwright=False):
    """
    Fetches the content of a website and extracts clean text.
    If recursive is True, it will follow internal links up to max_pages.
    """
    domain = urlparse(url).netloc
    to_crawl = [url]
    crawled = set()
    all_content = []
    metrics_summary = []

    while to_crawl and len(crawled) < max_pages:
        current_url = to_crawl.pop(0)
        if current_url in crawled:
            continue

        print(f"Crawling: {current_url}")
        try:
            if current_url.lower().endswith('.pdf'):
                content = extract_pdf_content(current_url)
            elif use_playwright and PLAYWRIGHT_AVAILABLE:
                content, metrics = crawl_with_playwright(current_url)
                if metrics:
                    metrics_summary.append({current_url: metrics})
            else:
                downloaded = trafilatura.fetch_url(current_url)
                content = trafilatura.extract(downloaded)

                if recursive:
                    # Find internal links
                    response = requests.get(current_url, timeout=10)
                    soup = BeautifulSoup(response.text, 'html.parser')
                    for a in soup.find_all('a', href=True):
                        full_url = urljoin(current_url, a['href'])
                        if is_valid_url(full_url, domain) and full_url not in crawled:
                            to_crawl.append(full_url)

            if content:
                all_content.append(f"--- Source: {current_url} ---\n{content}")
            crawled.add(current_url)

            if not recursive:
                break

        except Exception as e:
            print(f"Error crawling {current_url}: {e}")
            crawled.add(current_url)

    final_content = "\n\n".join(all_content)
    if metrics_summary:
        final_content += "\n\n--- Extracted Metrics ---\n" + json.dumps(metrics_summary, indent=2)

    return final_content

def crawl_with_playwright(url):
    """
    Uses Playwright to load dynamic content and extract text and metrics.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="networkidle", timeout=60000)

        # Get full text
        content = page.content()
        soup = BeautifulSoup(content, 'html.parser')
        text = trafilatura.extract(content) or soup.get_text()

        # Simple heuristic metric extraction
        metrics = {}
        page_text = soup.get_text()

        # Search for patterns like "1.2k likes", "500 comments", etc.
        patterns = {
            'likes': r'(\d+[\d,.]*[kKmM]?)\s*likes?',
            'comments': r'(\d+[\d,.]*[kKmM]?)\s*comments?',
            'reviews': r'(\d+[\d,.]*[kKmM]?)\s*reviews?'
        }

        for key, pattern in patterns.items():
            matches = re.findall(pattern, page_text, re.IGNORECASE)
            if matches:
                # Take the most likely one (often the largest or first depending on context)
                metrics[key] = matches

        browser.close()
        return text, metrics

def extract_pdf_content(url):
    """
    Extracts text from a PDF URL.
    """
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    with io.BytesIO(response.content) as f:
        reader = PdfReader(f)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
    return text

def generate_insights(text, model, custom_prompt, chat_history=None):
    """
    Sends the extracted text to Ollama and gets insights.
    Supports chat history for conversational multi-turn.
    """
    if chat_history is None:
        chat_history = []

    if not custom_prompt:
        prompt = f"Please provide key insights and a summary for the following website content:\n\n{text}"
    else:
        if text:
            prompt = f"{custom_prompt}\n\nContent:\n{text}"
        else:
            prompt = custom_prompt

    messages = chat_history + [{'role': 'user', 'content': prompt}]

    try:
        response = ollama.chat(model=model, messages=messages)
        return response['message']['content']
    except Exception as e:
        return f"Error connecting to Ollama: {e}. Make sure Ollama is running locally."

def generate_insights_stream(text, model, custom_prompt, chat_history=None):
    """
    Generator for streaming insights from Ollama.
    """
    if chat_history is None:
        chat_history = []

    if not custom_prompt:
        prompt = f"Please provide key insights and a summary for the following website content:\n\n{text}"
    else:
        if text:
            prompt = f"{custom_prompt}\n\nContent:\n{text}"
        else:
            prompt = custom_prompt

    messages = chat_history + [{'role': 'user', 'content': prompt}]

    try:
        stream = ollama.chat(model=model, messages=messages, stream=True)
        for chunk in stream:
            yield chunk['message']['content']
    except Exception as e:
        yield f"Error connecting to Ollama: {e}"

def main():
    parser = argparse.ArgumentParser(description="AI Local Web Crawler with Ollama")
    parser.add_argument("url", help="The URL of the website to crawl")
    parser.add_argument("--model", default="llama3", help="Ollama model to use (default: llama3)")
    parser.add_argument("--prompt", help="Custom prompt for generating insights")
    parser.add_argument("--recursive", action="store_true", help="Enable recursive crawling")
    parser.add_argument("--pages", type=int, default=5, help="Max pages to crawl in recursive mode")
    parser.add_argument("--dynamic", action="store_true", help="Use Playwright for dynamic content and metric extraction")

    args = parser.parse_args()

    print(f"Crawling {args.url} (Recursive: {args.recursive}, Dynamic: {args.dynamic})...")
    content = crawl_website(args.url, recursive=args.recursive, max_pages=args.pages, use_playwright=args.dynamic)

    if not content:
        print("No content extracted.")
        sys.exit(1)

    # Basic truncation
    max_chars = 30000
    if len(content) > max_chars:
        print(f"Content too long ({len(content)} chars), truncating.")
        content = content[:max_chars]

    print(f"Generating insights using model: {args.model}...")
    insights = generate_insights(content, args.model, args.prompt)

    print("\n--- Insights ---\n")
    print(insights)

if __name__ == "__main__":
    main()
