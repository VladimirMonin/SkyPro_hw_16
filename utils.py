import json
from datetime import datetime

def get_json(filename):
    """Возвращает данные из Json"""
    with open(filename, encoding='utf-8') as file:
        return json.load(file)


