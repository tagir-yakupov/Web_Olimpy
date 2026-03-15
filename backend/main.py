from flask import Flask, session, redirect, url_for, request, render_template
from registry import auth_bp, load_users, save_users
from parse1 import load_tasks

app = Flask(__name__, template_folder='templates')
app.secret_key = 'ключ'

load_users()
app.register_blueprint(auth_bp)

tasks = load_tasks()


@app.route('/')
@app.route('/main')
def main():
    user = session.get('user')
    return render_template("main_page.html", title="Главная страница", user=user)


@app.route('/profile')
def profile():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template("profile.html", user=session['user'])


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('main'))


@app.route('/task')
def task():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('task.html', tasks=tasks)


@app.route('/task/submit', methods=['POST'])
def task_submit():
    if 'user' not in session:
        return redirect(url_for('login'))

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
            'user_answer': user_answer,
            'correct_answer': correct_answer,
            'is_correct': is_correct
        })

    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Результат</title>
        <style>
            * {{ box-sizing: border-box; }}
            body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; background: #f4f4f4; }}
            .navbar {{ background: #333; padding: 15px 20px; }}
            .navbar a {{ color: white; text-decoration: none; padding: 10px 15px; border-radius: 4px; margin-right: 10px; }}
            .navbar a:hover {{ background: #555; }}
            .container {{ max-width: 800px; margin: 30px auto; padding: 30px; background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .score {{ font-size: 32px; font-weight: bold; color: #27ae60; text-align: center; padding: 20px; background: #e8f8f5; border-radius: 8px; margin-bottom: 30px; }}
            .task-result {{ background: #f9f9f9; padding: 15px; margin: 15px 0; border-radius: 8px; border-left: 4px solid #ddd; }}
            .task-result.correct {{ border-left-color: #27ae60; }}
            .task-result.wrong {{ border-left-color: #c0392b; }}
            .btn {{ display: inline-block; padding: 12px 25px; background: #3498db; color: white; text-decoration: none; border-radius: 4px; margin: 5px; }}
            .btn:hover {{ background: #2980b9; }}
            .center {{ text-align: center; }}
        </style>
    </head>
    <body>
        <div class="navbar">
            <a href="/">Главная</a>
            <a href="/task">Задания</a>
            <a href="/profile">Профиль</a>
        </div>
        <div class="container">
            <h1>Результат тестирования</h1>
            <div class="score">{correct} из {total} ({round(correct / total * 100)}%)</div>
            <h2>Разбор заданий:</h2>
    '''

    for r in results:
        status = 'Все правильно' if r['is_correct'] else 'К сожалению, неверно'
        css_class = 'correct' if r['is_correct'] else 'wrong'
        html += f'''
            <div class="task-result {css_class}">
                <p><b>Задание №{r['id']}</b> {status}</p>
                <p>Ваш ответ: {r['user_answer']}</p>
                <p>Правильный ответ: {r['correct_answer']}</p>
            </div>
        '''

    html += f'''
            <div class="center">
                <a href="/task" class="btn">Пройти ещё</a>
                <a href="/" class="btn" style="background:#95a5a6;">На главную страницу</a>
            </div>
        </div>
    </body>
    </html>
    '''

    return html


import atexit


@atexit.register
def on_exit():
    save_users()


if __name__ == '__main__':
    app.run(debug=True)