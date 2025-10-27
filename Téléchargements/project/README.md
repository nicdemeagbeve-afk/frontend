# 🚀 MiabeSite - Constructeur de Sites Web

MiabeSite est une plateforme web moderne qui permet à tout utilisateur de créer et gérer facilement son site web (vitrine, portfolio, boutique) sans compétences techniques.

## ✨ Fonctionnalités

- 🎨 **Création visuelle** - Interface drag-and-drop intuitive
- 📱 **Responsive design** - Sites optimisés mobile-first
- 🎯 **Wizard en 4 étapes** - Processus guidé de création
- 🌐 **Sous-domaines automatiques** - username.miabesite.site
- 💾 **Sauvegarde automatique** - Ne perdez jamais votre travail
- 🛡️ **Sécurisé** - HTTPS, validation, protection des données
- 📊 **Tableau de bord** - Gestion complète de vos sites

## 🛠️ Stack Technique

- **Backend:** Flask (Python)
- **Frontend:** HTML5, Bootstrap 5, JavaScript
- **Base de données:** MySQL (via PyMySQL / SQLAlchemy)
- **Serveur:** Ubuntu + Nginx + Gunicorn
- **Hébergement:** VPS Contabo

## 🚀 Installation

### Développement local

1. **Cloner le repository**
```bash
git clone https://github.com/votre-repo/miabesite.git
cd miabesite

    Créer l'environnement virtuel

bash

python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

    Installer les dépendances

bash

pip install -r requirements.txt

    Configuration

bash

cp .env.example .env
# Éditer .env avec vos configurations

    Initialiser la base de données

bash

flask db init
flask db migrate -m "Initial migration"
flask db upgrade
python scripts/init_db.py

    Lancer l'application

bash

    # Option A: utiliser le helper PowerShell sous Windows
    # Depuis la racine du projet
    .\scripts\run_local.ps1 python run.py

    # Ou lancer directement (en s'assurant que PYTHONPATH est défini)
    python run.py

Avec Docker
bash

docker-compose up --build

📁 Structure du Projet
text

miabesite/
├── app/                 # Application Flask
│   ├── routes/         # Blueprints et routes
│   ├── templates/      # Templates Jinja2
│   ├── static/         # Fichiers statiques
│   ├── models.py       # Modèles de données
│   └── utils/          # Utilitaires
├── migrations/         # Migrations de base de données
├── tests/              # Tests unitaires
├── scripts/            # Scripts d'administration
└── requirements.txt    # Dépendances Python

🎯 Utilisation
Créer un site web

    Inscription/Connexion

        Créez un compte gratuit

        Validez votre email

    Création du site

        Choisissez un template

        Personnalisez le contenu

        Ajustez le style

        Publiez en un clic

    Gestion

        Modifiez à tout moment

        Dupliquez vos sites

        Suivez les statistiques

Templates disponibles

    🎨 Portfolio Moderne - Présentez vos projets

    💼 Site Vitrine - Idéal pour les entreprises

    📝 Blog Personnel - Partagez vos articles

    🛍️ Boutique en ligne - Vendez vos produits

🔧 Configuration
Variables d'environnement
env

SECRET_KEY=votre-cle-secrete
DATABASE_URL=mysql+pymysql://root:password@127.0.0.1:3306/miabesite_db
BASE_DOMAIN=miabesite.site
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=votre-email
MAIL_PASSWORD=votre-mot-de-passe

Déploiement en production

    Préparer le serveur

bash

# Mettre à jour le système
sudo apt update && sudo apt upgrade -y

# Installer les dépendances
sudo apt install nginx postgresql python3-pip certbot

    Configurer la base de données

bash

sudo -u postgres createdb miabesite
sudo -u postgres createuser -P miabesite

    Déployer l'application

bash

# Cloner le code
git clone https://github.com/votre-repo/miabesite.git /var/www/miabesite

# Installer les dépendances
pip install -r requirements.txt

# Configurer Nginx
sudo cp nginx.conf /etc/nginx/sites-available/miabesite
sudo ln -s /etc/nginx/sites-available/miabesite /etc/nginx/sites-enabled/

# Obtenir le certificat SSL
sudo certbot --nginx -d miabesite.site -d *.miabesite.site

# Démarrer les services
sudo systemctl restart nginx
sudo systemctl enable nginx

🧪 Tests
bash

# Lancer tous les tests
pytest

# Tests avec couverture
pytest --cov=app tests/

# Tests spécifiques
pytest tests/test_auth.py
pytest tests/test_builder.py

📈 Évolutions Futures

    Plans payants avec domaines personnalisés

    Assistant IA pour la création de contenu

    Marketplace de templates

    API publique

    E-commerce avancé

    Blog intégré

    Analytics détaillés

🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :

    Fork le projet

    Créer une branche feature (git checkout -b feature/AmazingFeature)

    Commit vos changements (git commit -m 'Add some AmazingFeature')

    Push sur la branche (git push origin feature/AmazingFeature)

    Ouvrir une Pull Request

📄 Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.
🆘 Support

    📧 Email: support@miabesite.site

    🐛 Issues: GitHub Issues

    📚 Documentation: Wiki

🙏 Remerciements

    Flask - Framework web Python

    Bootstrap - Framework CSS

    PostgreSQL - Base de données

    Let's Encrypt - Certificats SSL gratuits

MiabeSite - Créé avec ❤️ pour rendre la création de sites web accessible à tous.

## 17. Fichiers de Configuration Final

### `config/production.py`
```python
import os

class ProductionConfig:
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Subdomain
    BASE_DOMAIN = os.environ.get('BASE_DOMAIN', 'miabesite.site')
    
    # File upload
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    UPLOAD_FOLDER = '/var/www/miabesite/uploads'
    
    # Session
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Rate limiting
    RATELIMIT_STORAGE_URL = 'memory://'
    
    # Logging
    LOG_LEVEL = 'INFO'
    LOG_FORMAT = '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'