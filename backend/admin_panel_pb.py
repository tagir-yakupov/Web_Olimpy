from datetime import timedelta
from flask import Blueprint, session, redirect, url_for, request, render_template, flash, current_app, jsonify
import os
import re
from werkzeug.utils import secure_filename
from random import randint
import json
from io import BytesIO

conf_pb = Blueprint('prob_conf', __name__, url_prefix='/task')
@conf_pb.route('/newtask', methods=['GET', 'POST'])
def new_prob():
    if session.get('user_name') != 'admin':
        flash('Доступ запрещен!', 'error')
        return redirect(url_for('main'))
    
    if request.method == 'POST':
        cond = request.form.get('condition')
        ans = request.form.get('answer')
        number = request.form.get('id')
        category = request.form.get('category')
        image_file = request.files.get('image')
        image_path = None
        if image_file and image_file.filename:
            filename = f'image_{category}_{number}_{randint(1,1000)}.png'
            with open(f'static/uploads/{filename}', 'wb') as f:
                f.write(image_file.read())
        json_path = f'data/task_{category}.json'
        tasks = None
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                tasks = json.load(f)
                if not isinstance(tasks, list):
                    tasks = [tasks]
        if any(task.get('id') == number for task in tasks):
            flash('Задача с таким ID уже существует!', 'error')
            return redirect(url_for('prob_conf.new_prob'))
        new_task = {
            'id': number,
            'question': cond,
            'image': f'/static/uploads/{filename}',
            'answer': ans
        }
        tasks[0]['questions'].append(new_task)
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(tasks[0], f)
        
        flash('Задача успешно добавлена!', 'success')
        return redirect(url_for('prob_conf.new_prob'))
    
    return render_template('admin_panel/add_pb.html')