"""
Основной файл Flask приложения
"""
import os
import sys
from datetime import timedelta
from flask import Flask, session, redirect, url_for, request, render_template, flash

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT_DIR)


from backend.registry import auth_bp
from backend.math_info import math_th_bp
from backend.admin_panel_th import conf_th
from backend.parse1 import load_tasks, load_math_oge
from backend.database.db_session import global_init, create_session
from backend.database.models import UserModel

# Инициализация БД
DB_DIR = os.path.join(ROOT_DIR, 'data')
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = os.path.join(DB_DIR, 'users.db')
global_init(DB_PATH)

# Инициализация приложения
app = Flask(__name__,
            template_folder=os.path.join(ROOT_DIR, 'templates'),
            static_folder=os.path.join(ROOT_DIR, 'static'))
app.secret_key = 'замените_на_случайный_ключ_минимум_32_символа'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

# Регистрация blueprint'ов
app.register_blueprint(auth_bp)
app.register_blueprint(math_th_bp)  # ← Регистрируем теорию по математике
app.register_blueprint(conf_th)

# Загружаем задания
tasks_info = load_tasks()
tasks_math = load_math_oge()




@app.route('/')
@app.route('/main')
def main():
    """Главная страница"""
    user_name = session.get('user_name')
    return render_template("main_page.html", title="Главная страница", user=user_name)


@app.route('/profile')
def profile():
    """Страница профиля"""
    if 'user_id' not in session:
        flash('Пожалуйста, войдите в систему', 'warning')
        return redirect(url_for('auth.login'))

    db_session = create_session()
    user = db_session.query(UserModel).get(session['user_id'])
    db_session.close()

    if not user:
        session.clear()
        flash('Пользователь не найден', 'danger')
        return redirect(url_for('auth.login'))

    return render_template("profile.html", user=user)


@app.route('/logout')
def logout():
    """Выход из системы"""
    session.clear()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('main'))




@app.route('/task')
def task_info():
    """Задания по информатике"""
    if 'user_id' not in session:
        flash('Пожалуйста, войдите в систему', 'warning')
        return redirect(url_for('auth.login'))
    return render_template('task.html', tasks=tasks_info, subject='Информатика')


@app.route('/task/math')
def task_math():
    """Задания по математике"""
    if 'user_id' not in session:
        flash('Пожалуйста, войдите в систему', 'warning')
        return redirect(url_for('auth.login'))
    return render_template('task_math_oge.html', tasks=tasks_math, subject='Математика')


@app.route('/task/submit', methods=['POST'])
def task_submit():
    """Обработка результатов тестирования"""
    if 'user_id' not in session:
        flash('Пожалуйста, войдите в систему', 'warning')
        return redirect(url_for('auth.login'))

    subject = request.form.get('subject', 'Информатика')
    tasks = tasks_math if subject == 'Математика' else tasks_info

    correct = 0
    total = len(tasks)
    results = []

    for t in tasks:
        user_answer = request.form.get(f't{t["id"]}', '').strip()
        correct_answer = str(t['answer']).strip()
        is_correct = user_answer.lower() == correct_answer.lower()

        if is_correct:
            correct += 1

        results.append({
            'id': t['id'],
            'question': t['question'][:100] + '...' if len(t['question']) > 100 else t['question'],
            'user_answer': user_answer or '—',
            'correct_answer': correct_answer,
            'is_correct': is_correct
        })

    percent = round(correct / total * 100) if total > 0 else 0

    return render_template('result.html',
                           correct=correct,
                           total=total,
                           percent=percent,
                           results=results,
                           subject=subject)


if __name__ == '__main__':
    app.run(debug=True)