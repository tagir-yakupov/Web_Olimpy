import os, json
from flask import Blueprint, session, redirect, url_for, request, render_template

auth_bp = Blueprint('auth', __name__)
USERS_FILE = os.path.join(os.path.dirname(__file__), 'users.json')
users = {}


def load_users():
    global users
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            users = json.load(f)


def save_users():
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False)


load_users()


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['username'].strip()
        pwd = request.form['password']

        if not name or not pwd:
            return render_template('auth.html', page_type='register', error='Заполните все поля')

        if name in users:
            return render_template('auth.html', page_type='register', error='Пользователь уже существует!')

        users[name] = pwd
        save_users()
        session['user'] = name
        return redirect(url_for('main'))

    return render_template('auth.html', page_type='register')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form['username'].strip()
        pwd = request.form['password']

        if name in users and users[name] == pwd:
            session['user'] = name
            return redirect(url_for('main'))
        else:
            return render_template('auth.html', page_type='login', error='Неверный логин или пароль')

    return render_template('auth.html', page_type='login')
