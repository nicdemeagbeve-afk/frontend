from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Site

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def dashboard():
    sites = Site.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard/dashboard.html', sites=sites)

@dashboard_bp.route('/sites')
@login_required
def site_list():
    sites = Site.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard/site_list.html', sites=sites)

@dashboard_bp.route('/site/delete/<int:site_id>', methods=['POST'])
@login_required
def delete_site(site_id):
    site = Site.query.get_or_404(site_id)
    
    if site.user_id != current_user.id:
        flash('Accès non autorisé.', 'danger')
        return redirect(url_for('dashboard.site_list'))
    
    db.session.delete(site)
    db.session.commit()
    
    flash('Site supprimé avec succès.', 'success')
    return redirect(url_for('dashboard.site_list'))