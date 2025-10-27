from app import db
from app.models import User, Site, Template

def init_sample_data():
    """Initialize sample data for development"""
    
    # Create sample templates
    templates = [
        Template(
            name="Portfolio Moderne",
            description="Template parfait pour présenter vos projets et compétences",
            category="portfolio",
            preview_url="/static/img/template1-preview.jpg"
        ),
        Template(
            name="Site Vitrine",
            description="Template élégant pour les petites entreprises et freelances",
            category="business",
            preview_url="/static/img/template2-preview.jpg"
        ),
        Template(
            name="Blog Personnel",
            description="Template idéal pour partager vos articles et réflexions",
            category="blog",
            preview_url="/static/img/template3-preview.jpg"
        )
    ]
    
    for template in templates:
        if not Template.query.filter_by(name=template.name).first():
            db.session.add(template)
    
    db.session.commit()

def get_user_sites(user_id):
    """Get all sites for a user with template information"""
    return Site.query.filter_by(user_id=user_id).join(Template).all()