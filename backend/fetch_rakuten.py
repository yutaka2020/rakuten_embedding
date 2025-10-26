import requests
import os
import time
from dotenv import load_dotenv
from sqlalchemy import create_engine
from db_setup import DATABASE_URL,Session_Local
from models import Base,Product

# .env読み込み
load_dotenv()
APPLICATION_ID = os.getenv("RAKUTEN_APPLICATION_ID")
API_URL = "https://app.rakuten.co.jp/services/api/IchibaItem/Search/20220601"
engine = create_engine(DATABASE_URL, future=True)

def fetch_items(keyword , pages):
    result = []
    for page in range (1,pages + 1):
        params = {
            "applicationId": APPLICATION_ID,
            "keyword": keyword,
            "hits": 30,
            "page": page,
            "imageFlag": 1,
            "format": "json",
            "availability": 1,}

        response = requests.get(API_URL, params=params)
        print(f"🔎 Fetching page {page}...")

        if response.status_code == 429:
            print("⚠️ APIリクエスト制限 5秒待機してリトライ...")
            time.sleep(5)
            continue

    if response.status_code != 200:
        print("Error:", response.status_code, response.text)
        return result

    data = response.json()
    items = data.get("Items",[])
    for i in items:
        item = i.get("Item",{})
        result.append({
                "product_id": item.get("itemCode", ""),
                "product_name": item.get("itemName", ""),
                "image_url": item["mediumImageUrls"][0]["imageUrl"],
                "product_url": item.get("itemUrl", ""),
                "price": item.get("itemPrice", 0),
                "shop_name": item.get("shopName", "")
        })
        time.sleep(2)
    return result

def save_to_db(items):
    Base.metadata.create_all(bind=engine)
    session = Session_Local()
    try:
        for item in items:
            existing = session.query(Product).filter_by(product_id=item["product_id"]).first()
            if existing:
                print(f"既存スキップ: {item['product_name']}")
                continue
            product = Product(**item)
            session.add(product)
        session.commit()
        print(" データ保存完了！")
    finally:
        session.close()

def main():
    assert APPLICATION_ID, " .env に RAKUTEN_APPLICATION_ID が設定されていません"
    items = fetch_items(keyword="スニーカー",pages=5)
    save_to_db(items)

if __name__ == "__main__":
    main()