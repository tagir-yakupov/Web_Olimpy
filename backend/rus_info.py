"""
Blueprint для теории по математике ОГЭ
"""
from flask import Blueprint, render_template

rus_th = Blueprint('rus_th', __name__, url_prefix='/theory/oge/rus')


@rus_th.route('')
@rus_th.route('/')
def open_math_theory():
    return render_template('theory_rus/rus_main.html')

@rus_th.route('/morphemics')
def morphemics():
    return render_template('theory_rus/rus_morph.html')

@rus_th.route('/spelling')
def spelling():
    return render_template('theory_rus/rus_orph.html')

@rus_th.route('/syntax')
def syntax():
    return render_template('theory_rus/rus_syn.html')

@rus_th.route('/morphology')
def morphology():
    return render_template('theory_rus/rus_morph1.html')

@rus_th.route('/punctuation')
def punctuation():
    return render_template('theory_rus/rus_punc.html')

@rus_th.route('/essay')
def essay():
    return render_template('theory_rus/rus_ess.html')

@rus_th.route('/summary')
def summary():
    return render_template('theory_rus/rus_izl.html')

