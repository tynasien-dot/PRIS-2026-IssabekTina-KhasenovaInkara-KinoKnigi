import json
import os
import requests
import streamlit as st
import re
import random

@st.cache_data(ttl=86400)
def get_movie_details(movie_title, movie_year=None):
    """Ищет фильм в TMDB и возвращает постер и краткое описание."""
    try:
        api_key = st.secrets["TMDB_API_KEY"]
    except KeyError:
        return {
            "poster": "https://via.placeholder.com/500x750.png?text=API+Key+Missing", 
            "overview": "Ключ API не найден в secrets.toml."
        }

    base_url = "https://api.themoviedb.org/3/search/movie"
    clean_title = re.sub(r'\(\d{4}\)', '', str(movie_title)).strip()
    
    params = {"api_key": api_key, "query": clean_title, "language": "ru-RU"}
    if movie_year:
        params["year"] = str(movie_year)
    
    try:
        response = requests.get(base_url, params=params, timeout=5)
        data = response.json()
        if data.get("results"):
            movie_info = data["results"][0]
            path = movie_info.get("poster_path")
            return {
                "poster": f"https://image.tmdb.org/t/p/w500{path}" if path else "https://via.placeholder.com/500x750.png?text=No+Poster",
                "overview": movie_info.get("overview", "Описание на русском языке пока отсутствует.")
            }
    except Exception:
        pass
        
    return {
        "poster": "https://via.placeholder.com/500x750.png?text=Error", 
        "overview": "Не удалось загрузить описание фильма."
    }

def load_rules():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    RULES_PATH = os.path.join(BASE_DIR, 'data', 'raw', 'rules.json')
    if not os.path.exists(RULES_PATH):
        return {"thresholds": {"min_rating": 1.0}, "lists": {"blacklist": []}}
    with open(RULES_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def check_rules(movie_dict):
    rules = load_rules()
    rating = movie_dict.get('imdb_score', 0)
    if rating < rules['thresholds']['min_rating']:
        return f"Рейтинг ({rating}) ниже допустимого"
    return "Соответствует"

def process_text_message(text, graph, movies_list):
    query = text.lower().strip()
    
    # НОВОЕ ПОЛНОЕ ПРИВЕТСТВИЕ (Без имени)
    if query in ["привет", "старт", "hi", "hello", "/start"]:
        return ("Салем! Я твой интеллектуальный киносоветчик. 🎬\n\n"
                "**Чем я могу быть полезен?**\n"
                "1. **Поиск и рекомендации:** Напиши жанр (например, 'Drama'), год или ключевое слово из сюжета, и я подберу лучшие варианты.\n"
                "2. **Компьютерное зрение:** Я умею определять жанр по постеру! Просто загрузи картинку в чат, и я проанализирую её.\n"
                "3. **База знаний:** Я использую граф связей, чтобы находить скрытые зависимости между фильмами.\n\n"
                "🎲 **Нет идей? Жми на кнопку с кубиком рядом со строкой ввода, и я выберу случайный фильм для тебя!**")

    # ЛОГИКА ДЛЯ КНОПКИ "МНЕ ПОВЕЗЕТ"
    if query == "мне повезет":
        random_movie = random.choice(movies_list)
        return f"🎲 Судьба выбрала для тебя фильм: **{random_movie['title']}**"

    # ПОИСК ПО ГРАФУ
    for node in graph.nodes:
        if query == node.lower():
            neighbors = list(graph.neighbors(node))
            return f"В базе знаний '{node}' найден в фильмах: {', '.join(neighbors[:7])}"

    # ПОИСК ПО ТЕКСТУ
    found_titles = []
    for m in movies_list:
        if query in m.get('description', '').lower() or query in m['title'].lower():
            found_titles.append(m['title'])
    
    if found_titles:
        return f"На основе твоего запроса рекомендую: {', '.join(found_titles[:5])}"

    return "Не совсем понял запрос. Попробуй ввести жанр, год или просто нажми на кубик! ✨"

def apply_production_model(movie):
    score = movie.get('imdb_score', 0)
    genres = movie.get('genres', [])
    year = int(movie.get('year', 0))
    
    if score >= 8.0 and year < 2005:
        return "🏆 Это культовая классика, проверенная временем."
    
    if "Animation" in genres and score >= 8.0: # <--- ПРОВЕРЬ ТУТ ЖАНР
        return "🎨 Эталонна анимация, рекомендованная всем возрастам."
    
    if "Drama" in genres and score >= 7.8:
        return "🎭 Серьезная психологическая работа."
    
    return "✅ Качественный контент, прошедший фильтрацию."