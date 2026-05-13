"""
Blueprint для авторизации и регистрации пользователей
"""
from datetime import timedelta
from flask import Blueprint, session, redirect, url_for, request, render_template, flash, current_app, jsonify
from sqlalchemy import or_

from backend.database.db_session import create_session
from backend.database.models import UserModel
from backend.database.forms import RegisterForm, LoginForm

auth_bp = Blueprint('auth', __name__, url_prefix='')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Регистрация нового пользователя"""
    form = RegisterForm()

    if form.validate_on_submit():
        # Проверка совпадения паролей
        if form.password.data != form.password_again.data:
            flash('Пароли не совпадают', 'danger')
            return render_template('auth.html', page_type='register', form=form)

        db_session = create_session()

        try:
            # Проверка email (уникальный)
            if db_session.query(UserModel).filter(
                UserModel.email == form.email.data.strip().lower()
            ).first():
                flash('Пользователь с таким email уже зарегистрирован', 'danger')
                return render_template('auth.html', page_type='register', form=form)

            # Проверка имени (уникальное)
            if db_session.query(UserModel).filter(
                UserModel.name == form.name.data.strip()
            ).first():
                flash('Пользователь с таким именем уже существует', 'danger')
                return render_template('auth.html', page_type='register', form=form)

            # Создание нового пользователя
            user = UserModel(
                name=form.name.data.strip(),
                email=form.email.data.strip().lower(),
                about=form.about.data.strip() if form.about.data else ''
            )
            user.set_password(form.password.data)

            db_session.add(user)
            db_session.commit()

            # Авторизация после регистрации
            session['user_id'] = user.id
            session['user_name'] = user.name
            session.permanent = True

            flash('Регистрация успешна! Добро пожаловать!', 'success')
            return redirect(url_for('main'))

        except Exception as e:
            db_session.rollback()
            flash(f'Ошибка регистрации: {str(e)}', 'danger')
            return render_template('auth.html', page_type='register', form=form)
        finally:
            db_session.close()

    return render_template('auth.html', page_type='register', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Вход пользователя"""
    form = LoginForm()

    if form.validate_on_submit():
        db_session = create_session()
        username_input = form.username.data.strip()

        try:
            # Поиск по имени ИЛИ email
            user = db_session.query(UserModel).filter(
                or_(
                    UserModel.name == username_input,
                    UserModel.email == username_input.lower()
                )
            ).first()

            if user and user.check_password(form.password.data):
                session['user_id'] = user.id
                session['user_name'] = user.name

                # "Запомнить меня"
                if form.remember_me.data:
                    session.permanent = True
                    current_app.permanent_session_lifetime = timedelta(days=30)
                else:
                    session.permanent = False

                flash(f'С возвращением, {user.name}!', 'success')
                return redirect(url_for('main'))
            else:
                flash('Неверный логин, email или пароль', 'danger')
                return render_template('auth.html', page_type='login', form=form)

        except Exception as e:
            flash(f'Ошибка входа: {str(e)}', 'danger')
            return render_template('auth.html', page_type='login', form=form)
        finally:
            db_session.close()

    return render_template('auth.html', page_type='login', form=form)


@auth_bp.route('/logout')
def logout():
    """Выход из системы"""
    user_name = session.pop('user_name', None)
    session.pop('user_id', None)
    session.clear()
    if user_name:
        flash(f'До свидания, {user_name}!', 'info')
    return redirect(url_for('main'))


@auth_bp.route('/check_username')
def check_username():
    """AJAX-проверка имени"""
    username = request.args.get('username', '').strip()
    if len(username) < 3:
        return jsonify({'available': False, 'message': 'Минимум 3 символа'})

    db_session = create_session()
    try:
        exists = db_session.query(UserModel).filter(UserModel.name == username).first() is not None
        return jsonify({'available': not exists, 'message': 'Имя занято' if exists else 'Доступно'})
    finally:
        db_session.close()


@auth_bp.route('/check_email')
def check_email():
    """AJAX-проверка email"""
    email = request.args.get('email', '').strip().lower()
    if '@' not in email:
        return jsonify({'available': False, 'message': 'Некорректный email'})

    db_session = create_session()
    try:
        exists = db_session.query(UserModel).filter(UserModel.email == email).first() is not None
        return jsonify({'available': not exists, 'message': 'Email занят' if exists else 'Доступно'})
    finally:
        db_session.close()