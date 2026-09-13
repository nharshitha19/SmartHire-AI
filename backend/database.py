import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Always read from Render's environment variable
DATABASE_URL = os.getenv("DATABASE_URL")

try:
    if DATABASE_URL and DATABASE_URL.startswith("postgresql"):
        # Use PostgreSQL on Render
        engine = create_engine(DATABASE_URL, pool_pre_ping=True)
        # Quick connection test
        with engine.connect() as conn:
            pass
    else:
        # Fallback for local development (SQLite)
        base_dir = os.path.dirname(os.path.abspath(__file__))
        sqlite_path = os.path.join(base_dir, "smarthire_ai.db")
        FALLBACK_DB_URL = f"sqlite:///{sqlite_path}"
        engine = create_engine(FALLBACK_DB_URL, connect_args={"check_same_thread": False})
except Exception as e:
    print(f"Warning: PostgreSQL connection failed ({e}). Falling back to SQLite.")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    sqlite_path = os.path.join(base_dir, "smarthire_ai.db")
    FALLBACK_DB_URL = f"sqlite:///{sqlite_path}"
    engine = create_engine(FALLBACK_DB_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Auto-create tables for SQLite fallback if not present
try:
    Base.metadata.create_all(bind=engine)
except Exception:
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
