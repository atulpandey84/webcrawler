from flask import Flask, render_template, request, jsonify
from crawler import crawl_website, generate_insights
import requests

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/insights', methods=['POST'])
def get_insights():
    data = request.json
    url = data.get('url')
    model = data.get('model', 'llama3')
    prompt = data.get('prompt')

    if not url:
        return jsonify({'error': 'URL is required'}), 400

    try:
        content = crawl_website(url)

        # Truncate content
        max_chars = 15000
        if len(content) > max_chars:
            content = content[:max_chars]

        insights = generate_insights(content, model, prompt)
        return jsonify({'insights': insights})
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Failed to crawl website: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
