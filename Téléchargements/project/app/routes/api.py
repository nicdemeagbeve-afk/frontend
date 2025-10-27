from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db, limiter
from app.models import Site

api_bp = Blueprint('api', __name__)

@api_bp.route('/sites/<int:site_id>/content', methods=['GET', 'POST'])
@login_required
@limiter.limit("10 per minute")
def site_content(site_id):
    site = Site.query.get_or_404(site_id)
    
    if site.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if request.method == 'GET':
        return jsonify(site.get_content())
    
    elif request.method == 'POST':
        content_data = request.json
        site.set_content(content_data)
        site.date_updated = db.func.now()
        db.session.commit()
        
        return jsonify({'success': True})

@api_bp.route('/templates')
def get_templates():
    templates = Template.query.filter_by(is_active=True).all()
    templates_data = [
        {
            'id': t.id,
            'name': t.name,
            'description': t.description,
            'category': t.category,
            'preview_url': t.preview_url
        }
        for t in templates
    ]
    
    return jsonify(templates_data)