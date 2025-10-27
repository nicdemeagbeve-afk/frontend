from app import create_app, db
from app.models import Template

def init_templates():
    app = create_app()
    with app.app_context():
        # Vérifier si des templates existent déjà
        if Template.query.first() is not None:
            print("Des templates existent déjà dans la base de données.")
            return

        # Créer les templates par défaut
        templates = [
            {
                'name': 'Template Portfolio',
                'description': 'Un template élégant pour présenter vos projets et votre parcours professionnel.',
                'category': 'Portfolio',
                'path_folder': 'portfolio',
                'preview_url': '/static/img/templates/portfolio.jpg',
                'is_active': True
            },
            {
                'name': 'E-commerce Moderne',
                'description': 'Template optimisé pour la vente en ligne avec un design moderne et responsive.',
                'category': 'E-commerce',
                'path_folder': 'ecommerce',
                'preview_url': '/static/img/templates/ecommerce.jpg',
                'is_active': True
            },
            {
                'name': 'Blog Minimaliste',
                'description': 'Design épuré parfait pour les blogueurs et créateurs de contenu.',
                'category': 'Blog',
                'path_folder': 'blog',
                'preview_url': '/static/img/templates/blog.jpg',
                'is_active': True
            }
        ]

        # Ajouter les templates à la base de données
        for template_data in templates:
            template = Template(**template_data)
            db.session.add(template)

        try:
            db.session.commit()
            print("✅ Templates initialisés avec succès!")
            print(f"📊 {len(templates)} templates créés")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Erreur lors de l'initialisation des templates: {str(e)}")

if __name__ == '__main__':
    init_templates()