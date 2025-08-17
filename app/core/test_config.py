"""
Test configuration that overrides the main settings for testing.
"""
from pydantic_settings import BaseSettings


class TestSettings(BaseSettings):
    # API Configuration
    API_V1_STR: str = "/api/v1"

    # Security Configuration
    SECRET_KEY: str = "test_secret_key_for_testing_only"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Environment
    ENVIRONMENT: str = "testing"

    # Database configuration - will use SQLite in memory for tests
    POSTGRES_USER: str = "test_user"
    POSTGRES_PASSWORD: str = "test_password"
    POSTGRES_DB: str = "test_db"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432

    # Default superuser configuration for tests
    FIRST_SUPERUSER_USERNAME: str = "admin"
    FIRST_SUPERUSER_EMAIL: str = "admin@example.com"
    FIRST_SUPERUSER_PASSWORD: str = "admin123"
    FIRST_SUPERUSER_FULL_NAME: str = "System Administrator"

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        # Tests will override this with SQLite in memory
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    class Config:
        case_sensitive = True
        env_file = ".env.test"


# Create test settings instance
test_settings = TestSettings()
