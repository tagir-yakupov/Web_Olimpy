import os
import sys
from flask import Flask, session, redirect, url_for, request, render_template
from backend.registry import auth_bp, load_users, save_users
from backend.parse1 import load_tasks, load_math_oge
import atexit

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__, template_folder=os.path.join(ROOT_DIR, 'templates'))
app.secret_key = 'ключ'

load_users()
app.register_blueprint(auth_bp)
tasks_info = load_tasks()
tasks_math = load_math_oge()


@app.route('/')
@app.route('/main')
def main():
    user = session.get('user')
    return render_template("main_page.html", title="Главная страница", user=user)


@app.route('/profile')
def profile():
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    return render_template("profile.html", user=session['user'])


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('main'))


@app.route('/task')
def task_info():
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    return render_template('task.html', tasks=tasks_info, subject='Информатика')


@app.route('/task/math')
def task_math():
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    return render_template('task_math_oge.html', tasks=tasks_math, subject='Математика')


@app.route('/task/submit', methods=['POST'])
def task_submit():
    if 'user' not in session:
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


@atexit.register
def on_exit():
    save_users()


if __name__ == '__main__':
    app.run(debug=True)
