import io
import requests
import faiss
import torch
import numpy as np
import pandas as pd
from sqlalchemy.orm import Session
from tqdm import tqdm
from models import Product
from db_setup import DATABASE_URL
from sqlalchemy import create_engine, select
from transformers import CLIPProcessor, CLIPModel
from PIL import Image

torch.set_num_threads(1)

DATABASE_URL = DATABASE_URL
engine = create_engine(DATABASE_URL, future=True)

model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

def fetch_image(url):
    try:
        response = requests.get(url,timeout=10)
        response.raise_for_status()
        return Image.open(io.BytesIO(response.content)).convert("RGB")
    except Exception as error:
        print(" 画像の読み込みに失敗しました:", url,"|",error)
        return None

def main():
    vectors = []
    id_map = []
    with Session(engine) as session:
        products = session.execute(select(Product.id, Product.image_url)).all()
        for pid, image_url in tqdm(products, desc="Embedding images"):
            img = fetch_image(image_url)
            if img is None:
                continue
            inputs = processor(images=img, return_tensors="pt")
            # 勾配の計算をOFFする
            with torch.no_grad():
                emb = model.get_image_features(**inputs)
                # L2正規化によりベクトルの長さを統一する
                emb = emb / emb.norm(p=2,dim=-1,keepdim=True)
                vec = emb.cpu().numpy().astype("float32")
            vectors.append(vec[0])
            id_map.append(pid)
    if not vectors:
        print("No vectors created")
        return
    
    mat = np.vstack(vectors).astype("float32")
    # 512次元のベクトルを登録できる検索indexを作成
    index = faiss.IndexFlatIP(mat.shape[1])
    index.add(mat)

    faiss.write_index(index,"faiss.index")
    # faiss内部のIDとDB上のproduct_idを紐つける
    pd.DataFrame({"faiss_id": range(len(id_map)),"product_id":id_map}).to_csv("id_map.csv", index=False)
    print(f"Saved faiss.index and id_map.csv ({len(id_map)} items)")


if __name__ == "__main__":
    main()