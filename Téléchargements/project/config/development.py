class DevelopmentConfig:
    # Security
    SECRET_KEY = 'dev-secret-key-change-in-production'
    
    # Database
    # Use DATABASE_URL env (MySQL) in development as well. No sqlite fallback.
    import os
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    if not SQLALCHEMY_DATABASE_URI:
        raise RuntimeError('DATABASE_URL non défini. Définissez la variable d\'environnement dans .env')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Subdomain
    BASE_DOMAIN = 'localhost:5000'
    
    # Debug
    DEBUG = True
    TESTING = False
    
    # File upload
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    UPLOAD_FOLDER = 'app/static/uploads'
    
    # Session
    SESSION_COOKIE_SECURE = False