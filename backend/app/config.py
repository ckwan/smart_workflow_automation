import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# -------------------------------------------------------------------
# ENVIRONMENT VARIABLES
# -------------------------------------------------------------------
# Docs: https://12factor.net/config
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:postgres@db:5432/taskdb")
SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key") # Replace with a secure key in production
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES= 60

# -------------------------------------------------------------------
# DATABASE SETUP
# -------------------------------------------------------------------
# SQLAlchemy docs: https://docs.sqlalchemy.org/en/20/orm/session_basics.html
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
