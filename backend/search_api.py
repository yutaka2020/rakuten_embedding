import io
from PIL import Image
import faiss
from fastapi import FastAPI
import pandas as pd
import requests
from sqlalchemy import create_engine
from transformers import CLIPModel, CLIPProcessor

# DB FAISS　を設定
DATABASE_URL = "postgresql+psycopg2://postgres:postgres@localhost:5432/rakuten"
FAISS_PATH = "faiss.index"
IDMAP_PATH = "id_map.csv"

engine = create_engine(DATABASE_URL,future=True)
index =faiss.read_index(FAISS_PATH)
id_map = pd.read_csv(IDMAP_PATH)

# CLIP model 読み込み
model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

app = FastAPI(title = "Sneaker Visual Search")

def load_image(src: str) -> Image.Image:
    """URLまたはパスから画像を取得"""
    if src.startswith("http"):
        request = requests.get(src, timeout = 15)
        request.raise_for_status()
        return Image.open(io.BytesIO(request.content)).convert("RGB")
    else:
        return Image.open(src).convert("RGB")

def search():
    image_url = "https://thumbnail.image.rakuten.co.jp/@0_mall/onitsukatiger/cabinet/item/866/kp2866-01_1.jpg?_ex=128x128"
    img = load_image(image_url)
    if img:
        img.show()

if __name__ == "__main__":
    search()