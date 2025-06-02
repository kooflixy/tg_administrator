import os
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseModel):
    #db
    DB_HOST: str = os.getenv("DB_HOST")
    DB_PORT: int = int(os.getenv("DB_PORT"))
    DB_USER: str = os.getenv("DB_USER")
    DB_PASS: str = os.getenv("DB_PASS")
    DB_NAME: str = os.getenv("DB_NAME")
    
    ADMIN_ID: int = int(os.getenv("ADMIN_ID"))
    TG_BOT_API_TOKEN: str = os.getenv("TG_BOT_API_TOKEN")

settings = Settings()