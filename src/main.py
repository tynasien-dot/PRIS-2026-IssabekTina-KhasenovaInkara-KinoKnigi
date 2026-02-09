import streamlit as st
from mock_data import movies_data
from logic import check_rules      # функция проверки правил

# Настройка страницы
st.set_page_config(page_title="Movie Advisor", page_icon="🎬")
st.title("Movie Rule-Based System 🎬")
st.write("**Текущий сценарий:** Проверка по правилам проекта")

st.sidebar.header("Входные данные фильма")

# --- Выбор фильма из списка ---
selected_movie_title = st.sidebar.selectbox(
    "Выберите фильм",
    options=[m["title"] for m in movies_data]
)

# Берем данные выбранного фильма
default_data = next(m for m in movies_data if m["title"] == selected_movie_title)

# --- Поля ввода в боковой панели ---
title = st.sidebar.text_input("Название фильма:", value=default_data["title"])
imdb_score = st.sidebar.number_input(
    "IMDB Score:", 
    min_value=0.0, 
    max_value=10.0, 
    value=float(default_data["imdb_score"]),
    step=0.1
)
is_available = st.sidebar.checkbox("Доступность (Available)", value=default_data["is_available"])
sentiment = st.sidebar.selectbox(
    "Настроение отзывов:", 
    options=["positive", "negative"], 
    index=0 if default_data["review_sentiment"] == "positive" else 1
)
genres_input = st.sidebar.text_input(
    "Жанры (через запятую):", 
    value=", ".join(default_data["genres"])
)
genres = [g.strip() for g in genres_input.split(",") if g.strip()]

# --- Кнопка запуска проверки ---
if st.button("Запустить анализ по правилам"):
    current_movie_data = {
        "title": title,
        "rating_value": imdb_score,  # logic.py ждет именно rating_value
        "is_available": is_available,
        "review_sentiment": sentiment,
        "tags_list": genres          # logic.py ждет именно tags_list
    }
    
    result = check_rules(current_movie_data)
    
    if "✅" in result:
        st.success(result)
        st.balloons() 
    elif "⛔️" in result:
        st.error(result)
    else:
        st.warning(result)

# --- Отладочный вывод ---
with st.expander("Посмотреть структуру данных для анализа"):
    debug_data = {
        "title": title,
        "rating_value": imdb_score,
        "is_available": is_available,
        "review_sentiment": sentiment,
        "tags_list": genres
    }
    st.json(debug_data)