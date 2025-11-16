from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base
import os
from dotenv import load_dotenv

# ===============================
# DB接続設定
# ===============================

# .env から環境変数を読み込む
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# SQLAlchemy のエンジンを作成（DB への実際の接続を管理）
engine = create_engine(DATABASE_URL,future=True)
# models.pyで定義されたテーブルをDBにを作成
Base.metadata.create_all(bind=engine)

# SessionLocal: DB セッション（接続）を生成するためのクラス
# - autocommit=False : 明示的に commit() を呼ぶ必要あり
# - autoflush=False  : commit前に自動で flush しない
Session_Local = sessionmaker(autocommit=False, autoflush=False, bind=engine)