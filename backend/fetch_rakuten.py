import requests
import os
import time
from dotenv import load_dotenv
from sqlalchemy import create_engine,select
from db_setup import DATABASE_URL,Session_Local
from models import Base,Product

# ===============================
# 設定値
# ===============================

# 楽天APIで検索するキーワード
keyword =("muji スニーカー")
# 楽天APIで検索するページ数（1ページあたり30件）
pages = 10

# .env から環境変数を読み込み
load_dotenv()
APPLICATION_ID = os.getenv("RAKUTEN_APPLICATION_ID")
# 楽天APIのエンドポイント
API_URL = "https://app.rakuten.co.jp/services/api/IchibaItem/Search/20220601"
# SQLAlchemyのエンジンを作成
engine = create_engine(DATABASE_URL, future=True)


# ===============================
# 楽天APIから商品データを取得
# ===============================
def fetch_items(keyword , pages):
    """
    指定したキーワードで楽天商品検索APIを叩き、
    ページごとにデータをまとめて返す。
    """
    # 商品データを格納するリスト
    result = []
    for page in range (1,pages + 1):
        params = {
            "applicationId": APPLICATION_ID,
            "keyword": keyword,
            "hits": 30,
            "page": page,
            "imageFlag": 1,
            "format": "json",
            "availability": 1,
        }

        # 楽天APIを叩く
        response = requests.get(API_URL, params=params)
        print(f"🔎 Fetching page {page}...")

        # 429エラーが発生した場合は5秒待機してリトライ
        if response.status_code == 429:
            print("APIリクエスト制限 5秒待機してリトライ...")
            time.sleep(2)
            continue

        # 200以外の場合はエラーを出力してスキップ
        if response.status_code != 200:
            print("Error:", response.status_code, response.text)
            continue

        # レスポンスをJSON形式に変換
        data = response.json()
        items = data.get("Items",[])

        # 商品データをresultに追加
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
            print(f"✅ Page {page} done → total {len(result)}")

        print(f"🎯 Total fetched: {len(result)} items")
        if len(items) == 0:
            print(f"⚠️ Page {page} is empty, stopping early.")
            break
        
        # 0.5秒待機 APIリクエスト制限を避ける
        time.sleep(0.5)

    return result

# ===============================
# DBに商品データを保存
# ===============================
def save_to_db(items):
    """
    items を PostgreSQL に保存する。
    - 同一バッチ内の重複(product_id)を除去
    - DBに既にあるproduct_idも除外
    """
    Base.metadata.create_all(bind=engine)
    session = Session_Local()

    try:
        # 1) 同一バッチ内の重複を除去（後勝ち）
        unique_map = {}
        for item in items:
            pid = item.get("product_id")
            if pid:
                unique_map[pid] = item
        items = list(unique_map.values())

        # 2) 既存product_idを一括取得して除外（N回SELECTしない）
        pids = [it["product_id"] for it in items if it.get("product_id")]
        if pids:
            existing_pids = set(
                session.execute(
                    select(Product.product_id).where(Product.product_id.in_(pids))
                ).scalars().all()
            )
        else:
            existing_pids = set()

        new_items = [it for it in items if it["product_id"] not in existing_pids]
        print(f"🧺 fetched={len(items)} existing={len(existing_pids)} insert={len(new_items)}")

        # 3) 追加してコミット
        session.add_all([Product(**it) for it in new_items])
        session.commit()
        print("✅ データ保存完了！")

    except Exception as e:
        session.rollback()
        raise
    finally:
        session.close()

# ===============================
# メイン関数
# ===============================
def main():
    """
    商品データを楽天APIから取得し、DBに保存する。
    """
    assert APPLICATION_ID, " .env に RAKUTEN_APPLICATION_ID が設定されていません"
    # 商品データを楽天APIから取得
    items = fetch_items(keyword=keyword,pages=pages)
    # 商品データをDBに保存
    save_to_db(items)

if __name__ == "__main__":
    main()