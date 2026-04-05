'''Здесь будет про материалы для подготовки'''

import os
import json
from flask import Blueprint, session, redirect, url_for, request, render_template

th_bp = Blueprint('math_th', __name__, url_prefix='')
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
USERS_FILE = os.path.join(ROOT_DIR, 'data', 'users.json')

@th_bp.route('/theory/oge/math')
def open_math_theory():
    return render_template('templates/math_th.html')
