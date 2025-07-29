from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import DATABASE_URL
import redis
from bcrypt import checkpw, gensalt, hashpw
redis_client = redis.Redis(host='localhost', port=6379, db=0)

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
salt = gensalt()

def verify_password(password: str, hashed):
    return checkpw(password.encode('utf-8'), hashed)

def hash_password(password: str):
    return hashpw(password.encode('utf-8'), salt)