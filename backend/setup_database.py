# File: backend/setup_database.py

"""
One-command database setup script.
Run this after creating .env file to set up your entire database.
"""

import subprocess
import sys
import os

def run_command(description, command):
    """Run a shell command and handle errors."""
    print(f"\n{'='*60}")
    print(f"🚀 {description}")
    print(f"{'='*60}")
    
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ Error: {result.stderr}")
        return False
    
    print(result.stdout)
    print(f"✅ {description} - DONE")
    return True

def main():
    print("""
╔══════════════════════════════════════════════════════════╗
║     REFERENCE CHECKER - DATABASE SETUP SCRIPT            ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    # Check if .env exists
    if not os.path.exists(".env"):
        print("❌ .env file not found!")
        print("   Please create .env file with your DATABASE_URL and API keys")
        print("   See .env.example for template")
        sys.exit(1)
    
    print("✅ .env file found")
    
    # Step 1: Initialize Alembic (if not already done)
    print("\n📋 Step 1: Initialize Alembic migrations")
    if not os.path.exists("migrations/versions"):
        os.makedirs("migrations/versions", exist_ok=True)
        run_command(
            "Initializing Alembic",
            "alembic init migrations"
        )
    else:
        print("✅ Alembic already initialized")
    
    # Step 2: Create initial migration
    print("\n📋 Step 2: Generate database migration")
    run_command(
        "Creating initial migration",
        'alembic revision --autogenerate -m "Initial schema"'
    )
    
    # Step 3: Run migrations
    print("\n📋 Step 3: Apply database migrations")
    if not run_command(
        "Running migrations",
        "alembic upgrade head"
    ):
        print("\n⚠️  Migration failed. Check your DATABASE_URL in .env")
        sys.exit(1)
    
    # Step 4: Seed domains
    print("\n📋 Step 4: Seed domain reputation data")
    if not run_command(
        "Seeding domains",
        "python scripts/seed_domains.py"
    ):
        print("\n⚠️  Domain seeding failed")
        sys.exit(1)
    
    # Step 5: Seed RAG sources
    print("\n📋 Step 5: Seed RAG sources (this may take 2-3 minutes)")
    print("⏳ Downloading embedding model...")
    if not run_command(
        "Seeding RAG sources",
        "python scripts/seed_rag_sources.py"
    ):
        print("\n⚠️  RAG seeding failed")
        sys.exit(1)
    
    # Success!
    print(f"""
{'='*60}
✅ DATABASE SETUP COMPLETE!
{'='*60}

Your database now has:
  • All tables created (users, references, reports, etc.)
  • ~40 known domains (academic, government, news)
  • 50 credible academic sources for RAG

🚀 Next steps:
  1. Run the backend: python -m uvicorn app.main:app --reload
  2. Test at: http://localhost:8000
  3. API docs: http://localhost:8000/docs

Happy coding! 🎉
    """)

if __name__ == "__main__":
    main()