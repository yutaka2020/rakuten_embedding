import io
import requests
import faiss
import torch
import numpy as np
from sqlalchemy.orm import Session
from tqdm import tqdm
from models import Product
from db_setup import DATABASE_URL
from sqlalchemy import create_engine, select
from transformers import CLIPProcessor, CLIPModel
from PIL import Image

# ----------------------------
# 設定
# ----------------------------
torch.set_num_threads(1)

# ----------------------------
# DB / モデル初期化
# ----------------------------
engine = create_engine(DATABASE_URL, future=True)

model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

# ----------------------------
# URL から画像を取得
# ----------------------------
def fetch_image(url: str):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return Image.open(io.BytesIO(response.content)).convert("RGB")
    except Exception as error:
        print(" 画像の読み込みに失敗しました:", url, "|", error)
        return None

# ----------------------------
# メイン処理
# ----------------------------
def main():
    vectors = []
    ids = []

    with Session(engine) as session:
        # ✅ 取得順を固定（デバッグ・再現性向上）
        products = session.execute(
            select(Product.id, Product.image_url).order_by(Product.id.asc())
        ).all()

        for pid, image_url in tqdm(products, desc="Embedding images"):
            img = fetch_image(image_url)
            if img is None:
                continue

            inputs = processor(images=img, return_tensors="pt")
            with torch.no_grad():
                emb = model.get_image_features(**inputs)
                emb = emb / emb.norm(p=2, dim=-1, keepdim=True)
                vec = emb.cpu().numpy().astype("float32")[0]  # (512,)

            vectors.append(vec)
            ids.append(int(pid))

    if not vectors:
        print("No vectors created")
        return

    mat = np.vstack(vectors).astype("float32")
    ids_np = np.array(ids, dtype=np.int64)

    # ----------------------------
    # FAISS Index（ID付き）
    # ----------------------------
    d = mat.shape[1]
    base = faiss.IndexFlatIP(d)
    index = faiss.IndexIDMap2(base)

    index.add_with_ids(mat, ids_np)

    # ----------------------------
    # 保存
    # ----------------------------
    faiss.write_index(index, "faiss.index")
    print(f"Saved faiss.index (IndexIDMap2) ({index.ntotal} items)")

if __name__ == "__main__":
    main()
