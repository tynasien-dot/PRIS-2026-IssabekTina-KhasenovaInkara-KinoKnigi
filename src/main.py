import streamlit as st
from mock_data import test_entity as default_data
from logic import check_rules

# Настройка страницы
st.set_page_config(page_title="Movie Advisor", page_icon="🎬")
st.title("Movie Rule-Based System 🎬")
st.write(f"**Текущий сценарий:** Проверка по правилам проекта")

st.sidebar.header("Входные данные фильма")

# Поля ввода в боковой панели
title = st.sidebar.text_input("Название фильма:", value=default_data["title"])
imdb_score = st.sidebar.number_input(
    "IMDB Score:", 
    min_value=0.0, 
    max_value=10.0, 
    value=float(default_data["imdb_score"]),
    step=0.1
)
is_available = st.sidebar.checkbox("Доступность (Available)", value=default_data["is_available"])

# Выбор настроения (для critical_rules в JSON)
sentiment = st.sidebar.selectbox(
    "Настроение отзывов:", 
    options=["positive", "negative"], 
    index=0 if default_data["review_sentiment"] == "positive" else 1
)

# Ввод жанров
genres_input = st.sidebar.text_input(
    "Жанры (через запятую):", 
    value=", ".join(default_data["genres"])
)
genres = [g.strip() for g in genres_input.split(",") if g.strip()]

# Кнопка запуска проверки
if st.button("Запустить анализ по правилам"):
    # Собираем данные в один словарь (ключи должны совпадать с logic.py)
    current_movie_data = {
        "title": title,
        "imdb_score": imdb_score,
        "is_available": is_available,
        "review_sentiment": sentiment,
        "genres": genres
    }
    
    # Вызываем логику
    result = check_rules(current_movie_data)
    
    # Красивый вывод результата
    if "✅" in result:
        st.success(result)
        st.balloons() # Маленький эффект успеха
    elif "⛔️" in result:
        st.error(result)
    else:
        st.warning(result)

# Отображение сырых данных для отладки
with st.expander("Посмотреть JSON текущего фильма"):
    st.json(current_movie_data if 'current_movie_data' in locals() else default_data)