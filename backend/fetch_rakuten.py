import requests
import os
from dotenv import load_dotenv

load_dotenv()
APPLICATION_ID = os.getenv("RAKUTEN_APPLICATION_ID")
API_URL = "https://app.rakuten.co.jp/services/api/IchibaItem/Search/20170706"

params = {
    "applicationId": APPLICATION_ID,
    "keyword": "スニーカー",  # キーワード検索
    "hits": 5                 # 取得件数
}

response = requests.get(API_URL, params=params)
data = response.json()

if "Items" not in data:
    print("No items found or invalid response")
    exit()

for item in data["Items"]:
    item_data = item["Item"]
    print("商品名:", item_data["itemName"])
