import streamlit as st
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components
import os
import re

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
    
    if st.button("Обновить данные"):
        st.subheader(f"🎬 {current_movie['title']}")
        st.write(f"**IMDB Score:** {current_movie['imdb_score']}")
        st.write(f"**Жанры:** {', '.join(current_movie['genres'])}")
        
        st.write("**Описание:**")
        st.info(current_movie.get('description', "Описание временно недоступно."))
        
        if current_movie.get('poster'):
            st.image(current_movie['poster'], use_container_width=True)
    

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
        
        year_match = re.search(r'(\d{4})', user_input)
        if year_match and int(year_match.group(1)) < 1980:
            answer = f"К сожалению, в нашем сервисе только фильмы с 1980 года."
        else:
            answer = process_text_message(user_input, st.session_state.graph, st.session_state.movies)
        
        poster_url = None
        for m in st.session_state.movies:
            if m['title'].lower() in answer.lower():
                poster_url = m['poster']
                break
        
        st.session_state.messages.append({"role": "assistant", "content": answer, "poster": poster_url})
        st.rerun()

st.caption("Разработано в рамках лабораторной работы PRIS-2026")