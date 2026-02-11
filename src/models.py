from dataclasses import dataclass, field
from typing import List

@dataclass
class Movie:
    name: str                 # Название фильма
    genres: List[str] = field(default_factory=list)   # Жанры
    directors: List[str] = field(default_factory=list) # Режиссеры
    actors: List[str] = field(default_factory=list)    # Актеры
    rating: float = 0.0   

    def __str__(self):
        return f"{self.name} (Genres: {', '.join(self.genres)}, Directors: {', '.join(self.directors)}, Actors: {', '.join(self.actors)})"

@dataclass
class Genre:
    name: str

@dataclass
class Person:
    name: str
    role: str 
