import os

class Config:
    """Base configuration with default settings."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'somekeybyArchit')
    DEBUG = False
    TESTING = False
    ALLOWED_EXTENSIONS = {'json', 'csv'}
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # Limit file uploads to 5MB

    # Database settings (optional, for future use)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///risk_score.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    """Configuration for development."""
    DEBUG = True
    ENV = 'development'


class TestingConfig(Config):
    """Configuration for testing."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


class ProductionConfig(Config):
    """Configuration for production."""
    DEBUG = False
    ENV = 'production'
    SECRET_KEY = os.environ.get('SECRET_KEY', 'change-this-in-prod')


# Dictionary to map environments
config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
}
