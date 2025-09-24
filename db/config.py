from dotenv import load_dotenv
import os

load_dotenv()  # читает .env из корня проекта

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set in .env")
