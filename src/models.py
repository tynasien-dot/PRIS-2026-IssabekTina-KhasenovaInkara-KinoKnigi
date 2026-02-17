from dataclasses import dataclass, field
from typing import List

@dataclass
class Movie:
    name: str
    year: str
    genres: List[str] = field(default_factory=list)
    rating: float = 0.0
    description: str = "" 
    poster_url: str = ""  

    def __str__(self):
        return f"{self.name} ({self.year})"