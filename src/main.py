import streamlit as st
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components
import os
from mock_data import movies_data
from knowledge_graph import create_graph
from logic import check_rules, process_text_message, apply_production_model, get_movie_details

st.set_page_config(page_title="Movie Advisor System", layout="wide")

if 'graph' not in st.session_state:
    st.session_state.graph = create_graph()
st.session_state.movies = movies_data

if 'messages' not in st.session_state:
    st.session_state.messages = []
    welcome_text = process_text_message("привет", st.session_state.graph, st.session_state.movies)
    st.session_state.messages.append({"role": "assistant", "content": welcome_text})

# --- САЙДБАР ---
with st.sidebar:
    st.header("📥 Выбор фильма")
    if st.session_state.movies:
        movie_titles = [m['title'] for m in st.session_state.movies]
        selected_name = st.selectbox("Выберите из топ 250-фильмов", movie_titles)
        current_movie = next((m for m in st.session_state.movies if m['title'] == selected_name), st.session_state.movies[0])
        if st.button("Анализировать фильм"):
            st.subheader(f"🎬 {current_movie['title']}")
            with st.spinner('Загрузка данных...'):
                movie_info = get_movie_details(current_movie['title'], current_movie.get('year'))
                st.image(movie_info['poster'], use_container_width=True)
                st.markdown(f"**📝 Обзор:**\n{movie_info['overview']}")
            st.success(apply_production_model(current_movie))

# --- ОСНОВНОЙ ИНТЕРФЕЙС ---
st.title("🎬 Movie Advisor System v2.0")
col1, col2 = st.columns([1, 1.2])

with col1:
    st.subheader("🕸 Граф знаний")
    net = Network(height="450px", width="100%", bgcolor="#f0f2f6", font_color="black")
    net.from_nx(st.session_state.graph)
    path = "graph_display.html"
    net.save_graph(path)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            html_data = f.read()
        components.html(html_data, height=480)

with col2:
    st.subheader("💬 Чат-бот консультант")
    
    # ЗАГРУЗКА ФАЙЛА (Для будущей функции Computer Vision)
    uploaded_file = st.file_uploader("Загрузи постер для определения жанра", type=['jpg', 'png', 'jpeg'])
    
    if uploaded_file is not None:
        # код (Computer Vision)
        st.info("Файл получен. Нейросеть анализирует изображение...")
        st.warning("Функция определения жанра будет доступна после интеграции модели.")

    chat_container = st.container(height=400)
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"], unsafe_allow_html=True)

    col_input, col_btn = st.columns([0.85, 0.15])
    with col_input:
        user_input = st.chat_input("Спроси про жанр или год...")
    with col_btn:
        luck_clicked = st.button("🎲")

    final_query = None
    if luck_clicked:
        final_query = "мне повезет"
    elif user_input:
        final_query = user_input

    if final_query:
        display_text = "🎲 Выбери мне случайный фильм!" if final_query == "мне повезет" else final_query
        st.session_state.messages.append({"role": "user", "content": display_text})
        answer = process_text_message(final_query, st.session_state.graph, st.session_state.movies)

        recommended_movies = [m for m in st.session_state.movies if m['title'].lower() in answer.lower()]
        limit = 1 if final_query == "мне повезет" else 3
        recommended_movies = recommended_movies[:limit]
        
        detailed_info_text = ""
        if recommended_movies:
            detailed_info_text = "\n🎬 **Информация:**\n"
            for movie in recommended_movies:
                system_verdict = apply_production_model(movie)
                movie_info = get_movie_details(movie['title'], movie.get('year'))
                poster_html = f'<br><img src="{movie_info["poster"]}" width="240" style="border-radius:10px;"><br>'
                detailed_info_text += f"---\n📌 **{movie['title']}**\n📖 {movie_info['overview']}\n{poster_html}"

        st.session_state.messages.append({"role": "assistant", "content": answer + detailed_info_text})
        st.rerun()

st.caption("Разработано в рамках лабораторной работы PRIS-2026")