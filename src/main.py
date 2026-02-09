# Настройка страницы
st.set_page_config(page_title="Movie Advisor", page_icon="🎬")
st.title("Movie Rule-Based System 🎬")
st.write(f"**Текущий сценарий:** Проверка по правилам проекта")

st.sidebar.header("Входные данные фильма")

# Поля ввода в боковой панели
title = st.sidebar.text_input("Название фильма:", value=default_data["title"])

# ВАЖНО: берем данные из mock_data по их старым ключам для дефолтных значений
imdb_score = st.sidebar.number_input(
    "IMDB Score:", 
    min_value=0.0, 
    max_value=10.0, 
    value=float(default_data["imdb_score"]),
    step=0.1
)
is_available = st.sidebar.checkbox("Доступность (Available)", value=default_data["is_available"])

# Выбор настроения
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
    # СОБИРАЕМ ДАННЫЕ: переименовываем ключи под logic.py
    current_movie_data = {
        "title": title,
        "rating_value": imdb_score,  # logic.py ждет именно rating_value
        "is_available": is_available,
        "review_sentiment": sentiment,
        "tags_list": genres          # logic.py ждет именно tags_list
    }
    
    # Вызываем логику
    result = check_rules(current_movie_data)
    
    # Красивый вывод результата
    if "✅" in result:
        st.success(result)
        st.balloons() 
    elif "⛔️" in result:
        st.error(result)
    else:
        st.warning(result)

# Отображение данных для отладки
with st.expander("Посмотреть структуру данных для анализа"):
    # Показываем финальный словарь, который уходит в логику
    debug_data = {
        "title": title,
        "rating_value": imdb_score,
        "is_available": is_available,
        "review_sentiment": sentiment,
        "tags_list": genres
    }
    st.json(debug_data)