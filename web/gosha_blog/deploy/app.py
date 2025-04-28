from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from pymongo import MongoClient
from bson.json_util import dumps
import os
import datetime
import json

app = Flask(__name__)
app.secret_key = 'super_secret_key_123'  # Для работы с сессиями

# Подключение к MongoDB
mongodb_uri = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/')
client = MongoClient(mongodb_uri)
db = client['vulnerable_blog']
users = db['users']
posts = db['posts']

# Создание админа при первом запуске
if not users.find_one({'username': 'admin'}):
    users.insert_one({
        'username': 'admin',
        'password': 'admin123',
        'is_admin': True
    })
    print('Admin user created')

@app.route('/')
def index():
    all_posts = list(posts.find())
    return render_template('index.html', posts=all_posts, user=session.get('user'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Уязвимый код - напрямую использует пользовательский ввод в запросе
        try:
            # Пытаемся распарсить password как JSON
            if password.startswith('{') and password.endswith('}'):
                password = json.loads(password)
        except:
            pass
            
        query = {
            'username': username,
            'password': password
        }
        
        # Уязвимость здесь - можно отправить специально сформированный JSON
        user = users.find_one(query)
        
        if user:
            session['user'] = {
                'username': user['username'],
                'is_admin': user.get('is_admin', False)
            }
            return redirect(url_for('index'))
        else:
            flash('Неверные учетные данные')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not users.find_one({'username': username}):
            users.insert_one({
                'username': username,
                'password': password,
                'is_admin': False
            })
            return redirect(url_for('login'))
        else:
            flash('Пользователь уже существует')
    
    return render_template('register.html')

@app.route('/create_post', methods=['POST'])
def create_post():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    title = request.form.get('title')
    content = request.form.get('content')
    
    posts.insert_one({
        'title': title,
        'content': content,
        'author': session['user']['username']
    })
    
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 