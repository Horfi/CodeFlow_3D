# backend/src/config.py
import os
from datetime import timedelta

class Config:
    """Base configuration class"""
    
    # Basic Flask config
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = False
    TESTING = False
    
    # Database configuration
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'sqlite:///codeflow.db'
    
    # File storage paths
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    REPOSITORY_STORAGE = os.path.join(BASE_DIR, '../../data/repositories')
    CACHE_STORAGE = os.path.join(BASE_DIR, '../../data/cache')
    ANALYTICS_STORAGE = os.path.join(BASE_DIR, '../../data/analytics')
    
    # Git repository settings
    MAX_REPOSITORY_SIZE = 500 * 1024 * 1024  # 500MB
    ALLOWED_FILE_EXTENSIONS = {
        '.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.cpp', '.c', '.h',
        '.css', '.scss', '.html', '.php', '.rb', '.go', '.rs', '.swift',
        '.json', '.xml', '.yml', '.yaml', '.md', '.txt'
    }
    
    # Graph processing settings
    MAX_NODES = 10000
    MAX_EDGES = 50000
    CENTRALITY_ITERATIONS = 100
    
    # User model settings
    USER_MODEL_UPDATE_INTERVAL = 300  # 5 minutes
    INTERACTION_BATCH_SIZE = 50
    MAX_USER_SESSIONS = 1000
    
    # Analytics settings
    ANALYTICS_BATCH_SIZE = 100
    ANALYTICS_FLUSH_INTERVAL = 60  # seconds
    MAX_ANALYTICS_RETENTION_DAYS = 90
    
    # API rate limiting
    RATELIMIT_STORAGE_URL = 'memory://'
    RATELIMIT_DEFAULT = '1000 per hour'
    
    # CORS settings
    CORS_ORIGINS = ['http://localhost:3000', 'http://127.0.0.1:3000']
    
    # Security settings
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None
    
    # Logging
    LOG_LEVEL = 'INFO'
    LOG_FILE = 'codeflow.log'
    
    @staticmethod
    def init_app(app):
        """Initialize app-specific configuration"""
        pass

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'
    
    # Development database
    DATABASE_URL = 'sqlite:///codeflow_dev.db'
    
    # Enable all CORS origins in development
    CORS_ORIGINS = ['*']

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    WTF_CSRF_ENABLED = False
    
    # In-memory database for testing
    DATABASE_URL = 'sqlite:///:memory:'
    
    # Smaller limits for testing
    MAX_REPOSITORY_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_NODES = 1000
    MAX_EDGES = 5000

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    
    # Production database from environment
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'sqlite:///codeflow_prod.db'
    
    # Stricter CORS in production
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '').split(',')
    
    # Production logging
    LOG_LEVEL = 'WARNING'
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # Log to syslog in production
        import logging
        from logging.handlers import SysLogHandler
        syslog_handler = SysLogHandler()
        syslog_handler.setLevel(logging.WARNING)
        app.logger.addHandler(syslog_handler)

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}