import json, os


def load_tasks():
    path = os.path.join(os.path.dirname(__file__), 'task.json')
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data['questions']
    except Exception as e:
        print(f"Ошибка: {e}")
        return []
