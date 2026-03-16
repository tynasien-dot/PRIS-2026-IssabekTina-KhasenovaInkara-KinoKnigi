import streamlit as st
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components
import os
import re

from mock_data import movies_data
from knowledge_graph import create_graph
from logic import check_rules, process_text_message, apply_production_model

st.set_page_config(page_title="Movie Management System", layout="wide")

# 1. Инициализация состояния
if 'graph' not in st.session_state:
    st.session_state.graph = create_graph()

# Принудительно обновляем список из mock_data (чтобы подтянулись фильтры)
st.session_state.movies = movies_data

if 'messages' not in st.session_state:
    st.session_state.messages = []

# --- САЙДБАР ---
with st.sidebar:
    st.header("📥 Выбор фильма")
    
    if st.session_state.movies:
        movie_titles = [m['title'] for m in st.session_state.movies]
        selected_name = st.selectbox("Выберите из топ 250-фильмов", movie_titles)
        
        # Исправленный поиск (защита от StopIteration)
        current_movie = next((m for m in st.session_state.movies if m['title'] == selected_name), st.session_state.movies[0])
        
        if st.button("Анализировать фильм"):
            st.subheader(f"🎬 {current_movie['title']}")
            
            p_url = current_movie.get('poster')
            if p_url and str(p_url).lower() != 'nan' and 'http' in str(p_url):
                st.image(p_url, use_container_width=True)
                
            st.write(f"**Рейтинг:** {current_movie['imdb_score']} ⭐")
            st.write(f"**Год:** {current_movie['year']}")
            st.write(f"**Жанры:** {', '.join(current_movie['genres'])}")

            st.divider()
            st.subheader("Оценка системы")
            
            # Твой вердикт
            verdict = apply_production_model(current_movie)
            st.success(verdict)
    else:
        st.error("Список фильмов пуст. Проверьте фильтры в mock_data.py")

# --- ОСНОВНОЙ ИНТЕРФЕЙС ---
st.title("🎬 Movie Advisor System v2.0")

col1, col2 = st.columns([1, 1])

# Граф знаний
with col1:
    st.subheader("🕸 Граф знаний")
    net = Network(height="400px", width="100%", bgcolor="#f0f2f6", font_color="black")
    net.from_nx(st.session_state.graph)
    
    path = "graph_display.html"
    net.save_graph(path)

    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            html_data = f.read()
        components.html(html_data, height=450)

# Чат-бот
with col2:
    st.subheader("💬 Чат-бот консультант")
    chat_container = st.container(height=400)

    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"], unsafe_allow_html=True)

    if user_input := st.chat_input("Спроси про жанр или год..."):
        st.session_state.messages.append({"role": "user", "content": user_input})

        answer = process_text_message(user_input, st.session_state.graph, st.session_state.movies)

        # Поиск рекомендаций (фильтруем тех, у кого нет ссылки)
        recommended_movies = []
        for m in st.session_state.movies:
            p_val = str(m.get('poster', '')).lower()
            if (m['title'].lower() in answer.lower() or m['description'].lower() in answer.lower()) and 'http' in p_val:
                recommended_movies.append(m)

        recommended_movies = recommended_movies[:3]
        detailed_info_text = "\n🎬 **Топ-3 рекомендации**\n"

        if recommended_movies:
            for idx, movie in enumerate(recommended_movies, 1):
                system_verdict = apply_production_model(movie)
                poster = movie.get("poster")
                
                # HTML карточка
                poster_html = f'<br><img src="{poster}" width="220" style="border-radius:10px;"><br>'

                detailed_info_text += f"""
---
🏆 **#{idx}**
📌 **Название:** {movie.get('title', '—')}
⭐ **Рейтинг:** {movie.get('imdb_score', '—')} | 📅 **Год:** {movie.get('year', '—')}
🎭 **Жанры:** {', '.join(movie.get('genres', []))}

🤖 **Оценка системы:** *{system_verdict}*
{poster_html}
"""

        final_answer = answer + ("\n\n" + detailed_info_text if recommended_movies else "")
        st.session_state.messages.append({"role": "assistant", "content": final_answer})
        st.rerun()

st.caption("Разработано в рамках лабораторной работы PRIS-2026")