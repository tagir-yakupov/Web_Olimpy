from datetime import timedelta
from flask import Blueprint, session, redirect, url_for, request, render_template, flash, current_app, jsonify
import os
import re
from werkzeug.utils import secure_filename
from random import randint

conf_th = Blueprint('conf', __name__, url_prefix='/theory/oge')

@conf_th.route('/new', methods=['GET', 'POST'])
def conf():
    if session.get('user_name') != 'admin':
        flash('Доступ запрещен!', 'error')
        return redirect(url_for('main'))
    
    if request.method == 'POST':
        task_condition = request.form.get('task_condition')
        task_solution = request.form.get('task_solution')
        category = request.form.get('task_type')
        number = request.form.get('task_number')
        theme = request.form.get('task_theme')
        image_url = request.form.get('image_url', '')
        num = ''.join([str(randint(0, 9)) for _ in range(10)])
        
        image_html = ''
        if image_url:
            image_html = f'\n                <img src="{image_url}" class="img-fluid my-3" alt="Задача {number}">'
        
        solution_lines = task_solution.split('\r\n')
        task_html = f'''
            <div class="task-block p-4">
    <div class="d-flex align-items-center gap-3 mb-3 flex-wrap">
        <div class="task-number">Задача №{number}</div>
        <span class="badge-type"><i class="bi bi-bar-chart-steps me-1"></i>{category}</span>
    </div>
            <p class="fs-5 fw-semibold">{task_condition}</p>
    <div class="solution-toggle" onclick="toggleSolution('{num}')">
        <i class="bi bi-eye-fill me-1"></i> Показать решение
    </div>
            <div id="{num}" class="solution-content d-none">{image_html}'''
        for elem in solution_lines[:-1]:
            if elem.strip():
                task_html += f'\n                <p>{elem}</p>'
        task_html += f'\n                <p class="fw-bold text-success mt-2"><i class="bi bi-check-circle-fill"></i>{solution_lines[-1]}</p>\n            </div>\n</div>\n\n'
        
        file_path = f'templates/{theme}.html'
        
        # Проверяем, существует ли файл
        if not os.path.exists(file_path):
            flash(f'Ошибка: файл {theme}.html не найден!', 'error')
            return redirect(url_for('conf.conf'))
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        button_pattern = r'(<div class="mt-4 pt-3 border-top">\s*<a href="[^"]+" class="btn[^"]*">.*?(?:Вернуться|Назад|Вернуться ко всем темам).*?</a>\s*</div>)'
        
        match = re.search(button_pattern, content, re.DOTALL | re.IGNORECASE)
        
        if match:
            new_content = content[:match.start()] + task_html + content[match.start():]
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            flash('Теория успешно добавлена!', 'success')
        else:
            body_match = re.search(r'(.*?)(</body>)', content, re.DOTALL | re.IGNORECASE)
            if body_match:
                new_content = body_match.group(1) + task_html + body_match.group(2)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                flash('Теория успешно добавлена в конец страницы!', 'success')
            else:
                with open(file_path, 'a', encoding='utf-8') as f:
                    f.write(task_html)
                flash('Теория добавлена в конец файла!', 'success')
        
        return redirect(url_for('conf.conf'))
    
    return render_template('admin_panel/add_th.html')