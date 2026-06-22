import unittest
from unittest.mock import patch, MagicMock
from crawler import crawl_website, generate_insights, is_valid_url
import requests

class TestCrawlerEnhanced(unittest.TestCase):

    def test_is_valid_url(self):
        self.assertTrue(is_valid_url("https://example.com/page", "example.com"))
        self.assertFalse(is_valid_url("https://other.com/page", "example.com"))
        self.assertFalse(is_valid_url("/page", "example.com"))

    @patch('trafilatura.fetch_url')
    @patch('trafilatura.extract')
    def test_crawl_website_single(self, mock_extract, mock_fetch):
        mock_fetch.return_value = "<html><body>Some content</body></html>"
        mock_extract.return_value = "Extracted content"

        url = "http://example.com"
        result = crawl_website(url)

        self.assertIn("Extracted content", result)
        self.assertIn("--- Source: http://example.com ---", result)

    @patch('ollama.chat')
    def test_generate_insights_history(self, mock_ollama_chat):
        mock_ollama_chat.return_value = {
            'message': {'content': 'Response with history'}
        }

        history = [{'role': 'user', 'content': 'First question'}]
        result = generate_insights("Some text", "llama3", "Follow up", chat_history=history)

        self.assertEqual(result, "Response with history")
        args, kwargs = mock_ollama_chat.call_args
        self.assertEqual(len(kwargs['messages']), 2)

    @patch('requests.get')
    def test_extract_pdf(self, mock_get):
        mock_response = MagicMock()
        mock_response.content = b"pdf content"
        mock_get.return_value = mock_response

        with patch('crawler.PdfReader') as mock_pdf_reader:
            mock_page = MagicMock()
            mock_page.extract_text.return_value = "PDF Text"
            mock_pdf_reader.return_value.pages = [mock_page]

            from crawler import extract_pdf_content
            result = extract_pdf_content("http://example.com/test.pdf")
            self.assertEqual(result.strip(), "PDF Text")

if __name__ == '__main__':
    unittest.main()
