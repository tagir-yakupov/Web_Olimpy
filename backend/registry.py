import os
import json
from flask import Blueprint, session, redirect, url_for, request, render_template

auth_bp = Blueprint('auth', __name__, url_prefix='')
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
USERS_FILE = os.path.join(ROOT_DIR, 'data', 'users.json')

users = {}


def load_users():
    global users
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                users = json.load(f)
        except Exception as e:
            print(f"Ошибка загрузки пользователей: {e}")
            users = {}
    else:
        users = {}


def save_users():
    try:
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Ошибка сохранения пользователей: {e}")


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('username', '').strip()
        pwd = request.form.get('password', '')

        if not name or not pwd:
            return render_template('auth.html', page_type='register', error='Заполните все поля')

        if len(name) < 3:
            return render_template('auth.html', page_type='register', error='Логин должен содержать минимум 3 символа')

        if name in users:
            return render_template('auth.html', page_type='register', error='Пользователь уже существует')

        users[name] = pwd
        save_users()
        session['user'] = name
        return redirect(url_for('main'))

    return render_template('auth.html', page_type='register')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form.get('username', '').strip()
        pwd = request.form.get('password', '')

        if name in users and users[name] == pwd:
            session['user'] = name
            return redirect(url_for('main'))
        else:
            return render_template('auth.html', page_type='login', error='Неверный логин или пароль')

    return render_template('auth.html', page_type='login')