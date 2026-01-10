from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
print(f"Connecting to: {DATABASE_URL[:30]}...")

engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    result = conn.execute(text("SELECT version();"))
    print("✅ Connected to PostgreSQL!")
    print(result.fetchone()[0])
    
    result = conn.execute(text("SELECT * FROM pg_extension WHERE extname = 'vector';"))
    if result.fetchone():
        print("✅ pgvector extension is installed!")
    else:
        print("❌ pgvector extension not found")

print("\n🎉 Database connection successful!")