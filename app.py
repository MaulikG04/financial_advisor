import ssl
import nltk
from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_cors import CORS
import sqlite3
import requests
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Bypass SSL certificate verification for NLTK
ssl._create_default_https_context = ssl._create_unverified_context

# Download NLTK resources
nltk.download('punkt')
nltk.download('stopwords')

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)
app.secret_key = 'your_secret_key_here'  # Replace with a secure key

ALPHA_VANTAGE_API_KEY = 'IBJAG507EFXMV0TB'

def fetch_company_info(stock_symbol):
    url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={stock_symbol}&apikey={ALPHA_VANTAGE_API_KEY}"
    response = requests.get(url)
    return response.json()

def extract_keywords(description):
    stop_words = set(stopwords.words('english'))
    words = word_tokenize(description.lower())
    filtered_words = [word for word in words if word.isalnum() and word not in stop_words]
    return filtered_words

def get_keywords_for_portfolio(portfolio):
    keywords_dict = {}
    for stock in portfolio:
        company_info = fetch_company_info(stock)
        if 'Description' in company_info:
            keywords_dict[stock] = extract_keywords(company_info['Description'])
    return keywords_dict

def relevance_score(article_title, keywords):
    score = 0
    article_title = article_title.lower()
    for keyword_list in keywords.values():
        for keyword in keyword_list:
            if keyword in article_title:
                score += 1
    return score

def personalized_summaries(user_id):
    conn = sqlite3.connect('financial_news.db')
    c = conn.cursor()
    c.execute('SELECT * FROM articles')  # Fetch all articles
    articles = c.fetchall()
    conn.close()

    user_portfolio = get_user_portfolio(user_id)
    keywords = get_keywords_for_portfolio(user_portfolio)
    ranked_articles = sorted(articles, key=lambda article: relevance_score(article[1], keywords), reverse=True)
    return ranked_articles[:10]

def get_user_portfolio(user_id):
    conn = sqlite3.connect('financial_news.db')
    c = conn.cursor()
    c.execute('SELECT portfolio FROM users WHERE id = ?', (user_id,))
    portfolio = c.fetchone()[0].split(',')
    conn.close()
    return portfolio

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    
    if request.method == 'POST':
        name = request.form['regName']
        email = request.form['regEmail']
        portfolio = request.form['regPortfolio']
        
        conn = sqlite3.connect('financial_news.db')
        c = conn.cursor()
        try:
            c.execute('INSERT INTO users (name, email, portfolio) VALUES (?, ?, ?)', (name, email, portfolio))
            conn.commit()
            user_id = c.lastrowid
        except sqlite3.IntegrityError:
            c.execute('SELECT id FROM users WHERE email = ?', (email,))
            user = c.fetchone()
            if user:
                user_id = user[0]
            else:
                return jsonify({'message': 'An error occurred during registration.'}), 500
        finally:
            conn.close()
        
        return redirect(url_for('user_home', user_id=user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    if request.method == 'POST':
        email = request.form['logEmail']
        conn = sqlite3.connect('financial_news.db')
        c = conn.cursor()
        c.execute('SELECT id FROM users WHERE email = ?', (email,))
        user = c.fetchone()
        conn.close()

        if user:
            return redirect(url_for('user_home', user_id=user[0]))
        else:
            return render_template('login.html', error='Invalid email')

@app.route('/home/<int:user_id>')
def user_home(user_id):
    summaries = personalized_summaries(user_id)
    return render_template('index.html', user_id=user_id, summaries=summaries)

@app.route('/portfolio/<int:user_id>', methods=['GET', 'POST'])
def portfolio(user_id):
    if request.method == 'POST':
        data = request.get_json()
        portfolio = ','.join(data.get('portfolio', []))
        
        conn = sqlite3.connect('financial_news.db')
        c = conn.cursor()
        c.execute('UPDATE users SET portfolio = ? WHERE id = ?', (portfolio, user_id))
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Portfolio updated successfully'})
    else:
        portfolio = get_user_portfolio(user_id)
        return jsonify(portfolio)

@app.route('/summaries/<int:user_id>', methods=['GET'])
def summaries(user_id):
    summaries = personalized_summaries(user_id)
    return jsonify(summaries)

@app.route('/feedback', methods=['POST'])
def feedback():
    data = request.get_json()
    article_id = data['articleId']
    feedback = data['feedback']
    return jsonify({'message': 'Feedback received successfully'})

@app.route('/admin/users', methods=['GET'])
def list_users():
    conn = sqlite3.connect('financial_news.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users')
    users = c.fetchall()
    conn.close()
    return jsonify(users)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'GET':
        return render_template('admin_login.html')
    
    if request.method == 'POST':
        data = request.get_json()
        email = data['email']
        password = data['password']
        
        if email == 'rau@1.com' and password == 'raunak':  # Replace with secure credentials
            session['admin_logged_in'] = True
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'message': 'Invalid credentials'})

@app.route('/admin')
def admin():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    return render_template('admin.html')

@app.route('/delete_user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    conn = sqlite3.connect('financial_news.db')
    c = conn.cursor()
    try:
        c.execute('DELETE FROM users WHERE id = ?', (user_id,))
        conn.commit()
        message = 'User deleted successfully'
    except sqlite3.Error as e:
        message = f"An error occurred: {e}"
    finally:
        conn.close()
    return jsonify({'message': message})

if __name__ == '__main__':
    app.run(debug=True)
