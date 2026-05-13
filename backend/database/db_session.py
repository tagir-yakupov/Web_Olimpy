"""
Модуль для работы с базой данных SQLAlchemy
"""
import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session

SqlAlchemyBase = orm.declarative_base()

__factory = None


def global_init(db_file: str):
    """
    Инициализация подключения к базе данных

    Args:
        db_file: Путь к файлу базы данных SQLite
    """
    global __factory

    if __factory:
        return

    if not db_file or not db_file.strip():
        raise Exception("Необходимо указать файл базы данных.")

    conn_str = f'sqlite:///{db_file.strip()}?check_same_thread=False'
    print(f"Подключение к базе данных по адресу {conn_str}")

    engine = sa.create_engine(conn_str, echo=False)
    __factory = orm.sessionmaker(bind=engine)

    # Импортируем все модели для регистрации метаданных

    SqlAlchemyBase.metadata.create_all(engine)


def create_session() -> Session:
    """
    Создание новой сессии базы данных

    Returns:
        Session: Объект сессии SQLAlchemy
    """
    global __factory
    return __factory()