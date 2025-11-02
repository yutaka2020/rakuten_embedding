from sqlite3 import DatabaseError
from sqlalchemy import create_engine, engine,text

DATABESE_URL = "postgresql+psycopg2://postgres:postgres@localhost:5432/rakuten"

engine = create_engine(DATABESE_URL,future=True,echo=False)

try:
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    print(("Connected to PostgreSQL successfully!"))
except Exception as e:
    print("Connection failed:", e)
