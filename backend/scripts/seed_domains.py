# File: backend/scripts/seed_domains.py

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import SessionLocal
from app.models import DomainReputation, DomainCategory


def seed_domains():
    """Seed the domain_reputation table with known domains."""
    
    db = SessionLocal()
    
    # Check if already seeded
    existing_count = db.query(DomainReputation).count()
    if existing_count > 0:
        print(f"✅ Domain reputation table already seeded ({existing_count} domains)")
        db.close()
        return
    
    domains_data = [
        # Academic (score: 30)
        ("nature.com", DomainCategory.academic, 30, True),
        ("science.org", DomainCategory.academic, 30, True),
        ("sciencemag.org", DomainCategory.academic, 30, True),
        ("cell.com", DomainCategory.academic, 30, True),
        ("pnas.org", DomainCategory.academic, 30, True),
        ("nejm.org", DomainCategory.academic, 30, True),
        ("thelancet.com", DomainCategory.academic, 30, True),
        ("arxiv.org", DomainCategory.academic, 30, True),
        ("academic.oup.com", DomainCategory.academic, 30, True),
        ("journals.plos.org", DomainCategory.academic, 30, True),
        ("ieeexplore.ieee.org", DomainCategory.academic, 30, True),
        ("sciencedirect.com", DomainCategory.academic, 30, True),
        ("ams.org", DomainCategory.academic, 30, True),
        ("journals.aps.org", DomainCategory.academic, 30, True),
        ("annualreviews.org", DomainCategory.academic, 30, True),
        ("jneurosci.org", DomainCategory.academic, 30, True),
        ("frontiersin.org", DomainCategory.academic, 28, True),
        ("journals.sagepub.com", DomainCategory.academic, 28, True),
        ("cambridge.org", DomainCategory.academic, 30, True),
        ("iopscience.iop.org", DomainCategory.academic, 28, True),
        
        # Government (score: 30)
        ("nih.gov", DomainCategory.government, 30, True),
        ("cdc.gov", DomainCategory.government, 30, True),
        ("nasa.gov", DomainCategory.government, 30, True),
        ("nsf.gov", DomainCategory.government, 30, True),
        ("fda.gov", DomainCategory.government, 30, True),
        ("epa.gov", DomainCategory.government, 30, True),
        ("noaa.gov", DomainCategory.government, 30, True),
        ("usgs.gov", DomainCategory.government, 30, True),
        
        # News (score: 25)
        ("reuters.com", DomainCategory.news, 25, True),
        ("apnews.com", DomainCategory.news, 25, True),
        ("bbc.com", DomainCategory.news, 25, True),
        ("npr.org", DomainCategory.news, 25, True),
        ("pbs.org", DomainCategory.news, 25, True),
        
        # Known unreliable (score: 0)
        ("example-fake-news.com", DomainCategory.unreliable, 0, True),
        ("conspiracy-theory-site.com", DomainCategory.unreliable, 0, True),
    ]
    
    domains = []
    for domain_name, category, score, verified in domains_data:
        domain = DomainReputation(
            domain_name=domain_name,
            category=category,
            base_score=score,
            is_verified=verified
        )
        domains.append(domain)
    
    db.bulk_save_objects(domains)
    db.commit()
    
    print(f"✅ Seeded {len(domains)} domains into domain_reputation table")
    db.close()


if __name__ == "__main__":
    print("🌱 Seeding domain reputation data...")
    seed_domains()
    print("✅ Domain seeding complete!")