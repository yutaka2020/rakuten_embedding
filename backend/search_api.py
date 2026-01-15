import io
from PIL import Image,UnidentifiedImageError
import faiss
from fastapi import FastAPI, File, Form, UploadFile, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import requests
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
import torch
from transformers import CLIPModel, CLIPProcessor
from models import Product
import os
from fastapi.responses import JSONResponse


# ===============================================================
# 　Sneaker Visual Search API
# 画像URLまたはアップロード画像を入力し、
# CLIP + FAISS により類似スニーカー商品を検索して返す。
# ===============================================================


# 返す検索上位件数定義
NumResult = 9

# FastAPIアプリ作成
app = FastAPI(title = "Sneaker Visual Search")

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})


# CROSを設定（Next.jsなど他のフロントエンドからの通信を許可）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ALLOWED_EXT = {".jpg", ".jpeg", ".png", ".webp"}  
ALLOWED_MIME = {"image/jpeg", "image/png", "image/webp"}  

def validate_upload(file: UploadFile):
    name = (file.filename or "").lower()
    ext = "." + name.split(".")[-1] if "." in name else ""

    # 拡張子チェック
    if ext not in ALLOWED_EXT:
        raise HTTPException(status_code=400, detail=f"対応外の拡張子です（{', '.join(sorted(ALLOWED_EXT))} のみ）")

    # Content-Typeチェック（ブラウザが送ってくるやつ）
    ctype = (file.content_type or "").lower()
    if ctype and ctype not in ALLOWED_MIME:
        raise HTTPException(status_code=400, detail=f"対応外のファイル形式です（Content-Type: {ctype}）")


# ---------------------------------------------------------------
# PyTorchの並列処理設定
# デフォルトではCPUコアをすべて使うため、Macなどで負荷が高くなる。
# スレッド数を制限してフリーズ防止。
# ---------------------------------------------------------------
torch.set_num_threads(1)
torch.set_num_interop_threads(1)

# ---------------------------------------------------------------
# DB / FAISS 関連設定
# PostgreSQLで商品情報を取得し、
# FAISS（ベクトル検索エンジン）で類似画像を探索する。
# ---------------------------------------------------------------
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:postgres@localhost:5432/rakuten"
)
FAISS_PATH = "faiss.index"

engine = create_engine(DATABASE_URL,future=True)
index =faiss.read_index(FAISS_PATH)
# FAISS ID → product_id 対応表を起動時に1回だけ作成（パフォーマンス最適化）

# CLIP モデル読み込み（画像 → ベクトル変換に使用）
model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32", use_fast=True)


def load_image(src: str) -> Image.Image:
    """URLから画像を取得（デバッグ付き）"""
    print("=== image_url debug ===")
    print("url:", src)
    print("length:", len(src))
    print("=======================")

    if not src.startswith("http"):
        raise ValueError("image_url は http(s) で始まる必要があります")

    response = requests.get(src, timeout=15)
    print("status_code:", response.status_code)
    print("content_type:", response.headers.get("Content-Type"))
    print("bytes:", len(response.content))
    print("head:", response.content[:32])
    print("=======================")

    response.raise_for_status()

    try:
        return Image.open(io.BytesIO(response.content)).convert("RGB")
    except Exception as e:
        raise ValueError(f"URLから取得したデータを画像として読めません: {e}")

@app.post("/api/search")
async def search(
    image_url: str = Form(None),
    file: UploadFile = File(None),
    topk: int = Form(NumResult),
    min_price: int = Form(None),
    max_price: int = Form(None),
    ):
    """
    画像URL or ファイルを受け取り、
    CLIPで埋め込み → FAISSで類似検索 → DBから商品情報を返す
    """
    print("min_price:", min_price, type(min_price))
    print("max_price:", max_price, type(max_price))

    # 入力チェック
    if (not image_url or not image_url.strip()) and file is None:
        return {"error": "画像URLまたはファイルを指定してください"}

    # 画像読み込み
    if image_url and image_url.strip():
        img = load_image(image_url.strip())
    elif file is not None:
        validate_upload(file)

        data = await file.read()
        if len(data) == 0:
            raise HTTPException(status_code=400, detail="アップロードされたファイルが空です")

        try:
            img = Image.open(io.BytesIO(data)).convert("RGB")
        except UnidentifiedImageError:
            raise HTTPException(status_code=400, detail="画像として読み込めませんでした（対応外または破損しています）")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"画像の読み込みに失敗しました: {e}")
    else:
        # この分岐には到達しないはず（入力チェックで既にエラーを返している）
        raise HTTPException(status_code=400, detail="画像URLまたはファイルを指定してください")


    # CLIP埋め込み（画像 → ベクトル）
    inputs = processor(images=img, return_tensors="pt")
    with torch.no_grad():
        q = model.get_image_features(**inputs)
        # L2正規化
        q = q / q.norm(p=2, dim=-1, keepdim=True)
        q = q.cpu().numpy().astype("float32")

    # # 類似検索（FAISSで上位topk件を検索）
    Distance, IndexID = index.search(q, topk)
    print("FAISS IDs sample:", IndexID[0][:10])
    product_ids = IndexID[0]
    scores = Distance[0]

    result = []

    with Session(engine) as session:
        # 有効なproduct_idのみを抽出（-1を除外）
        valid_ids = [int(pid) for pid in product_ids if pid != -1]
        
        if not valid_ids:
            return {"results": []}
        
        # まとめて取得
        query = select(Product).where(Product.id.in_(valid_ids))
        if min_price:
            query = query.where(Product.price >= min_price)
        if max_price:
            query = query.where(Product.price <= max_price)
        
        rows = session.execute(query).scalars().all()
        
        # product_idをキーとした辞書を作成（高速検索のため）
        product_dict = {row.id: row for row in rows}
        
        # 元の順序を保持しながら結果を構築
        for pid, score in zip(product_ids, scores):
            if pid == -1:
                continue
            row = product_dict.get(int(pid))
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
