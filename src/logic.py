import json
import os
import requests
import streamlit as st
import re

@st.cache_data(ttl=86400)
def get_movie_details(movie_title, movie_year=None):
    """Ищет фильм в TMDB и возвращает постер и краткое описание (overview)."""
    try:
        api_key = st.secrets["TMDB_API_KEY"]
    except KeyError:
        return {
            "poster": "https://via.placeholder.com/500x750.png?text=API+Key+Missing", 
            "overview": "Ключ API не найден в secrets.toml."
        }

    base_url = "https://api.themoviedb.org/3/search/movie"
    
    # Очищаем название от года в скобках для точного поиска
    clean_title = re.sub(r'\(\d{4}\)', '', str(movie_title)).strip()
    
    params = {
        "api_key": api_key,
        "query": clean_title,
        "language": "ru-RU"
    }
    
    if movie_year:
        params["year"] = str(movie_year)
    
    try:
        response = requests.get(base_url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        if data.get("results"):
            movie_info = data["results"][0]
            poster_path = movie_info.get("poster_path")
            overview = movie_info.get("overview")
            
            return {
                "poster": f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else "https://via.placeholder.com/500x750.png?text=No+Poster",
                "overview": overview if overview else "Описание на русском языке пока отсутствует."
            }
    except Exception as e:
        print(f"Ошибка API для '{clean_title}': {e}")
        
    return {
        "poster": "https://via.placeholder.com/500x750.png?text=Error", 
        "overview": "Не удалось загрузить описание фильма."
    }

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RULES_PATH = os.path.join(BASE_DIR, 'data', 'raw', 'rules.json')

def load_rules():
    if not os.path.exists(RULES_PATH):
        return {
            "scenario_name": "Default",
            "thresholds": {"min_rating": 1.0, "max_rating": 10.0},
            "lists": {"blacklist": []}
        }
    with open(RULES_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def check_rules(movie_dict):
    rules = load_rules()
    rating = movie_dict.get('imdb_score', 0)
    if rating < rules['thresholds']['min_rating']:
        return f"Рейтинг ({rating}) ниже допустимого"
    
    movie_genres = movie_dict.get('genres', [])
    for genre in movie_genres:
        if genre in rules['lists']['blacklist']:
            return f"Жанр '{genre}' запрещен правилами"
    return "Соответствует"

def process_text_message(text, graph, movies_list):
    query = text.lower().strip()
    if query in ["привет", "старт", "hi", "hello"]:
        return ("Салем! Я твой киносоветчик. 🎬\n\n"
                "Ты можешь:\n"
                "Написать жанр (например: 'Drama')\n"
                "Написать год (например: '1995')\n"
                "Написать слово из сюжета (например: 'adventure')")

    for node in graph.nodes:
        if query == node.lower():
            neighbors = list(graph.neighbors(node))
            return f"В базе знаний '{node}' найден в фильмах: {', '.join(neighbors[:7])}"

    found_titles = []
    for m in movies_list:
        if query in m.get('description', '').lower() or query in m['title'].lower():
            found_titles.append(m['title'])
    
    if found_titles:
        return f"По вашему описанию подобрал: {', '.join(found_titles[:5])}"

    return "Не совсем понял. Попробуй ввести жанр, год или ключевое слово (например, 'Animation')."

def apply_production_model(movie):
    score = movie.get('imdb_score', 0)
    genres = movie.get('genres', [])
    year = int(movie.get('year', 0))
    
    if score >= 8.0 and year < 2005:
        return "🏆 Это культовая классика, проверенная временем."
    if score >= 8.0 and year >= 2015:
        return "🔥 Современный блокбастер с высочайшим одобрением зрителей."
    if "Animation" in genres and score >= 8.0:
        return "🎨 Эталонная анимация, рекомендованная всем возрастам."
    if "Drama" in genres and score >= 7.8:
        return "🎭 Серьезная психологическая работа для вдумчивого просмотра."
    
    return "✅ Качественный контент, прошедший фильтрацию по рейтингу 7.5+."