import os
from dotenv import load_dotenv

load_dotenv()

OPEN_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPEN_API_KEY:
    print("[WARN] OPENAI_API_KEY is not set. Please check your .env file.")