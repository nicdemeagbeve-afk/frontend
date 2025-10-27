import os

class ProductionConfig:
    # Sécurité
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # Base de données
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Sous-domaines
    SERVER_NAME = os.environ.get('SERVER_NAME', 'miabesite.site')
    BASE_DOMAIN = os.environ.get('BASE_DOMAIN', 'miabesite.site')
    APPLICATION_ROOT = '/'
    PREFERRED_URL_SCHEME = 'https'
    
    # Upload de fichiers
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = '/var/www/miabesite/uploads'
    
    # Session
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Rate limiting
    RATELIMIT_STORAGE_URL = 'memory://'
    
    # Logging
    LOG_LEVEL = 'INFO'