import streamlit as st
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components
import os

from mock_data import movies_data
from knowledge_graph import create_graph
from logic import check_rules, process_text_message

st.set_page_config(page_title="Movie Management System", layout="wide")

if 'graph' not in st.session_state:
    st.session_state.graph = create_graph()
if 'movies' not in st.session_state:
    st.session_state.movies = movies_data
if 'messages' not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.header("📥 Входные данные фильма")
    
    movie_titles = [m['title'] for m in st.session_state.movies]
    selected_name = st.selectbox("Выберите фильм", movie_titles)
    
    current_movie = next(m for m in st.session_state.movies if m['title'] == selected_name)
    
    st.text_input("Название фильма:", value=current_movie['title'])
    st.number_input("IMDB Score:", value=float(current_movie['imdb_score']), step=0.1)
    st.checkbox("Доступность (Available)", value=True)
    st.selectbox("Настроение отзывов:", ["positive", "neutral", "negative"])
    st.text_input("Жанры (через запятую):", value=", ".join(current_movie['genres']))
    
    st.button("Обновить данные")
    
    st.divider()
    st.header("⚙️ Валидация")
    if st.button("Проверить по правилам"):
        res = check_rules(current_movie)
        st.info(f"Результат: {res}")

st.title("🎬 Movie Advisor System v2.0")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("🕸 Граф знаний")
    net = Network(height="400px", width="100%", bgcolor="#f0f2f6", font_color="black")
    net.from_nx(st.session_state.graph)
    
    path = "graph_display.html"
    net.save_graph(path)
    with open(path, 'r', encoding='utf-8') as f:
        html_data = f.read()
    components.html(html_data, height=450)

with col2:
    st.subheader("💬 Чат-бот консультант")
    
    chat_container = st.container(height=380)
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                if "poster" in message and message["poster"]:
                    st.image(message["poster"], width=100)

    if user_input := st.chat_input("Спроси про жанр или год..."):
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        answer = process_text_message(user_input, st.session_state.graph, st.session_state.movies)
        
        poster_url = None
        for m in st.session_state.movies:
            if m['title'].lower() in answer.lower():
                poster_url = m['poster']
                break
        
        st.session_state.messages.append({"role": "assistant", "content": answer, "poster": poster_url})
        st.rerun()

st.caption("Разработано в рамках лабораторной работы PRIS-2026")