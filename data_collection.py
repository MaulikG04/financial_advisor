import requests
import re
import sqlite3
from datetime import datetime
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from collections import Counter
from transformers import pipeline

nltk.download('punkt')

NEWS_API_KEY = 'f661a646e66540819ce0a0b3804d0cd4'  # Replace with your NewsAPI key

def fetch_financial_news():
    url = f'https://newsapi.org/v2/everything?q=finance&apiKey={NEWS_API_KEY}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        articles = data.get('articles', [])
        return articles
    else:
        print("Failed to fetch news articles")
        return []

def preprocess_text(text):
    text = re.sub(r'\s+', ' ', text)  # Remove extra whitespace
    text = re.sub(r'\[[0-9]*\]', '', text)  # Remove references
    text = re.sub(r'http\S+', '', text)  # Remove URLs
    return text.strip()

def score_sentences(text):
    sentences = sent_tokenize(text)
    words = word_tokenize(text)
    word_frequencies = Counter(words)
    sentence_scores = []
    for sentence in sentences:
        score = sum(word_frequencies[word] for word in word_tokenize(sentence))
        sentence_scores.append((score, sentence))
    return sentence_scores

def extractive_summary(text, n=5):
    sentence_scores = score_sentences(text)
    top_sentences = sorted(sentence_scores, reverse=True)[:n]
    summary = " ".join([sentence for score, sentence in top_sentences])
    return summary

summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def abstractive_summary(text):
    input_length = len(text.split())
    max_length = min(150, max(30, int(0.5 * input_length)))  # Ensure max_length is at least 30
    min_length = min(30, max(10, int(0.2 * input_length)))  # Ensure min_length is at least 10
    summary = summarizer(text, max_length=max_length, min_length=min_length, do_sample=False)
    return summary[0]['summary_text']

def hybrid_summary(text, n=5):
    initial_summary = extractive_summary(text, n)
    final_summary = abstractive_summary(initial_summary)
    return final_summary

def store_article(title, summary, url, published_at):
    conn = sqlite3.connect('financial_news.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO articles (title, content, url, published_at)
        VALUES (?, ?, ?, ?)
    ''', (title, summary, url, published_at))
    conn.commit()
    conn.close()

if __name__ == '__main__':
    news_articles = fetch_financial_news()
    for article in news_articles:
        title = article.get('title', 'No Title')
        content = preprocess_text(article.get('content', ''))
        summary = hybrid_summary(content)
        url = article.get('url', 'No URL')
        published_at = article.get('publishedAt', 'No Date')
        store_article(title, summary, url, published_at)
        print(f"Stored article: {title}")
        print(summary)
