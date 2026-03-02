import pandas as pd
import os
import re

def load_clean_data():
    current_dir = os.path.dirname(__file__)
    file_path = os.path.join(current_dir, '..', 'data', 'raw', 'MovieGenre.csv')
    
    try:
        df = pd.read_csv(file_path, encoding='latin-1')
        # добавлена фильтрация строк без постеров 
        df = df.dropna(subset=['Title', 'Genre', 'IMDB Score', 'Poster'])
        
        # вытаскиваем год из столбца тайтл
        def get_year_from_title(title_string):
            match = re.search(r'\((\d{4})\)', str(title_string))
            if match:
                return int(match.group(1)) 
            return 0 

        df['year_val'] = df['Title'].apply(get_year_from_title)
        
        # добавлен фильтр рейтинга и проверка на пустую строку в постере
        df = df[
            (df['year_val'] >= 1980) & 
            (df['IMDB Score'] >= 7.5) & 
            (df['Poster'].astype(str).str.strip() != "")
        ]
        
        # изменено количество фильмов на 250
        if len(df) > 250:
            df = df.sample(n=250, random_state=42)
            
        movies = []
        for _, row in df.iterrows():
            raw_title = str(row['Title'])
            year = str(row['year_val'])
            
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