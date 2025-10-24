import requests
import os
from dotenv import load_dotenv

# .env読み込み
load_dotenv()
APPLICATION_ID = os.getenv("RAKUTEN_APPLICATION_ID")
API_URL = "https://app.rakuten.co.jp/services/api/IchibaItem/Search/20170706"

def fetch_items(keyword , pages):
    result = []
    params = {
    "applicationId": APPLICATION_ID,
    "keyword": keyword,  # キーワード検索
    "hits":5,            # 取得件数
    "page": pages
}
    response = requests.get(API_URL, params=params)

    # エラーハンドリング
    if response.status_code != 200:
        print("Error:", response.status_code, response.text)
        return result

    data = response.json()
    items = data.get("Items",[])
    for i in items:
        item = i.get("Item",{})
        result.append({
            "product_name": item.get("itemUrl", ""),
        })
    return result

def save_to_db(items):
    print(items)

def main():
    assert APPLICATION_ID, " .env に RAKUTEN_APPLICATION_ID が設定されていません"
    items = fetch_items(keyword="スニーカー",pages=1)
    save_to_db(items)

if __name__ == "__main__":
    main()