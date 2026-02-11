import networkx as nx
from models import Movie, Genre, Person

def create_graph():
    G = nx.Graph()

    # Фильмы
    movie1 = Movie("Интерстеллар", genres=["Sci-Fi", "Drama"], directors=["Кристофер Нолан"], actors=["Мэттью МакКонахи"])
    movie2 = Movie("Начало", genres=["Sci-Fi", "Action"], directors=["Кристофер Нолан"], actors=["Леонардо ДиКаприо"])
    movie3 = Movie("Темный рыцарь", genres=["Action", "Crime"], directors=["Кристофер Нолан"], actors=["Кристиан Бэйл"])
    
    movies = [movie1, movie2, movie3]

    # жанры
    all_genres = set()
    for movie in movies:
        all_genres.update(movie.genres)
    for genre in all_genres:
        G.add_node(genre, type="genre")

    # добавить людей
    all_people = {}
    for movie in movies:
        for director in movie.directors:
            all_people[director] = "Director"
        for actor in movie.actors:
            all_people[actor] = "Actor"
    for person, role in all_people.items():
        G.add_node(person, type=role.lower())

    # фильсы как узлы
    for movie in movies:
        G.add_node(movie.name, type="movie")

    # связи
    for movie in movies:
        for genre in movie.genres:
            G.add_edge(movie.name, genre)
        for director in movie.directors:
            G.add_edge(movie.name, director)
        for actor in movie.actors:
            G.add_edge(movie.name, actor)

    return G

def find_related_entities(graph, start_node):
    """
    Найти все объекты, связанные с start_node
    """
    if start_node not in graph:
        return []
    return list(graph.neighbors(start_node))
