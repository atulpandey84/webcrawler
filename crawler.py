import requests
from bs4 import BeautifulSoup
import argparse
import ollama
import sys

def crawl_website(url):
    """
    Fetches the content of a website and extracts clean text.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the URL: {e}")
        sys.exit(1)

    soup = BeautifulSoup(response.text, 'html.parser')

    # Remove script and style elements
    for script_or_style in soup(["script", "style"]):
        script_or_style.decompose()

    # Get text
    text = soup.get_text()

    # Break into lines and remove leading and trailing whitespace
    lines = (line.strip() for line in text.splitlines())
    # Break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # Drop blank lines
    clean_text = '\n'.join(chunk for chunk in chunks if chunk)

    return clean_text

def generate_insights(text, model, custom_prompt):
    """
    Sends the extracted text to Ollama and gets insights.
    """
    if not custom_prompt:
        prompt = f"Please provide key insights and a summary for the following website content:\n\n{text}"
    else:
        prompt = f"{custom_prompt}\n\nContent:\n{text}"

    try:
        response = ollama.chat(model=model, messages=[
            {
                'role': 'user',
                'content': prompt,
            },
        ])
        return response['message']['content']
    except Exception as e:
        return f"Error connecting to Ollama: {e}. Make sure Ollama is running locally."

def main():
    parser = argparse.ArgumentParser(description="AI Local Web Crawler with Ollama")
    parser.add_argument("url", help="The URL of the website to crawl")
    parser.add_argument("--model", default="llama3", help="Ollama model to use (default: llama3)")
    parser.add_argument("--prompt", help="Custom prompt for generating insights")

    args = parser.parse_args()

    print(f"Crawling {args.url}...")
    content = crawl_website(args.url)

    # Basic truncation if content is too long for a typical LLM context window (optional, but good for stability)
    # Most local models handle 4k-8k tokens, so we'll do a rough character limit for now.
    max_chars = 15000
    if len(content) > max_chars:
        print(f"Content too long ({len(content)} chars), truncating to {max_chars} chars.")
        content = content[:max_chars]

    print(f"Generating insights using model: {args.model}...")
    insights = generate_insights(content, args.model, args.prompt)

    print("\n--- Insights ---\n")
    print(insights)

if __name__ == "__main__":
    main()
