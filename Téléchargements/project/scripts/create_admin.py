#!/usr/bin/env python3
"""
Script de création d'un utilisateur administrateur
"""
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import User

def create_admin_user():
    """Create an admin user"""
    app = create_app()
    
    with app.app_context():
        username = input("Nom d'utilisateur admin: ")
        email = input("Email admin: ")
        password = input("Mot de passe admin: ")
        
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            print("❌ Un utilisateur avec cet email existe déjà")
            return
        
        # Create admin user
        admin = User(
            username=username,
            email=email,
            role='admin'
        )
        admin.set_password(password)
        
        db.session.add(admin)
        db.session.commit()
        
        print(f"✅ Utilisateur admin '{username}' créé avec succès!")

if __name__ == '__main__':
    create_admin_user()