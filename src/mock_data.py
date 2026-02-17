import pandas as pd
import os
import re

def load_clean_data():
    current_dir = os.path.dirname(__file__)
    file_path = os.path.join(current_dir, '..', 'data', 'raw', 'MovieGenre.csv')
    
    try:
        df = pd.read_csv(file_path, encoding='latin-1')
        
        df = df.dropna(subset=['Title', 'Genre', 'IMDB Score'])
        
        df = df.head(60)
        
        movies = []
        for _, row in df.iterrows():
            raw_title = str(row['Title'])
            
            year_match = re.search(r'\((\d{4})\)', raw_title)
            year = year_match.group(1) if year_match else "Unknown"
            
            clean_title = re.sub(r'\(\d{4}\)', '', raw_title).strip()
            
            genres = str(row['Genre']).split('|')
            rating = row['IMDB Score']
            
            description = (f"This {', '.join(genres)} film was released in {year}. "
                           f"It is titled {clean_title} and has an IMDB rating of {rating}.")
            
            movies.append({
                "title": clean_title,
                "year": year,
                "imdb_score": float(rating),
                "genres": genres,
                "description": description,
                "poster": str(row.get('Poster', ''))
            })
            
        return movies

    except Exception as e:
        print(f"⚠️ Ошибка загрузки датасета: {e}")
        return []

movies_data = load_clean_data()