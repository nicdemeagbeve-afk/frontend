import pytest
import json
from app import create_app, db
from app.models import User, Site

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            
            # Create test user
            user = User(username='testuser', email='test@example.com')
            user.set_password('testpassword')
            db.session.add(user)
            db.session.commit()
            
        yield client

def test_create_site(client):
    """Test site creation"""
    # Login first
    client.post('/login', data={
        'email': 'test@example.com',
        'password': 'testpassword'
    })
    
    response = client.post('/builder/create', data={
        'site_name': 'Mon Site Test',
        'template_id': 1
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'&#201;ditez votre contenu' in response.data

def test_save_content(client):
    """Test content saving"""
    # Login and create site
    client.post('/login', data={
        'email': 'test@example.com',
        'password': 'testpassword'
    })
    
    site = Site(
        user_id=1,
        name='Test Site',
        subdomain='test-site',
        template_id=1
    )
    db.session.add(site)
    db.session.commit()
    
    content_data = {
        'hero_title': 'Titre de test',
        'hero_subtitle': 'Sous-titre de test'
    }
    
    response = client.post(f'/api/sites/{site.id}/content', 
                         json=content_data,
                         content_type='application/json')
    
    assert response.status_code == 200
    assert response.json['success'] == True