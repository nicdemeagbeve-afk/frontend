#!/usr/bin/env python3
"""
Script d'initialisation de la base de données
"""
import os
import sys

# Add the app directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.utils.database import init_sample_data

def init_database():
    """Initialize the database with sample data"""
    app = create_app()
    
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Initialize sample data
        init_sample_data()
        
        print("✅ Base de données initialisée avec succès!")
        print("📊 Tables créées: users, sites, templates, logs")
        print("🎨 Templates d'exemple ajoutés")

if __name__ == '__main__':
    init_database()