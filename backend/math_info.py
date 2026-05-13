from flask import Blueprint, render_template

math_th_bp = Blueprint('math_th', __name__, url_prefix='/theory/oge/math')


@math_th_bp.route('')
@math_th_bp.route('/')
def open_math_theory():
    return render_template('theory_math/math_main.html')


@math_th_bp.route('/numbers_and_calculations')
def numbers_and_calculations():
    return render_template('theory_math/math_nums.html')


@math_th_bp.route('/equalizations')
def equalizations():
    return render_template('theory_math/math_eq.html')


@math_th_bp.route('/plots')
def plots():
    return render_template('theory_math/math_plots.html')


@math_th_bp.route('/geometry')
def geometry():
    return render_template('theory_math/math_geometry.html')


@math_th_bp.route('/problems')
def problems():
    return render_template('theory_math/math_problems.html')
