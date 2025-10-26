from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from sqlalchemy import Integer, Text, String, TIMESTAMP, func, Column

Base = declarative_base()

class Product(Base):
    __tablename__ = "products"
    id:  id = Column(Integer, primary_key=True, index=True)
    product_id: Mapped[str] = mapped_column(String(255))
    product_name: Mapped[str] = mapped_column(Text)
    image_url: Mapped[str] = mapped_column(Text)
    product_url: Mapped[str] = mapped_column(Text)
    price: Mapped[int] = mapped_column(Integer, nullable=True)
    shop_name: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[str] = mapped_column(TIMESTAMP, server_default=func.now())
