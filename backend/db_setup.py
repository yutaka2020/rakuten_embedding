from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL,future=True)
Base.metadata.create_all(bind=engine)

Session_Local = sessionmaker(autocommit=False, autoflush=False, bind=engine)