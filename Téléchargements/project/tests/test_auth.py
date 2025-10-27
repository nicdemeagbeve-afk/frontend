import pytest
from app import create_app, db
from app.models import User

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client

def test_register(client):
    """Test user registration"""
    response = client.post('/register', data={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'testpassword',
        'confirm_password': 'testpassword'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Compte cr&#233;&#233; avec succ&#232;s' in response.data

def test_login(client):
    """Test user login"""
    # First create a user
    user = User(username='testuser', email='test@example.com')
    user.set_password('testpassword')
    db.session.add(user)
    db.session.commit()
    
    # Then test login
    response = client.post('/login', data={
        'email': 'test@example.com',
        'password': 'testpassword'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Tableau de bord' in response.data

def test_invalid_login(client):
    """Test login with invalid credentials"""
    response = client.post('/login', data={
        'email': 'wrong@example.com',
        'password': 'wrongpassword'
    }, follow_redirects=True)
    
    assert b'Email ou mot de passe incorrect' in response.data