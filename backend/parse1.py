import json
import os
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_tasks():
    """Загружает задания по информатике из data/task.json"""
    path = os.path.join(ROOT_DIR, 'data', 'task.json')
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('questions', [])
    except FileNotFoundError:
        print(f"Файл {path} не найден, возвращаем пустой список")
        return []
    except json.JSONDecodeError as e:
        print(f"Ошибка JSON в {path}: {e}")
        return []
    except Exception as e:
        print(f"Ошибка загрузки заданий: {e}")
        return []


def load_math_oge():
    """Загружает задания по математике ОГЭ из data/task_math_oge.json"""
    path = os.path.join(ROOT_DIR, 'data', 'task_math_oge.json')
    try:
        with open(path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return data.get('questions', [])
    except FileNotFoundError:
        print(f"Файл {path} не найден, возвращаем пустой список")
        return []
    except json.JSONDecodeError as e:
        print(f"Ошибка JSON в {path}: {e}")
        return []
    except Exception as e:
        print(f"Ошибка загрузки заданий: {e}")
        return []