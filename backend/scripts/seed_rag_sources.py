# File: backend/scripts/seed_rag_sources.py

import sys
import os
import json
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sentence_transformers import SentenceTransformer
from app.database import SessionLocal
from app.models import RAGSource, SourceAddedBy


def seed_rag_sources():
    """Seed the rag_sources table with credible academic sources."""
    
    db = SessionLocal()
    
    # Check if already seeded
    existing_count = db.query(RAGSource).count()
    if existing_count > 0:
        print(f"✅ RAG sources table already seeded ({existing_count} sources)")
        db.close()
        return
    
    # Load seed data
    data_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "data", "rag_sources.json")
    
    if not os.path.exists(data_file):
        print(f"❌ Seed data file not found: {data_file}")
        print("   Please make sure data/rag_sources.json exists")
        db.close()
        return
    
    with open(data_file, 'r', encoding='utf-8') as f:
        sources_data = json.load(f)
    
    print(f"📚 Loaded {len(sources_data)} sources from seed data")
    
    # Load embedding model
    print("🤖 Loading embedding model (this may take a minute)...")
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    print("✅ Model loaded!")
    
    # Create RAG sources with embeddings ONE BY ONE (not bulk)
    for idx, source_data in enumerate(sources_data, 1):
        # Generate embedding from title + abstract
        text_to_embed = f"{source_data['title']}. {source_data['abstract']}"
        embedding = model.encode(text_to_embed)
        
        # Convert numpy array to Python list, then to string for pgvector
        embedding_list = embedding.tolist()
        
        source = RAGSource(
            url=source_data['url'],
            title=source_data['title'],
            content_text=source_data['abstract'],
            embedding_vector=embedding_list,  # pgvector will handle the conversion
            domain=source_data['domain'],
            credibility_score=source_data['credibility_score'],
            added_by=SourceAddedBy.manual
        )
        
        # Add and commit one by one
        db.add(source)
        
        if idx % 10 == 0:
            print(f"   Processed {idx}/{len(sources_data)} sources...")
            db.commit()  # Commit every 10
    
    # Final commit
    db.commit()
    
    print(f"✅ Seeded {len(sources_data)} sources into rag_sources table")
    db.close()


if __name__ == "__main__":
    print("🌱 Seeding RAG sources data...")
    print("⚠️  This will download the embedding model (~90MB) on first run")
    seed_rag_sources()
    print("✅ RAG seeding complete!")