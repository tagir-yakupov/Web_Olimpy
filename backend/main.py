import os
import sys
import random
from datetime import datetime, timedelta
from flask import Flask, session, redirect, url_for, request, render_template, flash, jsonify

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT_DIR)

if os.path.exists(os.path.join(os.path.dirname(__file__), 'backend')):
    ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
    sys.path.insert(0, ROOT_DIR)

from backend.registry import auth_bp
from backend.math_info import math_th_bp
from backend.admin_panel_th import conf_th
from backend.admin_panel_pb import conf_pb
from backend.parse1 import load_tasks, load_math_oge
from backend.database.db_session import global_init, create_session
from backend.database.models import UserModel
from backend.chat import chatt
from backend.rus_info import rus_th

DB_DIR = os.path.join(ROOT_DIR, 'data')
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = os.path.join(DB_DIR, 'users.db')
global_init(DB_PATH)

app = Flask(__name__,
            template_folder=os.path.join(ROOT_DIR, 'templates'),
            static_folder=os.path.join(ROOT_DIR, 'static'))
app.secret_key = 'замените_на_случайный_ключ_минимум_32_символа'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

app.register_blueprint(auth_bp)
app.register_blueprint(math_th_bp)
app.register_blueprint(conf_th)
app.register_blueprint(conf_pb)
app.register_blueprint(chatt)
app.register_blueprint(rus_th)

ALL_TASKS_INFO = load_tasks()
ALL_TASKS_MATH = load_math_oge()

def _filter_and_sort_tasks(tasks: list, difficulty: int = None, topic: str = None, sort_by: str = 'id') -> list:
    if difficulty is not None:
        tasks = [t for t in tasks if t.get('difficulty') == difficulty]
    if topic:
        tasks = [t for t in tasks if topic.lower() in t.get('topic', '').lower()]

    if sort_by == 'difficulty':
        tasks = sorted(tasks, key=lambda x: (x.get('difficulty', 9), x.get('id', 999)))
    elif sort_by == 'topic':
        tasks = sorted(tasks, key=lambda x: (x.get('topic', ''), x.get('id', 999)))
    else:
        tasks = sorted(tasks, key=lambda x: x.get('id', 999))

    return tasks

def _get_available_topics(subject: str) -> list:
    tasks = ALL_TASKS_INFO if subject == 'informatics' else ALL_TASKS_MATH
    topics = list(set(t.get('topic', 'Без темы') for t in tasks if t.get('topic')))
    return sorted(topics)

def generate_variant(subject: str,
                     total_tasks: int = 10,
                     difficulty_distribution: dict = None,
                     topics: list = None,
                     exclude_ids: list = None) -> list:
    all_tasks = ALL_TASKS_INFO if subject == 'informatics' else ALL_TASKS_MATH

    if topics:
        all_tasks = [t for t in all_tasks if t.get('topic') in topics]

    if exclude_ids:
        all_tasks = [t for t in all_tasks if t['id'] not in exclude_ids]

    if len(all_tasks) <= total_tasks:
        return random.sample(all_tasks, len(all_tasks))

    if difficulty_distribution is None:
        difficulty_distribution = {
            1: int(total_tasks * 0.3),
            2: int(total_tasks * 0.4),
            3: total_tasks - int(total_tasks * 0.3) - int(total_tasks * 0.4)
        }

    variant = []

    for difficulty, count in difficulty_distribution.items():
        if count <= 0:
            continue
        available = [t for t in all_tasks if t.get('difficulty') == difficulty and t not in variant]
        selected = random.sample(available, min(count, len(available)))
        variant.extend(selected)

    if len(variant) < total_tasks:
        remaining = total_tasks - len(variant)
        available = [t for t in all_tasks if t not in variant]
        variant.extend(random.sample(available, min(remaining, len(available))))

    random.shuffle(variant)
    return variant[:total_tasks]

def get_variant_stats(tasks: list) -> dict:
    stats = {
        'total': len(tasks),
        'by_difficulty': {1: 0, 2: 0, 3: 0},
        'by_topic': {},
        'estimated_time': 0
    }

    for t in tasks:
        diff = t.get('difficulty', 2)
        stats['by_difficulty'][diff] = stats['by_difficulty'].get(diff, 0) + 1

        topic = t.get('topic', 'Без темы')
        stats['by_topic'][topic] = stats['by_topic'].get(topic, 0) + 1

        stats['estimated_time'] += diff * 60

    return stats

@app.route('/')
@app.route('/main')
def main():
    user_name = session.get('user_name')
    return render_template("main_page.html", title="Главная страница", user=user_name)

@app.route('/profile')
def profile():
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
    session.clear()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('main'))

@app.route('/task')
def task_info():
    if 'user_id' not in session:
        flash('Пожалуйста, войдите в систему', 'warning')
        return redirect(url_for('auth.login'))

    difficulty = request.args.get('difficulty', type=int)
    topic = request.args.get('topic', type=str)
    sort_by = request.args.get('sort', default='id', type=str)

    tasks = _filter_and_sort_tasks(ALL_TASKS_INFO, difficulty, topic, sort_by)
    topics = _get_available_topics('informatics')

    return render_template('task.html',
                           tasks=tasks,
                           subject='Информатика',
                           current_difficulty=difficulty,
                           current_topic=topic,
                           current_sort=sort_by,
                           available_topics=topics,
                           all_tasks_count=len(ALL_TASKS_INFO))

@app.route('/task/math')
def task_math():
    if 'user_id' not in session:
        flash('Пожалуйста, войдите в систему', 'warning')
        return redirect(url_for('auth.login'))

    difficulty = request.args.get('difficulty', type=int)
    topic = request.args.get('topic', type=str)
    sort_by = request.args.get('sort', default='id', type=str)

    tasks = _filter_and_sort_tasks(ALL_TASKS_MATH, difficulty, topic, sort_by)
    topics = _get_available_topics('math')

    return render_template('task_math_oge.html',
                           tasks=tasks,
                           subject='Математика',
                           current_difficulty=difficulty,
                           current_topic=topic,
                           current_sort=sort_by,
                           available_topics=topics,
                           all_tasks_count=len(ALL_TASKS_MATH))

@app.route('/task/submit', methods=['POST'])
def task_submit():
    if 'user_id' not in session:
        flash('Пожалуйста, войдите в систему', 'warning')
        return redirect(url_for('auth.login'))

    subject = request.form.get('subject', 'Информатика')
    tasks = ALL_TASKS_MATH if subject == 'Математика' else ALL_TASKS_INFO

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

@app.route('/generate')
def generate_variant_page():
    if 'user_id' not in session:
        flash('Пожалуйста, войдите в систему', 'warning')
        return redirect(url_for('auth.login'))

    return render_template('generate_variant.html',
                           title='Генератор вариантов',
                           subjects=[
                               {'id': 'informatics', 'name': 'Информатика'},
                               {'id': 'math', 'name': 'Математика'}
                           ],
                           difficulty_levels=[
                               {'id': 1, 'name': 'Легко', 'color': 'success', 'icon': '🟢'},
                               {'id': 2, 'name': 'Средне', 'color': 'warning', 'icon': '🟡'},
                               {'id': 3, 'name': 'Сложно', 'color': 'danger', 'icon': '🔴'}
                           ],
                           info_topics=_get_available_topics('informatics'),
                           math_topics=_get_available_topics('math'))

@app.route('/generate/create', methods=['POST'])
def create_variant():
    if 'user_id' not in session:
        return jsonify({'error': 'Требуется авторизация'}), 401

    data = request.json
    subject = data.get('subject', 'informatics')
    total_tasks = int(data.get('total_tasks', 10))

    difficulty_dist = {}
    for diff in [1, 2, 3]:
        count = int(data.get(f'difficulty_{diff}', 0))
        if count > 0:
            difficulty_dist[diff] = count

    topics = data.get('topics', [])

    tasks = generate_variant(
        subject=subject,
        total_tasks=total_tasks,
        difficulty_distribution=difficulty_dist if difficulty_dist else None,
        topics=topics if topics else None,
        exclude_ids=[]
    )

    session[f'variant_{subject}'] = {
        'tasks': tasks,
        'created_at': datetime.now().isoformat(),
        'settings': data
    }

    stats = get_variant_stats(tasks)

    return jsonify({
        'success': True,
        'variant_id': f"{subject}_{int(datetime.now().timestamp())}",
        'tasks': tasks,
        'stats': stats,
        'subject_display': 'Информатика' if subject == 'informatics' else 'Математика'
    })

@app.route('/generate/take/<subject>')
def take_variant(subject: str):
    if 'user_id' not in session:
        flash('Пожалуйста, войдите в систему', 'warning')
        return redirect(url_for('auth.login'))

    variant_key = f'variant_{subject}'
    if variant_key not in session:
        flash('Вариант не найден. Создайте новый.', 'warning')
        return redirect(url_for('generate_variant_page'))

    variant = session[variant_key]
    tasks = variant.get('tasks', [])

    return render_template('task_variant.html',
                           tasks=tasks,
                           subject='Информатика' if subject == 'informatics' else 'Математика',
                           variant_id=variant_key,
                           stats=get_variant_stats(tasks))

@app.route('/generate/variant/submit', methods=['POST'])
def submit_variant():
    if 'user_id' not in session:
        flash('Пожалуйста, войдите в систему', 'warning')
        return redirect(url_for('auth.login'))

    subject_param = request.form.get('subject_param', 'informatics')
    variant_key = f'variant_{subject_param}'

    if variant_key not in session:
        flash('Вариант истёк. Создайте новый.', 'warning')
        return redirect(url_for('generate_variant_page'))

    variant = session[variant_key]
    tasks = variant.get('tasks', [])
    subject_display = 'Информатика' if subject_param == 'informatics' else 'Математика'

    correct = 0
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

    percent = round(correct / len(tasks) * 100) if tasks else 0

    session.pop(variant_key, None)

    return render_template('result.html',
                           correct=correct,
                           total=len(tasks),
                           percent=percent,
                           results=results,
                           subject=subject_display,
                           is_variant=True)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)