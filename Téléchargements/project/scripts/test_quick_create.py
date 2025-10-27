import os
from app import create_app, db
from app.models import User, Site
from flask_login import login_user

# Ensure PYTHONPATH root if needed (but running from project root should work)
app = create_app()

with app.app_context():
    # Create or get a test user
    user = User.query.filter_by(username='test_quick').first()
    if not user:
        user = User(username='test_quick', email='test_quick@example.com')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()
        print('Created test user', user.id)
    else:
        print('Using existing test user', user.id)

    # Use test request context to simulate a logged-in POST
    from flask import url_for
    from app.routes.site_builder import quick_create_ecommerce
    from flask import request
    
    with app.test_request_context('/builder/quick-create-ecommerce', method='POST', data={'site_name': 'Boutique Test'}):
        # log in user
        login_user(user)
        # Call the view function directly
        response = quick_create_ecommerce()
        print('quick_create_ecommerce response type:', type(response))
        try:
            # If redirect, try to get location
            loc = response.location if hasattr(response, 'location') else None
            print('Redirect location:', loc)
        except Exception:
            pass

    # List sites for the user
    sites = Site.query.filter_by(user_id=user.id).all()
    print('User has', len(sites), 'sites')
    for s in sites:
        print('-', s.id, s.name, s.subdomain, s.status)
