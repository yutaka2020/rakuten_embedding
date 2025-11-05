import io
from PIL import Image
import faiss
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from numpy._core.multiarray import scalar
import pandas as pd
import requests
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
import torch
from transformers import CLIPModel, CLIPProcessor
from models import Product

app = FastAPI(title = "Sneaker Visual Search")
# CROSを設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ← すべてのオリジン（開発中はこれでOK）
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

torch.set_num_threads(1)
torch.set_num_interop_threads(1)

@app.middleware("http")
async def log_cors(request, call_next):
    print("🌐 Origin:", request.headers.get("origin"))
    response = await call_next(request)
    print("🔁 Response headers:", response.headers)
    return response

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


def load_image(src: str) -> Image.Image:
    """URLまたはパスから画像を取得"""
    if src.startswith("http"):
        request = requests.get(src, timeout = 15)
        request.raise_for_status()
        return Image.open(io.BytesIO(request.content)).convert("RGB")
    else:
        return Image.open(src).convert("RGB")

@app.post("/api/search")
async def search(
    image_url: str = Form(None),
    file: UploadFile = File(None),
    topk: int = Form(1)
    ):
    """画像URL or ファイルを受け取り、類似画像を返す"""
    if not image_url and not file:
        return {"error": "画像URLまたは、ファイルを指定してください"}

    if image_url:
        img = load_image(image_url)
    else:
        img = Image.open(io.BytesIO(await file.read())).convert("RGB")    
    
     # CLIP埋め込み
    inputs = processor(images=img, return_tensors="pt")
    with torch.no_grad():
        q = model.get_image_features(**inputs)
        q = q / q.norm(p=2, dim=-1, keepdim=True)
        q = q.cpu().numpy().astype("float32")

    # 類似検索
    Distance, IndexID = index.search(q, topk)
    faiss_ids = IndexID[0]
    scores = Distance[0]

    id_map_dict = id_map.set_index("faiss_id")["product_id"].to_dict()
    result = []
    with Session(engine) as session:
        for fid ,score in zip(faiss_ids, scores):
            pid = int(id_map_dict.get(fid, -1))
            if pid == -1:
                continue
            row = session.execute(
                select(Product).where(Product.id == pid)
            ).scalar_one_or_none()
            if not row:
                continue
            result.append({
                 "score": float(score),
                "name": row.product_name,
                "price": row.price,
                "image_url": row.image_url,
                "product_url": row.product_url,
                "shop": row.shop_name,
            })

        return {"results": result}
