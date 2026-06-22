import ollama
import json
import re

def analyze_social_data(text, model="llama3"):
    """
    Performs sentiment analysis and rigorous analytics on the extracted text and metrics.
    """
    prompt = f"""
    Analyze the following website content which may include social metrics (likes, comments, reviews).
    1. Perform a sentiment analysis of the reviews or overall content (Positive, Negative, Neutral).
    2. Summarize the key themes in the comments or reviews.
    3. If numerical metrics like likes, comments, or star ratings are present, provide a statistical summary.
    4. Provide actionable insights based on the analysis.

    Return the analysis in a structured format (Markdown).

    Content:
    {text}
    """

    try:
        response = ollama.chat(model=model, messages=[
            {
                'role': 'user',
                'content': prompt,
            },
        ])
        return response['message']['content']
    except Exception as e:
        return f"Error performing analytics: {e}"

def analyze_social_data_stream(text, model="llama3"):
    """
    Generator for streaming analytics results.
    """
    prompt = f"""
    Analyze the following website content which may include social metrics (likes, comments, reviews).
    1. Perform a sentiment analysis of the reviews or overall content (Positive, Negative, Neutral).
    2. Summarize the key themes in the comments or reviews.
    3. If numerical metrics like likes, comments, or star ratings are present, provide a statistical summary.
    4. Provide actionable insights based on the analysis.

    Return the analysis in a structured format (Markdown).

    Content:
    {text}
    """

    try:
        stream = ollama.chat(model=model, messages=[
            {
                'role': 'user',
                'content': prompt,
            },
        ], stream=True)
        for chunk in stream:
            yield chunk['message']['content']
    except Exception as e:
        yield f"Error performing analytics: {e}"
