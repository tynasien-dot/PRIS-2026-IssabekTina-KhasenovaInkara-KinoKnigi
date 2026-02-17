import streamlit as st
from mock_data import movies_data
from logic import check_rules      

import networkx as nx
import matplotlib.pyplot as plt

from knowledge_graph import create_graph, find_related_entities

st.set_page_config(page_title="Movie Advisor", page_icon="🎬")
st.title("Movie Rule-Based System 🎬")
st.write("**Текущий сценарий:** Проверка по правилам проекта")

st.sidebar.header("Входные данные фильма")

selected_movie_title = st.sidebar.selectbox(
    "Выберите фильм",
    options=[m["title"] for m in movies_data]
)

default_data = next(m for m in movies_data if m["title"] == selected_movie_title)

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

if st.button("Запустить анализ по правилам"):
    current_movie_data = {
        "title": title,
        "rating_value": imdb_score,  
        "is_available": is_available,
        "review_sentiment": sentiment,
        "tags_list": genres          
    }
    
    result = check_rules(current_movie_data)
    
    if "✅" in result:
        st.success(result)
        st.balloons() 
    elif "⛔️" in result:
        st.error(result)
    else:
        st.warning(result)

with st.expander("Посмотреть структуру данных для анализа"):
    debug_data = {
        "title": title,
        "rating_value": imdb_score,
        "is_available": is_available,
        "review_sentiment": sentiment,
        "tags_list": genres
    }
    st.json(debug_data)

st.divider()
st.header("Knowledge Graph: Связи фильма 🎞️🕸")

G = create_graph()

all_nodes = list(G.nodes())
selected_node = st.selectbox(
    "Выберите объект для анализа связей:",
    options=all_nodes
)

if st.button("Показать связи в графе"):
    neighbors = find_related_entities(G, selected_node)
    if neighbors:
        st.success(f"Объект **{selected_node}** связан с: {', '.join(neighbors)}")
    else:
        st.warning("Связи не найдены")

st.write("### Визуализация графа знаний")

fig, ax = plt.subplots(figsize=(9, 6))
pos = nx.spring_layout(G, seed=42)

# цвета узлов
node_colors = []
for node, data in G.nodes(data=True):
    n_type = data.get("type", "unknown")
    if n_type == "movie":
        node_colors.append("lightgreen")
    elif n_type == "genre":
        node_colors.append("lightblue")
    elif n_type == "actor":
        node_colors.append("pink")
    elif n_type == "director":
        node_colors.append("gold")
    else:
        node_colors.append("gray")

nx.draw(
    G,
    pos,
    with_labels=True,
    node_color=node_colors,
    edge_color="gray",
    node_size=1800,
    font_size=9,
    ax=ax
)

st.pyplot(fig)