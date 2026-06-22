import unittest
from unittest.mock import patch, MagicMock
from crawler import crawl_website, generate_insights
import requests

class TestCrawler(unittest.TestCase):

    @patch('requests.get')
    def test_crawl_website(self, mock_get):
        # Mock response from requests.get
        mock_response = MagicMock()
        mock_response.text = "<html><body><p>Hello, World!</p><script>console.log('test')</script></body></html>"
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        url = "http://example.com"
        result = crawl_website(url)

        self.assertEqual(result, "Hello, World!")
        mock_get.assert_called_once_with(url, timeout=10)

    @patch('ollama.chat')
    def test_generate_insights(self, mock_ollama_chat):
        # Mock response from ollama.chat
        mock_ollama_chat.return_value = {
            'message': {
                'content': 'This is a test insight.'
            }
        }

        text = "Hello, World!"
        model = "llama3"
        prompt = None

        result = generate_insights(text, model, prompt)

        self.assertEqual(result, "This is a test insight.")
        mock_ollama_chat.assert_called_once()
        args, kwargs = mock_ollama_chat.call_args
        self.assertEqual(kwargs['model'], 'llama3')
        self.assertIn("Hello, World!", kwargs['messages'][0]['content'])

    @patch('ollama.chat')
    def test_generate_insights_custom_prompt(self, mock_ollama_chat):
        mock_ollama_chat.return_value = {
            'message': {
                'content': 'Custom insight.'
            }
        }

        text = "Hello, World!"
        model = "llama3"
        prompt = "Custom prompt"

        result = generate_insights(text, model, prompt)

        self.assertEqual(result, "Custom insight.")
        args, kwargs = mock_ollama_chat.call_args
        self.assertIn("Custom prompt", kwargs['messages'][0]['content'])
        self.assertIn("Hello, World!", kwargs['messages'][0]['content'])

if __name__ == '__main__':
    unittest.main()
