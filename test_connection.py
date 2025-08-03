

import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")

if not DATABASE_URI:
    raise ValueError("SQLALCHEMY_DATABASE_URI not found in environment variables")

try:
    engine = create_engine(DATABASE_URI)
    connection = engine.connect()
    print("✅ Database connection successful!")
    connection.close()
except Exception as e:
    print("❌ Database connection failed:", str(e))