from sqlalchemy import create_engine
from models import Base
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL,future=True)
Base.metadata.create_all(bind=engine)

print("Table 'product' create successfully ")