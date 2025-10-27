from flask import Blueprint, render_template, request, current_app, g, abort
from app.models import Site

sites_bp = Blueprint('sites', __name__, subdomain='<subdomain>')

@sites_bp.route('/')
def site_home(subdomain):
    """Affiche le site publié selon le sous-domaine"""
    site = Site.query.filter_by(subdomain=subdomain, status='published').first()
    
    if not site:
        # Si le site n'existe pas ou n'est pas publié
        abort(404, description=f"Le site avec le sous-domaine '{subdomain}' n'existe pas ou n'est pas publié.")
    
    # Préparer les données pour le template
    site_content = site.get_content()
    site_data = {
        'store_name': site_content.get('store_name', site.name),
        'site_name': site.name,
        'subdomain': site.subdomain,
        'content': site_content,
        'style': site_content.get('style', {}),
        'owner': site.owner,
        'template_id': site.template_id or 1,
        'url': site.get_url(),
        'meta': site_content.get('meta', {})
    }
    
    # Fusionner le contenu pour un accès facile dans les templates
    if isinstance(site_content, dict):
        site_data.update(site_content)
    
    # Déterminer le template à utiliser - priorité au template e-commerce
    template_name = f"sites/template{site.template_id or 1}.html"
    
    # Vérifier si c'est un site e-commerce
    if site_content.get('products') and site_content.get('store_name'):
        template_name = "sites/ecommerce_base.html"
    
    # Rendu du template
    try:
        return render_template(template_name, site_data=site_data, site=site)
    except Exception as e:
        # Fallback si le template n'existe pas
        current_app.logger.warning(f"Template {template_name} non trouvé, utilisation du template par défaut: {e}")
        try:
            # Essayer le template e-commerce de fallback
            return render_template("sites/ecommerce_base.html", site_data=site_data, site=site)
        except:
            # Final fallback
            return render_template("sites/default.html", site_data=site_data, site=site)

@sites_bp.route('/<path:page_path>')
def site_page(subdomain, page_path):
    """Gère les pages supplémentaires du site"""
    site = Site.query.filter_by(subdomain=subdomain, status='published').first()
    
    if not site:
        abort(404)
    
    # Préparer les données
    site_content = site.get_content()
    site_data = {
        'store_name': site_content.get('store_name', site.name),
        'site_name': site.name,
        'subdomain': site.subdomain,
        'content': site_content,
        'style': site_content.get('style', {}),
        'owner': site.owner,
        'template_id': site.template_id or 1,
        'url': site.get_url(),
        'current_page': page_path,
        'meta': site_content.get('meta', {})
    }
    
    # Fusionner le contenu
    if isinstance(site_content, dict):
        site_data.update(site_content)
    
    # Essayer d'abord le template spécifique à la page
    specific_template = f"sites/template{site.template_id or 1}_{page_path}.html"
    generic_template = f"sites/template{site.template_id or 1}_page.html"
    
    try:
        return render_template(specific_template, site_data=site_data, site=site, page_path=page_path)
    except:
        try:
            return render_template(generic_template, site_data=site_data, site=site, page_path=page_path)
        except:
            # Fallback vers le template par défaut
            return render_template("sites/page.html", site_data=site_data, site=site, page_path=page_path)

@sites_bp.route('/preview/<int:site_id>')
def site_preview(site_id):
    """Aperçu du site avant publication (sans sous-domaine)"""
    from flask_login import current_user
    
    site = Site.query.get_or_404(site_id)
    
    # Vérifier les permissions
    if not current_user.is_authenticated or site.user_id != current_user.id:
        abort(403)
    
    # Préparer les données pour la prévisualisation
    site_content = site.get_content()
    site_data = {
        'store_name': site_content.get('store_name', site.name),
        'site_name': site.name,
        'subdomain': site.subdomain,
        'content': site_content,
        'style': site_content.get('style', {}),
        'owner': site.owner,
        'template_id': site.template_id or 1,
        'url': site.get_url(),
        'is_preview': True,
        'meta': site_content.get('meta', {})
    }
    
    # Fusionner le contenu
    if isinstance(site_content, dict):
        site_data.update(site_content)
    
    # Utiliser le template e-commerce si c'est une boutique
    template_name = f"sites/template{site.template_id or 1}.html"
    if site_content.get('products') and site_content.get('store_name'):
        template_name = "sites/ecommerce_base.html"
    
    # Ajouter une bannière de prévisualisation
    try:
        response = render_template(template_name, site_data=site_data, site=site)
        # Injecter une bannière de prévisualisation
        preview_banner = """
        <div style="position: fixed; top: 0; left: 0; right: 0; background: #ffc107; color: #000; text-align: center; padding: 10px; z-index: 9999; font-weight: bold;">
            🔍 APERÇU - Ce site n'est pas encore publié
        </div>
        """
        response = response.replace('<body>', '<body>' + preview_banner)
        return response
    except Exception as e:
        current_app.logger.warning(f"Template de prévisualisation non trouvé: {e}")
        return render_template("sites/default.html", site_data=site_data, site=site)

@sites_bp.route('/product/<int:product_id>')
def product_detail(subdomain, product_id):
    """Page détail d'un produit"""
    site = Site.query.filter_by(subdomain=subdomain, status='published').first()
    
    if not site:
        abort(404)
    
    site_content = site.get_content()
    products = site_content.get('products', [])
    product = next((p for p in products if p.get('id') == product_id), None)
    
    if not product:
        abort(404)
    
    site_data = {
        'store_name': site_content.get('store_name', site.name),
        'site_name': site.name,
        'subdomain': site.subdomain,
        'content': site_content,
        'style': site_content.get('style', {}),
        'owner': site.owner,
        'template_id': site.template_id or 1,
        'url': site.get_url(),
        'current_product': product,
        'meta': site_content.get('meta', {})
    }
    
    if isinstance(site_content, dict):
        site_data.update(site_content)
    
    # Essayer le template de détail produit
    try:
        return render_template("sites/product_detail.html", site_data=site_data, site=site, product=product)
    except:
        # Fallback vers la page générique
        return render_template("sites/ecommerce_base.html", site_data=site_data, site=site)

# Filtres template pour les sites
@sites_bp.app_template_filter('site_asset')
def site_asset_filter(filename):
    """Génère le chemin vers les assets du site"""
    site = getattr(g, 'site', None)
    if site:
        return f"/static/sites/{site.template_id or 1}/{filename}"
    return f"/static/sites/1/{filename}"

@sites_bp.app_template_filter('site_url')
def site_url_filter(path=''):
    """Génère une URL absolue pour le site"""
    site = getattr(g, 'site', None)
    if site:
        base_url = site.get_url()
        return f"{base_url}/{path.lstrip('/')}" if path else base_url
    return path

@sites_bp.app_template_filter('format_price')
def format_price_filter(price):
    """Formate un prix en euros"""
    try:
        return f"{float(price):.2f} €"
    except (ValueError, TypeError):
        return "0.00 €"

# Gestion d'erreur spécifique aux sous-domaines
@sites_bp.errorhandler(404)
def site_not_found(error):
    """Gestion d'erreur 404 pour les sous-domaines"""
    subdomain = getattr(g, 'site_subdomain', None)
    if subdomain:
        return render_template('sites/404.html', subdomain=subdomain), 404
    return error