from transformers import pipeline
from PIL import Image

# список жанров
GENRES = [
    "Action",
    "Drama",
    "Comedy",
    "Horror",
    "Romance",
    "Sci-Fi",
    "Adventure",
    "Animation",
    "Thriller",
    "Fantasy"
]

# загружаем модель (делаем это один раз)
_classifier = None

def load_model():
    global _classifier
    if _classifier is None:
        _classifier = pipeline(
            "zero-shot-image-classification",
            model="openai/clip-vit-base-patch32"
        )
    return _classifier


def predict_genres(image):
    """
    image: PIL.Image
    return: список топ-3 жанров [(genre, score)]
    """
    classifier = load_model()

    try:
        results = classifier(image, candidate_labels=GENRES)

        # сортируем по уверенности
        results = sorted(results, key=lambda x: x["score"], reverse=True)

        top = results[:3]

        return [(r["label"], round(r["score"], 3)) for r in top]

    except Exception as e:
        return [("Ошибка анализа", 0.0)]


def predict_from_path(image_path):
    """
    если вдруг понадобится путь к файлу
    """
    try:
        image = Image.open(image_path).convert("RGB")
        return predict_genres(image)
    except Exception:
        return [("Ошибка загрузки изображения", 0.0)]