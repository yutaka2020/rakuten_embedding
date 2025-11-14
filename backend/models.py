from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from sqlalchemy import Integer, Text, String, TIMESTAMP, func, Column

Base = declarative_base()

# ===============================
# DBモデルを定義
# 楽天APIから取得した商品データを保存するテーブル
# ===============================
class Product(Base):
    __tablename__ = "products"

    # 内部管理用ID
    id:  id = Column(Integer, primary_key=True, index=True)
    # 楽天の商品コード
    product_id: Mapped[str] = Column(String, unique=True, index=True)
    # 商品名
    product_name: Mapped[str] = mapped_column(Text)
    # 商品画像URL
    image_url: Mapped[str] = mapped_column(Text)
    # 商品ページURL
    product_url: Mapped[str] = mapped_column(Text)
    # 商品価格（nullable: 一部データに価格なしの場合を許容）
    price: Mapped[int] = mapped_column(Integer, nullable=True)      
    # 商品店舗名（nullable）
    shop_name: Mapped[str] = mapped_column(Text, nullable=True)
    # 作成日時
    created_at: Mapped[str] = mapped_column(TIMESTAMP, server_default=func.now())
