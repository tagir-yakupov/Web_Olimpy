"""
WTForms для авторизации и регистрации
"""
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, EmailField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length


class RegisterForm(FlaskForm):
    """
    Форма регистрации нового пользователя
    """
    name = StringField('Имя пользователя', validators=[
        DataRequired(message='Введите имя'),
        Length(min=3, max=50, message='Имя от 3 до 50 символов')
    ])
    email = EmailField('Почта', validators=[
        DataRequired(message='Введите email'),
        Email(message='Некорректный email')
    ])
    password = PasswordField('Пароль', validators=[
        DataRequired(message='Введите пароль'),
        Length(min=6, message='Пароль минимум 6 символов')
    ])
    password_again = PasswordField('Повторите пароль', validators=[
        DataRequired(message='Повторите пароль'),
        EqualTo('password', message='Пароли не совпадают')
    ])
    about = TextAreaField('О себе', validators=[])
    submit = SubmitField('Зарегистрироваться')


class LoginForm(FlaskForm):
    """
    Форма входа пользователя
    """
    username = StringField('Логин или email', validators=[
        DataRequired(message='Введите логин или email')
    ])
    password = PasswordField('Пароль', validators=[
        DataRequired(message='Введите пароль')
    ])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')