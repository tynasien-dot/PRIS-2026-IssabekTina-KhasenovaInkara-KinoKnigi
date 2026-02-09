import json
import os

# Автоматически находим путь к папке проекта
# __file__ - это путь к текущему файлу (logic.py)
# dirname(__file__) - это папка src
# dirname(dirname(...)) - это корень проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Формируем путь к rules.json так, чтобы он работал у всех
RULES_PATH = os.path.join(BASE_DIR, 'data', 'raw', 'rules.json')

def load_rules():
    # Проверяем, существует ли файл вообще, прежде чем открывать
    if not os.path.exists(RULES_PATH):
        raise FileNotFoundError(f"Файл не найден по пути: {RULES_PATH}. Проверь, что папка 'data/raw' существует!")
        
    with open(RULES_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def check_rules(data):
    try:
        rules = load_rules()
    except Exception as e:
        return f"❌ Ошибка загрузки правил: {str(e)}"
    
    # --- Hard Filter: проверка доступности ---
    if rules['critical_rules']['must_be_available'] and not data['is_available']:
        return "⛔️ Критическая ошибка: Объект недоступен"

    # --- Проверка рейтинга ---
    if data['rating_value'] < rules['thresholds']['min_rating']:
        return f"❌ Отказ: Рейтинг ({data['rating_value']}) ниже порога"
    
    if data['rating_value'] > rules['thresholds']['max_rating']:
        return f"❌ Отказ: Рейтинг ({data['rating_value']}) выше порога"

    # --- Проверка тегов (Blacklist) ---
    for tag in data['tags_list']:
        if tag in rules['lists']['blacklist']:
            return f"⚠️ Предупреждение: Запрещенный тег ({tag})"
    
    return f"✅ Успех: Соответствует сценарию '{rules['scenario_name']}'"