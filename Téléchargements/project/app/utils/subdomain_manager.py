import re
from flask import request, current_app
from app.models import Site

class SubdomainManager:
    """Gestionnaire pour les opérations liées aux sous-domaines"""
    
    # Liste des sous-domaines réservés
    RESERVED_SUBDOMAINS = {
        'www', 'admin', 'api', 'mail', 'ftp', 'blog', 'shop', 'store', 'app',
        'apps', 'dashboard', 'account', 'accounts', 'auth', 'login', 'logout',
        'register', 'signup', 'signin', 'webmail', 'cpanel', 'host', 'hosting',
        'support', 'help', 'docs', 'documentation', 'test', 'dev', 'development',
        'staging', 'prod', 'production', 'secure', 'ssl', 'static', 'assets',
        'media', 'files', 'img', 'images', 'js', 'css', 'cdn', 'cache', 'status',
        'monitor', 'stats', 'analytics', 'api-docs', 'admin-panel', 'control-panel'
    }
    
    @staticmethod
    def is_valid_subdomain(subdomain):
        """Valide le format d'un sous-domaine"""
        if not subdomain:
            return False
            
        if len(subdomain) < 3 or len(subdomain) > 63:
            return False
        
        # Seuls les caractères alphanumériques et tirets sont autorisés
        if not re.match(r'^[a-z0-9]([a-z0-9-]*[a-z0-9])?$', subdomain):
            return False
        
        # Vérifier si le sous-domaine est réservé
        if SubdomainManager.is_reserved(subdomain):
            return False
        
        return True
    
    @staticmethod
    def is_reserved(subdomain):
        """Vérifie si un sous-domaine est réservé"""
        return subdomain.lower() in SubdomainManager.RESERVED_SUBDOMAINS
    
    @staticmethod
    def generate_subdomain(name):
        """Génère un sous-domaine à partir d'un nom de site"""
        if not name:
            return "my-site"
        
        # Convertir en minuscules et remplacer les espaces par des tirets
        subdomain = name.lower().strip()
        
        # Remplacer les caractères spéciaux
        subdomain = re.sub(r'[^\w\s-]', '', subdomain)
        subdomain = re.sub(r'[-\s]+', '-', subdomain)
        
        # Supprimer les tirets en début et fin
        subdomain = subdomain.strip('-')
        
        # S'assurer de la longueur
        if len(subdomain) < 3:
            subdomain = f"{subdomain}-site"
        elif len(subdomain) > 63:
            subdomain = subdomain[:63].rstrip('-')
        
        return subdomain
    
    @staticmethod
    def get_available_subdomain(base_subdomain):
        """Trouve un sous-domaine disponible basé sur le sous-domaine de base"""
        if not SubdomainManager.is_valid_subdomain(base_subdomain):
            base_subdomain = "my-site"
        
        subdomain = base_subdomain
        counter = 1
        
        while not SubdomainManager.is_subdomain_available(subdomain):
            subdomain = f"{base_subdomain}-{counter}"
            counter += 1
            if counter > 100:  # Limite de sécurité
                raise ValueError("Impossible de trouver un sous-domaine disponible")
        
        return subdomain
    
    @staticmethod
    def is_subdomain_available(subdomain):
        """Vérifie si un sous-domaine est disponible"""
        if not SubdomainManager.is_valid_subdomain(subdomain):
            return False
        
        return not Site.query.filter_by(subdomain=subdomain).first()
    
    @staticmethod
    def get_site_from_subdomain():
        """Récupère le site basé sur le sous-domaine de la requête"""
        host = request.host
        base_domain = current_app.config.get('BASE_DOMAIN', 'miabesite.site')
        
        # Supprimer le port si présent (pour le développement)
        host = host.split(':')[0]
        base_domain = base_domain.split(':')[0]
        
        # Vérifier si l'hôte se termine par le domaine de base
        if host.endswith(base_domain):
            # Extraire le sous-domaine
            subdomain = host.replace(f'.{base_domain}', '')
            
            # Gérer les cas spéciaux (www, domaine nu)
            if not subdomain or subdomain in ['www', base_domain]:
                return None
            
            # Rechercher le site
            site = Site.query.filter_by(subdomain=subdomain, status='published').first()
            return site
        
        return None
    
    @staticmethod
    def validate_subdomain_creation(site_name, user):
        """Valide et prépare la création d'un sous-domaine"""
        if not user.can_create_site():
            raise ValueError("Vous avez atteint la limite de sites autorisés")
        
        # Générer le sous-domaine de base
        base_subdomain = SubdomainManager.generate_subdomain(site_name)
        
        # Obtenir un sous-domaine disponible
        subdomain = SubdomainManager.get_available_subdomain(base_subdomain)
        
        return subdomain