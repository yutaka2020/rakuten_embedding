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


# CPU スレッド数を1に固定（Mac で libomp エラー防止）
torch.set_num_threads(1)

# ============================
#  DB接続設定
# ============================
engine = create_engine(DATABASE_URL, future=True)

# ============================
#  CLIPモデル読み込み
# ============================
model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

# ============================
#  URL から画像を取得
# ============================
def fetch_image(url):
    """
    画像URLから画像をダウンロードし、PIL.Image に変換して返す。
    ダウンロードに失敗した場合は None を返す。
    """
    try:
        response = requests.get(url,timeout=10)
        response.raise_for_status()
        return Image.open(io.BytesIO(response.content)).convert("RGB")
    except Exception as error:
        print(" 画像の読み込みに失敗しました:", url,"|",error)
        return None

# ============================
#  画像 → ベクトル化 & FAISS へ登録
# ============================
def main():
    # CLIPで作ったベクトルを格納
    vectors = []
    # FAISSのID ⇄ DBのproduct_id の対応表
    id_map = []
    # DB から (id, image_url) を全件取得
    with Session(engine) as session:
        products = session.execute(select(Product.id, Product.image_url)).all()
        for pid, image_url in tqdm(products, desc="Embedding images"):
            # 画像のダウンロード
            img = fetch_image(image_url)
            if img is None:
                continue

            # CLIP入力用テンソルに変換
            inputs = processor(images=img, return_tensors="pt")

            # 勾配の計算をOFFする
            with torch.no_grad():
                emb = model.get_image_features(**inputs)
                # L2正規化によりベクトルの長さを統一する
                emb = emb / emb.norm(p=2,dim=-1,keepdim=True)
                # numpy に変換（FAISS用）
                vec = emb.cpu().numpy().astype("float32")
            vectors.append(vec[0])
            id_map.append(pid)

    # ベクトルが1つも作成されなかった場合はエラーを出力して終了
    if not vectors:
        print("No vectors created")
        return
    # numpyの2次元配列にまとめる
    mat = np.vstack(vectors).astype("float32")

    # ============================
    #  FAISS の Index を作成（内積用）
    # ============================
    # 512次元のベクトルを登録できる検索indexを作成（IP: Inner Product）
    index = faiss.IndexFlatIP(mat.shape[1])
    index.add(mat)

    # ============================
    #  index・id_map の保存
    # ============================
    faiss.write_index(index,"faiss.index")
    # faiss内部のIDとDB上のproduct_idを紐つける
    pd.DataFrame({"faiss_id": range(len(id_map)),"product_id":id_map}).to_csv("id_map.csv", index=False)
    print(f"Saved faiss.index and id_map.csv ({len(id_map)} items)")

# ============================
#  メイン関数実行
# ============================
if __name__ == "__main__":
    main()