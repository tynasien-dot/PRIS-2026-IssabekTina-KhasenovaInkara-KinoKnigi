import networkx as nx
from models import Movie
from mock_data import movies_data

def create_graph():
    G = nx.Graph()
    
    for data in movies_data:
        movie = Movie(
            name=data["title"],
            year=data["year"],
            genres=data["genres"],
            rating=data["imdb_score"],
            description=data["description"],
            poster_url=data["poster"]
        )

        G.add_node(movie.name, type="movie", rating=movie.rating, year=movie.year)

        for g in movie.genres:
            G.add_node(g, type="genre")
            G.add_edge(movie.name, g)

        if movie.year != "Unknown":
            G.add_node(movie.year, type="year")
            G.add_edge(movie.name, movie.year)
            
    return G

def get_recommendations(G, node_name):
    if node_name not in G:
        return []
    return list(G.neighbors(node_name))