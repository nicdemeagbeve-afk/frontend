from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json
import re

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    role = db.Column(db.String(20), default='user')
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    is_verified = db.Column(db.Boolean, default=False)
    
    sites = db.relationship('Site', backref='owner', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def can_create_site(self):
        """Vérifie si l'utilisateur peut créer un nouveau site"""
        max_sites = 3 if self.role == 'user' else 10
        return self.sites.count() < max_sites
    
    def get_published_sites(self):
        """Retourne les sites publiés de l'utilisateur"""
        return self.sites.filter_by(status='published').all()

class Site(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    subdomain = db.Column(db.String(100), unique=True, nullable=False)
    template_id = db.Column(db.Integer, db.ForeignKey('template.id'))
    content_json = db.Column(db.Text)
    status = db.Column(db.String(20), default='draft')  # draft, published, archived
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relation avec Template
    template = db.relationship('Template', backref='sites')
    
    def get_content(self):
        """Retourne le contenu du site sous forme de dictionnaire"""
        if self.content_json:
            try:
                return json.loads(self.content_json)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def set_content(self, content_dict):
        """Définit le contenu du site"""
        self.content_json = json.dumps(content_dict)
    
    def publish(self):
        """Publie le site"""
        self.status = 'published'
        self.date_updated = datetime.utcnow()
        db.session.commit()
    
    def unpublish(self):
        """Dépublie le site"""
        self.status = 'draft'
        self.date_updated = datetime.utcnow()
        db.session.commit()
    
    def is_published(self):
        """Vérifie si le site est publié"""
        return self.status == 'published'
    
    def is_ecommerce_ready(self):
        """Vérifie si le site e-commerce est prêt à être publié"""
        content = self.get_content()
        
        # Vérifications de base pour l'e-commerce
        required_fields = [
            'store_name', 'hero_title', 'hero_subtitle',
            'products', 'contact_email'
        ]
        
        for field in required_fields:
            if not content.get(field):
                return False
        
        # Vérifier qu'il y a au moins un produit
        products = content.get('products', [])
        if len(products) == 0:
            return False
        
        # Vérifier que chaque produit a les champs requis
        for product in products:
            if not all(key in product for key in ['name', 'price', 'description']):
                return False
        
        return True
    
    def add_default_ecommerce_content(self):
        """Ajoute un contenu e-commerce par défaut"""
        default_content = {
            'store_name': self.name,
            'hero_title': 'Bienvenue dans notre boutique',
            'hero_subtitle': 'Découvrez nos produits exceptionnels',
            'about_title': 'À propos de notre boutique',
            'about_description': 'Nous nous engageons à vous offrir les meilleurs produits avec un service client exceptionnel.',
            'contact_email': 'contact@example.com',
            'contact_phone': '+33 1 23 45 67 89',
            'contact_address': '123 Rue du Commerce, 75000 Paris',
            'products': [
                {
                    'id': 1,
                    'name': 'Produit Exemplaire',
                    'price': 29.99,
                    'description': 'Description de votre produit phare',
                    'image': '/static/images/default-product.jpg',
                    'category': 'Général',
                    'in_stock': True,
                    'features': ['Haute qualité', 'Livraison rapide', 'Garantie satisfait ou remboursé']
                }
            ],
            'style': {
                'primary_color': '#667eea',
                'secondary_color': '#764ba2',
                'text_color': '#333333',
                'bg_color': '#ffffff',
                'font_family': "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"
            },
            'payment_methods': ['Carte bancaire', 'PayPal', 'Virement'],
            'shipping_info': 'Livraison sous 2-3 jours ouvrés',
            'return_policy': '30 jours pour changer d\'avis'
        }
        self.set_content(default_content)
    
    @staticmethod
    def generate_subdomain(name, user_id):
        """Génère un sous-domaine unique à partir du nom du site"""
        from app.utils.subdomain_manager import SubdomainManager
        
        # Générer le sous-domaine de base
        base_subdomain = SubdomainManager.generate_subdomain(name)
        
        # Vérifier et ajuster pour l'unicité
        subdomain = base_subdomain
        counter = 1
        
        while Site.query.filter_by(subdomain=subdomain).first():
            subdomain = f"{base_subdomain}-{counter}"
            counter += 1
            if counter > 100:  # Limite de sécurité
                raise ValueError("Impossible de générer un sous-domaine unique")
        
        return subdomain
    
    def get_url(self, base_domain=None):
        """Retourne l'URL complète du site"""
        if not base_domain:
            from flask import current_app
            base_domain = current_app.config.get('BASE_DOMAIN', 'miabesite.site')
        return f"https://{self.subdomain}.{base_domain}"
    
    def to_dict(self):
        """Retourne les données du site sous forme de dictionnaire"""
        return {
            'id': self.id,
            'name': self.name,
            'subdomain': self.subdomain,
            'template_id': self.template_id,
            'status': self.status,
            'date_created': self.date_created.isoformat(),
            'date_updated': self.date_updated.isoformat(),
            'url': self.get_url(),
            'content': self.get_content()
        }

class Template(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    path_folder = db.Column(db.String(200))
    preview_url = db.Column(db.String(200))
    category = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, default=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Retourne les données du template sous forme de dictionnaire"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'preview_url': self.preview_url,
            'is_active': self.is_active
        }

class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    site_id = db.Column(db.Integer, db.ForeignKey('site.id'))
    action = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relations
    user = db.relationship('User', backref='logs')
    site = db.relationship('Site', backref='logs')

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))