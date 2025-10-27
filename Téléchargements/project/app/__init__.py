from flask import Flask, g, request, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
# Charger le fichier .env depuis la racine du projet
load_dotenv(env_file)

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
limiter = Limiter(key_func=get_remote_address)

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    # Forcer l'utilisation de la variable d'environnement DATABASE_URL (MySQL)
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        raise RuntimeError('DATABASE_URL non défini. Veuillez définir la variable d\'environnement DATABASE_URL dans votre fichier .env (ex: mysql+pymysql://user:pw@host:3306/dbname)')
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Configuration des sous-domaines
    app.config['SERVER_NAME'] = os.environ.get('SERVER_NAME', 'localhost:5000')
    app.config['BASE_DOMAIN'] = os.environ.get('BASE_DOMAIN', 'miabesite.site')
    app.config['APPLICATION_ROOT'] = '/'
    app.config['PREFERRED_URL_SCHEME'] = 'https' if os.environ.get('FLASK_ENV') == 'production' else 'http'
    
    # Activer le support des sous-domaines
    app.url_map.default_subdomain = 'www'
    
    # Initialisation des extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    limiter.init_app(app)
    
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'
    
    # Context processor pour rendre le site global disponible
    @app.context_processor
    def inject_site():
        site = getattr(g, 'site', None)
        return dict(current_site=site)
    
    # Middleware pour détecter les sous-domaines
    @app.before_request
    def before_request():
        # Réinitialiser g.site à chaque requête
        g.site = None
        g.site_subdomain = None
        
        # Détecter le sous-domaine
        from app.utils.subdomain_manager import SubdomainManager
        site = SubdomainManager.get_site_from_subdomain()
        
        if site:
            g.site = site
            g.site_subdomain = site.subdomain
    
    # Blueprints principaux (sans sous-domaine)
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.site_builder import builder_bp
    from app.routes.api import api_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(builder_bp, url_prefix='/builder')
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Blueprint pour les sites (avec sous-domaines)
    from app.routes.sites import sites_bp
    app.register_blueprint(sites_bp, subdomain='<subdomain>')
    
    # Gestion des erreurs pour les sous-domaines
    @app.errorhandler(404)
    def not_found_error(error):
        # Si c'est une requête sur un sous-domaine et que le site n'existe pas
        if hasattr(g, 'site_subdomain') and g.site_subdomain:
            return render_template('errors/404_subdomain.html', subdomain=g.site_subdomain), 404
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return render_template('errors/500.html'), 500
    
    return app