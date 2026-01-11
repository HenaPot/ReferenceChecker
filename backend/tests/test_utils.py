# File: backend/tests/test_utils.py

import pytest
from datetime import datetime, timedelta
from app.utils.security import hash_password, verify_password, create_access_token, decode_access_token
from fastapi import HTTPException


class TestPasswordHashing:
    """Test password hashing utilities."""
    
    def test_hash_password_creates_hash(self):
        """Test that hash_password creates a hash."""
        password = "mySecurePassword123"
        hashed = hash_password(password)
        
        assert hashed != password  # Should be different
        assert len(hashed) > 20  # Should be a reasonable length
        assert hashed.startswith("$2b$")  # bcrypt format
    
    def test_hash_password_different_each_time(self):
        """Test that same password generates different hashes (due to salt)."""
        password = "samePassword"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        
        assert hash1 != hash2  # Different due to random salt
    
    def test_verify_password_correct(self):
        """Test verifying correct password."""
        password = "correctPassword"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) == True
    
    def test_verify_password_incorrect(self):
        """Test verifying incorrect password."""
        password = "correctPassword"
        wrong_password = "wrongPassword"
        hashed = hash_password(password)
        
        assert verify_password(wrong_password, hashed) == False
    
    def test_verify_password_empty_string(self):
        """Test verifying empty password."""
        password = "password123"
        hashed = hash_password(password)
        
        assert verify_password("", hashed) == False


class TestJWTTokens:
    """Test JWT token creation and validation."""
    
    def test_create_access_token(self):
        """Test creating an access token."""
        data = {"sub": "user123"}
        token = create_access_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 20
        assert token.count('.') == 2  # JWT has 3 parts separated by dots
    
    def test_decode_access_token_valid(self):
        """Test decoding a valid token."""
        data = {"sub": "user123", "email": "test@example.com"}
        token = create_access_token(data)
        
        decoded = decode_access_token(token)
        
        assert decoded["sub"] == "user123"
        assert decoded["email"] == "test@example.com"
        assert "exp" in decoded  # Should have expiration
    
    def test_decode_access_token_invalid(self):
        """Test decoding an invalid token raises exception."""
        invalid_token = "this.is.invalid"
        
        with pytest.raises(HTTPException) as exc_info:
            decode_access_token(invalid_token)
        
        assert exc_info.value.status_code == 401
    
    def test_token_expiration(self):
        """Test that token includes expiration."""
        data = {"sub": "user123"}
        token = create_access_token(data, expires_delta=timedelta(hours=1))
        
        decoded = decode_access_token(token)
        
        assert "exp" in decoded
        # Expiration should be in the future
        exp_timestamp = decoded["exp"]
        assert exp_timestamp > datetime.utcnow().timestamp()


class TestSchemaValidation:
    """Test Pydantic schema validation."""
    
    def test_user_schema_validation(self):
        """Test UserCreate schema validation."""
        from app.schemas.user import UserCreate
        
        # Valid user
        valid_user = UserCreate(
            email="test@example.com",
            password="password123"
        )
        
        assert valid_user.email == "test@example.com"
        assert valid_user.password == "password123"
    
    def test_user_schema_invalid_email(self):
        """Test UserCreate rejects invalid email."""
        from app.schemas.user import UserCreate
        from pydantic import ValidationError
        
        with pytest.raises(ValidationError):
            UserCreate(
                email="not-an-email",  # Invalid
                password="password123"
            )
    
    def test_reference_schema_validation(self):
        """Test ReferenceCreate schema validation."""
        from app.schemas.reference import ReferenceCreate
        
        valid_ref = ReferenceCreate(
            url="https://www.nature.com/articles/test"
        )
        
        assert valid_ref.url == "https://www.nature.com/articles/test"
    
    def test_reference_schema_accepts_various_urls(self):
        """Test ReferenceCreate accepts various URL formats."""
        from app.schemas.reference import ReferenceCreate
        
        # Schema is permissive - accepts various formats
        urls = [
            "https://www.nature.com/articles/test",
            "http://arxiv.org/abs/2401.12345",
            "www.example.com",  # Even without protocol
        ]
        
        for url in urls:
            ref = ReferenceCreate(url=url)
            assert ref.url == url


class TestConfigSettings:
    """Test configuration settings."""
    
    def test_settings_loaded(self):
        """Test that settings are loaded correctly."""
        from app.config import settings
        
        assert settings.JWT_SECRET_KEY is not None
        assert settings.JWT_ALGORITHM == "HS256"
        assert settings.JWT_EXPIRATION_HOURS > 0
        assert settings.DATABASE_URL is not None
    
    def test_settings_has_embedding_model(self):
        """Test that embedding model is configured."""
        from app.config import settings
        
        assert hasattr(settings, 'EMBEDDING_MODEL')
        assert settings.EMBEDDING_MODEL is not None


class TestDomainExtraction:
    """Test domain extraction logic."""
    
    def test_extract_domain_from_url(self):
        """Test extracting domain from various URLs."""
        from urllib.parse import urlparse
        
        test_cases = [
            ("https://www.nature.com/articles/test", "nature.com"),
            ("https://arxiv.org/abs/2401.12345", "arxiv.org"),
            ("http://www.cdc.gov/health", "cdc.gov"),
            ("https://www.example.com/path/to/page", "example.com"),
        ]
        
        for url, expected_domain in test_cases:
            domain = urlparse(url).netloc.replace('www.', '').lower()
            assert domain == expected_domain
    
    def test_extract_domain_handles_subdomains(self):
        """Test that subdomain extraction works."""
        from urllib.parse import urlparse
        
        url = "https://blog.example.com/post"
        domain = urlparse(url).netloc.lower()
        
        assert domain == "blog.example.com"


class TestEnumTypes:
    """Test enum types work correctly."""
    
    def test_domain_category_enum(self):
        """Test DomainCategory enum."""
        from app.models.domain_reputation import DomainCategory
        
        assert DomainCategory.academic.value == "academic"
        assert DomainCategory.government.value == "government"
        assert DomainCategory.news.value == "news"
        assert DomainCategory.unknown.value == "unknown"
    
    def test_reference_status_enum(self):
        """Test ReferenceStatus enum."""
        from app.models.reference import ReferenceStatus
        
        assert ReferenceStatus.processing.value == "processing"
        assert ReferenceStatus.completed.value == "completed"
        assert ReferenceStatus.failed.value == "failed"


class TestCredibilityScoring:
    """Test credibility scoring logic (without database)."""
    
    def test_credibility_level_calculation(self):
        """Test credibility level based on score percentage."""
        def get_credibility_level(score: int, max_score: int) -> str:
            percentage = (score / max_score) * 100
            
            if percentage >= 80:
                return "highly_credible"
            elif percentage >= 60:
                return "credible"
            elif percentage >= 40:
                return "questionable"
            elif percentage >= 20:
                return "unreliable"
            else:
                return "highly_unreliable"
        
        assert get_credibility_level(90, 100) == "highly_credible"
        assert get_credibility_level(70, 100) == "credible"
        assert get_credibility_level(50, 100) == "questionable"
        assert get_credibility_level(30, 100) == "unreliable"
        assert get_credibility_level(10, 100) == "highly_unreliable"
    
    def test_score_boundaries(self):
        """Test edge cases for score calculation."""
        def get_credibility_level(score: int, max_score: int) -> str:
            percentage = (score / max_score) * 100
            
            if percentage >= 80:
                return "highly_credible"
            elif percentage >= 60:
                return "credible"
            elif percentage >= 40:
                return "questionable"
            elif percentage >= 20:
                return "unreliable"
            else:
                return "highly_unreliable"
        
        # Boundary tests
        assert get_credibility_level(80, 100) == "highly_credible"
        assert get_credibility_level(79, 100) == "credible"
        assert get_credibility_level(60, 100) == "credible"
        assert get_credibility_level(59, 100) == "questionable"