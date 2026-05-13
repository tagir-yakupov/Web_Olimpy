"""
Модуль для загрузки и генерации заданий
"""
import json
import os
import random

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


def _load_json(path: str) -> list:
    """Вспомогательная функция для загрузки JSON"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('questions', [])
    except FileNotFoundError:
        print(f"Файл {path} не найден")
        return []
    except json.JSONDecodeError as e:
        print(f"Ошибка JSON в {path}: {e}")
        return []
    except Exception as e:
        print(f"Ошибка загрузки: {e}")
        return []


def _filter_and_sort_tasks(tasks: list, difficulty: int = None, topic: str = None, sort_by: str = 'id') -> list:
    """
    Фильтрация и сортировка заданий

    Args:
        tasks: Список заданий
        difficulty: Уровень сложности (1, 2, 3) или None
        topic: Название темы или None
        sort_by: 'id', 'difficulty', 'topic'

    Returns:
        Отфильтрованный и отсортированный список
    """
    # Фильтрация
    if difficulty is not None:
        tasks = [t for t in tasks if t.get('difficulty') == difficulty]

    if topic:
        tasks = [t for t in tasks if topic.lower() in t.get('topic', '').lower()]

    # Сортировка
    if sort_by == 'difficulty':
        tasks = sorted(tasks, key=lambda x: (x.get('difficulty', 9), x.get('id', 999)))
    elif sort_by == 'topic':
        tasks = sorted(tasks, key=lambda x: (x.get('topic', ''), x.get('id', 999)))
    else:
        tasks = sorted(tasks, key=lambda x: x.get('id', 999))

    return tasks


def load_tasks(difficulty: int = None, topic: str = None, sort_by: str = 'id'):
    """Загружает задания по информатике с фильтрацией"""
    tasks = _load_json(os.path.join(ROOT_DIR, 'data', 'task.json'))
    return _filter_and_sort_tasks(tasks, difficulty, topic, sort_by)


def load_math_oge(difficulty: int = None, topic: str = None, sort_by: str = 'id'):
    """Загружает задания по математике с фильтрацией"""
    tasks = _load_json(os.path.join(ROOT_DIR, 'data', 'task_math_oge.json'))
    return _filter_and_sort_tasks(tasks, difficulty, topic, sort_by)


def get_available_topics(subject: str = 'informatics') -> list:
    """Возвращает список доступных тем"""
    path = os.path.join(ROOT_DIR, 'data',
                        'task.json' if subject == 'informatics' else 'task_math_oge.json')
    tasks = _load_json(path)
    topics = list(set(t.get('topic', 'Без темы') for t in tasks if t.get('topic')))
    return sorted(topics)


def generate_variant(subject: str,
                     total_tasks: int = 10,
                     difficulty_distribution: dict = None,
                     topics: list = None,
                     exclude_ids: list = None) -> list:
    """Генерирует персонализированный вариант заданий"""
    all_tasks = _load_json(os.path.join(ROOT_DIR, 'data',
                                        'task.json' if subject == 'informatics' else 'task_math_oge.json'))

    if topics:
        all_tasks = [t for t in all_tasks if t.get('topic') in topics]

    if exclude_ids:
        all_tasks = [t for t in all_tasks if t['id'] not in exclude_ids]

    if len(all_tasks) <= total_tasks:
        return random.sample(all_tasks, len(all_tasks))

    if difficulty_distribution is None:
        difficulty_distribution = {
            1: int(total_tasks * 0.3),
            2: int(total_tasks * 0.4),
            3: total_tasks - int(total_tasks * 0.3) - int(total_tasks * 0.4)
        }

    variant = []

    for difficulty, count in difficulty_distribution.items():
        if count <= 0:
            continue
        available = [t for t in all_tasks if t.get('difficulty') == difficulty and t not in variant]
        selected = random.sample(available, min(count, len(available)))
        variant.extend(selected)

    if len(variant) < total_tasks:
        remaining = total_tasks - len(variant)
        available = [t for t in all_tasks if t not in variant]
        variant.extend(random.sample(available, min(remaining, len(available))))

    random.shuffle(variant)
    return variant[:total_tasks]


def get_variant_stats(tasks: list) -> dict:
    """Возвращает статистику по варианту"""
    stats = {
        'total': len(tasks),
        'by_difficulty': {1: 0, 2: 0, 3: 0},
        'by_topic': {},
        'estimated_time': 0
    }

    for t in tasks:
        diff = t.get('difficulty', 2)
        stats['by_difficulty'][diff] = stats['by_difficulty'].get(diff, 0) + 1

        topic = t.get('topic', 'Без темы')
        stats['by_topic'][topic] = stats['by_topic'].get(topic, 0) + 1

        stats['estimated_time'] += diff * 60

    return stats