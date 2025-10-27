import io
import requests
from db_setup import DATABASE_URL
from sqlalchemy import create_engine
from transformers import CLIPProcessor, CLIPModel
from PIL import Image

DATABASE_URL = DATABASE_URL
engine = create_engine(DATABASE_URL, future=True)

model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

def fetch_image(url):
    try:
        response = requests.get(url,timeout=10)
        response.raise_for_status()
        return Image.open(io.BytesIO(response.content)).convert("RGB")
    except Exception:
        print(" 画像の読み込みに失敗しました:", url)
        return None

def main():
    img = fetch_image("https://thumbnail.image.rakuten.co.jp/@0_mall/onitsukatiger/cabinet/item/866/kp2866-01_1.jpg?_ex=128x128")
    if img:
        img.show()  
if __name__ == "__main__":
    main()