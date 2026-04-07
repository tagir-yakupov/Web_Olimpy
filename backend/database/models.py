"""
Модели базы данных SQLAlchemy
"""
import datetime
import sqlalchemy
from sqlalchemy import orm
from werkzeug.security import generate_password_hash, check_password_hash

from backend.database.db_session import SqlAlchemyBase


class UserModel(SqlAlchemyBase):
    """
    Модель пользователя

    Таблица: users
    """
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False, unique=True, index=True)
    about = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    email = sqlalchemy.Column(sqlalchemy.String, index=True, unique=True, nullable=False)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)

    def set_password(self, password: str):
        """
        Хеширует и устанавливает пароль

        Args:
            password: Пароль в открытом виде
        """
        # 🔧 ИСПРАВЛЕНО: используем pbkdf2 вместо scrypt для совместимости
        self.hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password: str) -> bool:
        """
        Проверяет пароль

        Args:
            password: Пароль для проверки

        Returns:
            bool: True если пароль верный
        """
        return check_password_hash(self.hashed_password, password)

    @property
    def avatar(self) -> str:
        """
        Возвращает URL аватара с инициалами

        Returns:
            str: URL изображения аватара
        """
        initials = (self.name or 'U')[0].upper()
        return f"https://ui-avatars.com/api/?name={initials}&background=5a8f5a&color=fff&size=128"

    def __repr__(self):
        return f"<User {self.name} ({self.email})>"