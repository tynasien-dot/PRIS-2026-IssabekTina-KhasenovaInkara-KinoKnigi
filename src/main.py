import streamlit as st
from mock_data import test_entity as default_data
from logic import check_rules

st.title("Rule-Based System for Movies 🎬")
st.write("### Настройка входящих данных")

title = st.sidebar.text_input("Название фильма:", value=default_data["title"])
imdb_score = st.sidebar.number_input("IMDB Score:", value=default_data["imdb_score"])
is_available = st.sidebar.checkbox("Доступность", value=default_data["is_available"])
review_sentiment = st.sidebar.selectbox("Настроение отзыва:", ["positive", "negative"], index=0 if default_data["review_sentiment"]=="positive" else 1)

genres_input = st.sidebar.text_input("Жанры (через запятую):", value=", ".join(default_data["genres"]))
genres = [g.strip() for g in genres_input.split(",")]

if st.button("Проверить фильм"):
    current_data = {
        "title": title,
        "imdb_score": imdb_score,
        "is_available": is_available,
        "review_sentiment": review_sentiment,
        "genres": genres
    }
    result = check_rules(current_data)
    
    if "✅" in result:
        st.success(result)
    elif "⛔️" in result:
        st.error(result)
    else:
        st.warning(result)
