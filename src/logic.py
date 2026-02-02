import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RULES_PATH = os.path.join(BASE_DIR, 'data', 'raw', 'rules.json')

def load_rules():
    with open(RULES_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def check_rules(data):
    rules = load_rules()
    
    # --- Hard Filter: проверка доступности ---
    if rules['critical_rules']['must_be_available'] and not data['is_available']:
        return "⛔️ Критическая ошибка: Книга/фильм недоступен"

    # --- Проверка рейтинга ---
    if data['rating_value'] < rules['thresholds']['min_rating']:
        return f"❌ Отказ: Рейтинг ({data['rating_value']}) ниже допустимого порога"
    
    if data['rating_value'] > rules['thresholds']['max_rating']:
        return f"❌ Отказ: Рейтинг ({data['rating_value']}) выше допустимого порога"

    # --- Проверка тегов (Blacklist) ---
    for tag in data['tags_list']:
        if tag in rules['lists']['blacklist']:
            return f"⚠️ Предупреждение: Найден запрещенный тег ({tag})"
    
    # --- Всё прошло ---
    return f"✅ Успех: Объект соответствует сценарию '{rules['scenario_name']}'"
