"""
Configuration settings for the Russian Roulette Flask application.

This module contains configuration classes for different environments
(development, production, testing) and application settings.
"""

import os
import secrets
from datetime import timedelta


class Config:
    """Base configuration class with common settings."""

    # Secret key for session management and CSRF protection
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)

    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # Application settings
    MAX_PLAYERS = 6
    MIN_PLAYERS = 2
    CHAMBER_COUNT = 6

    # JSON settings
    JSON_SORT_KEYS = False
    JSONIFY_PRETTYPRINT_REGULAR = True

    # Template settings
    TEMPLATES_AUTO_RELOAD = True


class DevelopmentConfig(Config):
    """Development environment configuration."""

    DEBUG = True
    TESTING = False

    # More verbose logging in development
    LOG_LEVEL = 'DEBUG'

    # Allow insecure session cookies for development
    SESSION_COOKIE_SECURE = False


class ProductionConfig(Config):
    """Production environment configuration."""

    DEBUG = False
    TESTING = False

    # Security settings for production
    SESSION_COOKIE_SECURE = True  # Requires HTTPS
    SESSION_COOKIE_HTTPONLY = True

    # Logging
    LOG_LEVEL = 'WARNING'

    # Override secret key check for production
    if not os.environ.get('SECRET_KEY'):
        raise ValueError("No SECRET_KEY set for production environment")


class TestingConfig(Config):
    """Testing environment configuration."""

    TESTING = True
    DEBUG = True

    # Use in-memory database for testing
    WTF_CSRF_ENABLED = False

    # Faster password hashing for tests
    SESSION_COOKIE_SECURE = False


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config():
    """Get the configuration class based on environment variable."""
    env = os.environ.get('FLASK_ENV', 'development').lower()
    return config.get(env, config['default'])
