from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from app import db
from app.models import Site, Template
from app.utils.subdomain_manager import SubdomainManager
import json

builder_bp = Blueprint('builder', __name__)

@builder_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_site():
    if request.method == 'POST':
        site_name = request.form.get('site_name')
        template_id = request.form.get('template_id')
        
        print(f"🔍 DEBUG create_site POST: site_name={site_name}, template_id={template_id}")
        
        # Validation des données
        if not site_name or not template_id:
            flash('Veuillez remplir tous les champs requis.', 'danger')
            return redirect(url_for('builder.create_site'))
        
        # Vérifier que l'utilisateur peut créer un nouveau site
        if not current_user.can_create_site():
            flash('Vous avez atteint la limite de sites autorisés. Veuillez mettre à niveau votre compte.', 'danger')
            return redirect(url_for('builder.create_site'))
        
        # Vérifier que le template existe
        template = Template.query.get(template_id)
        if not template:
            flash('Template sélectionné invalide.', 'danger')
            return redirect(url_for('builder.create_site'))
        
        try:
            # Générer et valider le sous-domaine
            subdomain = SubdomainManager.validate_subdomain_creation(site_name, current_user)
            
            # Créer le site
            site = Site(
                user_id=current_user.id,
                name=site_name,
                subdomain=subdomain,
                template_id=template_id,
                status='draft'
            )
            
            # Ajouter le contenu e-commerce par défaut
            site.add_default_ecommerce_content()
            
            db.session.add(site)
            db.session.commit()
            
            print(f"🔍 DEBUG: Site créé avec ID: {site.id}, sous-domaine: {subdomain}")
            
            flash(f'Site "{site_name}" créé avec succès!', 'success')
            
            # Rediriger vers l'étape 2 (contenu) après création
            return redirect(url_for('builder.step2_content', site_id=site.id))
            
        except ValueError as e:
            flash(f'Erreur lors de la création du site: {str(e)}', 'danger')
            return redirect(url_for('builder.create_site'))
        except Exception as e:
            current_app.logger.error(f"Erreur création site: {str(e)}")
            flash('Une erreur est survenue lors de la création du site.', 'danger')
            return redirect(url_for('builder.create_site'))
    
    # GET request - afficher la page de sélection des templates
    templates = Template.query.filter_by(is_active=True).all()
    print(f"🔍 DEBUG create_site GET: {len(templates)} templates trouvés")
    
    return render_template('builder/step1_template.html', 
                         templates=templates, 
                         step=1,
                         can_create_site=current_user.can_create_site())


@builder_bp.route('/quick-create-ecommerce', methods=['POST'])
@login_required
def quick_create_ecommerce():
    """Créer rapidement une boutique e-commerce avec contenu par défaut et produits d'exemple."""
    # Nom optionnel fourni par le client
    site_name = request.form.get('site_name') or f"Ma boutique {current_user.username}"

    # Vérifier quota
    if not current_user.can_create_site():
        flash('Vous avez atteint la limite de sites autorisés. Veuillez mettre à niveau votre compte.', 'danger')
        return redirect(url_for('dashboard.dashboard'))

    # Choisir un template actif par défaut
    template = Template.query.filter_by(is_active=True).first()
    if not template:
        flash('Aucun template actif disponible pour créer la boutique.', 'danger')
        return redirect(url_for('builder.create_site'))

    try:
        # Générer un sous-domaine disponible
        from app.utils.subdomain_manager import SubdomainManager
        base = SubdomainManager.generate_subdomain(site_name)
        subdomain = SubdomainManager.get_available_subdomain(base)

        # Créer le site
        site = Site(
            user_id=current_user.id,
            name=site_name,
            subdomain=subdomain,
            template_id=template.id,
            status='draft'
        )

        # Contenu e-commerce par défaut
        site.add_default_ecommerce_content()

        # Ajouter quelques produits d'exemple (copie de la logique existante)
        content = site.get_content()
        sample_products = [
            {
                'id': 1,
                'name': 'Produit Premium',
                'price': 49.99,
                'description': 'Un produit de haute qualité avec des fonctionnalités exceptionnelles.',
                'category': 'Premium',
                'in_stock': True,
                'features': ['Haute qualité', 'Garantie 2 ans', 'Support 24/7']
            },
            {
                'id': 2,
                'name': 'Produit Standard',
                'price': 29.99,
                'description': 'Un produit fiable et abordable pour tous les jours.',
                'category': 'Standard',
                'in_stock': True,
                'features': ['Rapport qualité-prix', 'Facile à utiliser', 'Livraison rapide']
            }
        ]

        content.setdefault('products', [])
        existing_ids = [p.get('id', 0) for p in content['products']]
        max_existing_id = max(existing_ids) if existing_ids else 0
        for p in sample_products:
            max_existing_id += 1
            p['id'] = max_existing_id
            content['products'].append(p)

        site.set_content(content)

        db.session.add(site)
        db.session.commit()

        flash(f'Boutique "{site.name}" créée avec succès — vous pouvez la personnaliser maintenant.', 'success')
        return redirect(url_for('builder.step2_content', site_id=site.id))

    except Exception as e:
        current_app.logger.error(f"Erreur quick-create-ecommerce: {e}")
        flash('Erreur lors de la création rapide de la boutique.', 'danger')
        return redirect(url_for('builder.create_site'))

@builder_bp.route('/<int:site_id>/step1')
@login_required
def step1_template(site_id):
    """Étape 1 - Sélection du template (pour modification)"""
    site = Site.query.get_or_404(site_id)
    if site.user_id != current_user.id:
        flash('Accès non autorisé.', 'danger')
        return redirect(url_for('dashboard.dashboard'))
    
    templates = Template.query.filter_by(is_active=True).all()
    return render_template('builder/step1_template.html', 
                         site=site, 
                         templates=templates, 
                         step=1,
                         can_create_site=current_user.can_create_site())

@builder_bp.route('/<int:site_id>/step2')
@login_required
def step2_content(site_id):
    """Étape 2 - Configuration de la boutique e-commerce"""
    site = Site.query.get_or_404(site_id)
    if site.user_id != current_user.id:
        flash('Accès non autorisé.', 'danger')
        return redirect(url_for('dashboard.dashboard'))
    
    # Récupérer le contenu actuel du site
    site_content = site.get_content()
    
    return render_template('builder/step2_content.html', 
                         site=site, 
                         site_content=site_content,
                         step=2)

@builder_bp.route('/<int:site_id>/step3')
@login_required
def step3_style(site_id):
    """Étape 3 - Personnalisation du style"""
    site = Site.query.get_or_404(site_id)
    if site.user_id != current_user.id:
        flash('Accès non autorisé.', 'danger')
        return redirect(url_for('dashboard.dashboard'))
    
    # Récupérer le style actuel
    site_content = site.get_content()
    site_style = site_content.get('style', {})
    
    return render_template('builder/step3_style.html', 
                         site=site, 
                         site_style=site_style,
                         step=3)

@builder_bp.route('/<int:site_id>/step4')
@login_required
def step4_publish(site_id):
    """Étape 4 - Publication de la boutique"""
    site = Site.query.get_or_404(site_id)
    if site.user_id != current_user.id:
        flash('Accès non autorisé.', 'danger')
        return redirect(url_for('dashboard.dashboard'))
    
    # Vérifier que la boutique e-commerce est prête
    is_ready = site.is_ecommerce_ready()
    validation_errors = []
    
    if not is_ready:
        content = site.get_content()
        
        # Détails des erreurs de validation
        if not content.get('store_name'):
            validation_errors.append("Nom de la boutique manquant")
        if not content.get('hero_title'):
            validation_errors.append("Titre principal manquant")
        if not content.get('hero_subtitle'):
            validation_errors.append("Sous-titre manquant")
        if not content.get('contact_email'):
            validation_errors.append("Email de contact manquant")
        
        products = content.get('products', [])
        if len(products) == 0:
            validation_errors.append("Aucun produit ajouté")
        else:
            for i, product in enumerate(products):
                if not product.get('name'):
                    validation_errors.append(f"Produit {i+1}: nom manquant")
                if not product.get('price'):
                    validation_errors.append(f"Produit {i+1}: prix manquant")
                if not product.get('description'):
                    validation_errors.append(f"Produit {i+1}: description manquante")
    
    return render_template('builder/step4_publish.html', 
                         site=site, 
                         is_ready=is_ready,
                         validation_errors=validation_errors,
                         step=4)

@builder_bp.route('/<int:site_id>/update-template', methods=['POST'])
@login_required
def update_template(site_id):
    """Mettre à jour le template du site"""
    site = Site.query.get_or_404(site_id)
    if site.user_id != current_user.id:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    template_id = request.json.get('template_id')
    
    # Vérifier que le template existe
    template = Template.query.get(template_id)
    if not template:
        return jsonify({'success': False, 'error': 'Template invalide'}), 400
    
    # Mettre à jour le template
    site.template_id = template_id
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Template mis à jour avec succès'})

@builder_bp.route('/<int:site_id>/save-content', methods=['POST'])
@login_required
def save_content(site_id):
    """Sauvegarder le contenu de la boutique e-commerce"""
    site = Site.query.get_or_404(site_id)
    if site.user_id != current_user.id:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    try:
        content_data = request.json
        
        # Validation basique du contenu
        if not isinstance(content_data, dict):
            return jsonify({'success': False, 'error': 'Format de contenu invalide'}), 400
        
        # Validation des champs requis pour l'e-commerce
        required_fields = ['store_name', 'hero_title', 'hero_subtitle', 'contact_email']
        missing_fields = [field for field in required_fields if not content_data.get(field)]
        
        if missing_fields:
            return jsonify({
                'success': False, 
                'error': f'Champs requis manquants: {", ".join(missing_fields)}'
            }), 400
        
        # Validation des produits
        products = content_data.get('products', [])
        if len(products) == 0:
            return jsonify({
                'success': False, 
                'error': 'Au moins un produit est requis pour une boutique e-commerce'
            }), 400
        
        for i, product in enumerate(products):
            if not product.get('name') or not product.get('price') or not product.get('description'):
                return jsonify({
                    'success': False, 
                    'error': f'Produit {i+1}: nom, prix et description sont requis'
                }), 400
            
            # Valider le prix
            try:
                price = float(product.get('price', 0))
                if price <= 0:
                    return jsonify({
                        'success': False, 
                        'error': f'Produit {i+1}: le prix doit être supérieur à 0'
                    }), 400
            except (ValueError, TypeError):
                return jsonify({
                    'success': False, 
                    'error': f'Produit {i+1}: prix invalide'
                }), 400
        
        # Sauvegarder le contenu
        site.set_content(content_data)
        site.date_updated = db.func.now()
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': 'Contenu de la boutique sauvegardé avec succès',
            'is_ecommerce_ready': site.is_ecommerce_ready()
        })
        
    except Exception as e:
        current_app.logger.error(f"Erreur sauvegarde contenu: {str(e)}")
        return jsonify({'success': False, 'error': 'Erreur lors de la sauvegarde'}), 500

@builder_bp.route('/<int:site_id>/save-style', methods=['POST'])
@login_required
def save_style(site_id):
    """Sauvegarder le style de la boutique"""
    site = Site.query.get_or_404(site_id)
    if site.user_id != current_user.id:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    try:
        style_data = request.json
        
        # Récupérer le contenu actuel
        current_content = site.get_content()
        
        # Mettre à jour seulement la partie style
        current_content['style'] = style_data
        
        # Sauvegarder
        site.set_content(current_content)
        site.date_updated = db.func.now()
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Style sauvegardé avec succès'})
        
    except Exception as e:
        current_app.logger.error(f"Erreur sauvegarde style: {str(e)}")
        return jsonify({'success': False, 'error': 'Erreur lors de la sauvegarde du style'}), 500

@builder_bp.route('/<int:site_id>/publish', methods=['POST'])
@login_required
def publish_site(site_id):
    """Publier la boutique e-commerce"""
    site = Site.query.get_or_404(site_id)
    if site.user_id != current_user.id:
        flash('Accès non autorisé.', 'danger')
        return redirect(url_for('dashboard.dashboard'))
    
    try:
        # Vérifier que la boutique e-commerce est prête
        if not site.is_ecommerce_ready():
            content = site.get_content()
            error_messages = []
            
            if not content.get('store_name'):
                error_messages.append("Le nom de la boutique est requis")
            if not content.get('hero_title'):
                error_messages.append("Le titre principal est requis")
            if not content.get('hero_subtitle'):
                error_messages.append("Le sous-titre est requis")
            if not content.get('contact_email'):
                error_messages.append("L'email de contact est requis")
            
            products = content.get('products', [])
            if len(products) == 0:
                error_messages.append("Au moins un produit est requis")
            else:
                for i, product in enumerate(products):
                    if not product.get('name'):
                        error_messages.append(f"Produit {i+1}: le nom est requis")
                    if not product.get('price'):
                        error_messages.append(f"Produit {i+1}: le prix est requis")
                    if not product.get('description'):
                        error_messages.append(f"Produit {i+1}: la description est requise")
            
            flash_message = "Veuillez compléter les informations de votre boutique avant de publier:<br>" + "<br>".join([f"• {msg}" for msg in error_messages])
            flash(flash_message, 'warning')
            return redirect(url_for('builder.step2_content', site_id=site_id))
        
        # Publier le site
        site.publish()
        
        # Générer l'URL complète
        site_url = site.get_url()
        
        flash(f'✅ Votre boutique en ligne a été publiée avec succès! Accédez-y à: <a href="{site_url}" target="_blank">{site_url}</a>', 'success')
        return redirect(url_for('dashboard.dashboard'))
        
    except Exception as e:
        current_app.logger.error(f"Erreur publication site: {str(e)}")
        flash('Une erreur est survenue lors de la publication de votre boutique.', 'danger')
        return redirect(url_for('builder.step4_publish', site_id=site_id))

@builder_bp.route('/<int:site_id>/unpublish', methods=['POST'])
@login_required
def unpublish_site(site_id):
    """Dépublier la boutique"""
    site = Site.query.get_or_404(site_id)
    if site.user_id != current_user.id:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    try:
        site.unpublish()
        return jsonify({'success': True, 'message': 'Boutique dépubliée avec succès'})
        
    except Exception as e:
        current_app.logger.error(f"Erreur dépublication site: {str(e)}")
        return jsonify({'success': False, 'error': 'Erreur lors de la dépublication'}), 500

@builder_bp.route('/<int:site_id>/duplicate', methods=['POST'])
@login_required
def duplicate_site(site_id):
    """Dupliquer une boutique existante"""
    original_site = Site.query.get_or_404(site_id)
    if original_site.user_id != current_user.id:
        flash('Accès non autorisé.', 'danger')
        return redirect(url_for('dashboard.dashboard'))
    
    # Vérifier que l'utilisateur peut créer un nouveau site
    if not current_user.can_create_site():
        flash('Vous avez atteint la limite de sites autorisés. Veuillez mettre à niveau votre compte.', 'danger')
        return redirect(url_for('dashboard.dashboard'))
    
    try:
        # Générer un nouveau sous-domaine
        new_subdomain = SubdomainManager.get_available_subdomain(
            f"{original_site.subdomain}-copy"
        )
        
        # Créer le nouveau site
        new_site = Site(
            user_id=current_user.id,
            name=f"{original_site.name} (Copie)",
            subdomain=new_subdomain,
            template_id=original_site.template_id,
            status='draft'
        )
        
        # Copier le contenu
        new_site.set_content(original_site.get_content())
        
        db.session.add(new_site)
        db.session.commit()
        
        flash(f'Boutique dupliquée avec succès! Nouvelle boutique: {new_site.name}', 'success')
        return redirect(url_for('builder.step2_content', site_id=new_site.id))
        
    except Exception as e:
        current_app.logger.error(f"Erreur duplication site: {str(e)}")
        flash('Une erreur est survenue lors de la duplication de la boutique.', 'danger')
        return redirect(url_for('dashboard.dashboard'))

@builder_bp.route('/<int:site_id>/delete', methods=['POST'])
@login_required
def delete_site(site_id):
    """Supprimer une boutique"""
    site = Site.query.get_or_404(site_id)
    if site.user_id != current_user.id:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    try:
        site_name = site.name
        db.session.delete(site)
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': f'Boutique "{site_name}" supprimée avec succès'
        })
        
    except Exception as e:
        current_app.logger.error(f"Erreur suppression site: {str(e)}")
        return jsonify({'success': False, 'error': 'Erreur lors de la suppression'}), 500

@builder_bp.route('/preview/<int:site_id>')
@login_required
def site_preview(site_id):
    """Aperçu de la boutique avant publication"""
    site = Site.query.get_or_404(site_id)
    if site.user_id != current_user.id:
        flash('Accès non autorisé.', 'danger')
        return redirect(url_for('dashboard.dashboard'))
    
    # Préparer les données pour l'aperçu
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
        'is_preview': True
    }
    
    # Fusionner le contenu pour un accès facile dans les templates
    if isinstance(site_content, dict):
        site_data.update(site_content)
    
    # Utiliser le template e-commerce
    template_name = "sites/ecommerce_base.html"
    
    try:
        response = render_template(template_name, site_data=site_data, site=site)
        # Injecter une bannière de prévisualisation
        preview_banner = """
        <div style="position: fixed; top: 0; left: 0; right: 0; background: #ffc107; color: #000; text-align: center; padding: 10px; z-index: 9999; font-weight: bold; border-bottom: 2px solid #ffab00;">
            <i class="bi bi-eye-fill me-2"></i>APERÇU - Cette boutique n'est pas encore publiée
            <button onclick="this.parentElement.remove()" style="background: none; border: none; margin-left: 10px; cursor: pointer;">×</button>
        </div>
        """
        response = response.replace('<body>', '<body>' + preview_banner)
        return response
    except Exception as e:
        current_app.logger.warning(f"Template de prévisualisation non trouvé: {e}")
        return render_template("sites/default.html", site_data=site_data, site=site)

@builder_bp.route('/check-subdomain')
@login_required
def check_subdomain():
    """Vérifier la disponibilité d'un sous-domaine"""
    subdomain = request.args.get('subdomain', '').lower().strip()
    
    if not subdomain:
        return jsonify({'available': False, 'message': 'Sous-domaine vide'})
    
    # Valider le format
    if not SubdomainManager.is_valid_subdomain(subdomain):
        return jsonify({'available': False, 'message': 'Sous-domaine invalide'})
    
    # Vérifier la disponibilité
    is_available = SubdomainManager.is_subdomain_available(subdomain)
    
    return jsonify({
        'available': is_available,
        'message': 'Sous-domaine disponible' if is_available else 'Sous-domaine déjà pris'
    })

@builder_bp.route('/<int:site_id>/validate-ecommerce')
@login_required
def validate_ecommerce(site_id):
    """Valider si la boutique e-commerce est prête pour la publication"""
    site = Site.query.get_or_404(site_id)
    if site.user_id != current_user.id:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    is_ready = site.is_ecommerce_ready()
    validation_details = {
        'is_ready': is_ready,
        'missing_fields': [],
        'product_errors': []
    }
    
    if not is_ready:
        content = site.get_content()
        
        # Vérifier les champs requis
        required_fields = [
            ('store_name', 'Nom de la boutique'),
            ('hero_title', 'Titre principal'),
            ('hero_subtitle', 'Sous-titre'),
            ('contact_email', 'Email de contact')
        ]
        
        for field, label in required_fields:
            if not content.get(field):
                validation_details['missing_fields'].append(label)
        
        # Vérifier les produits
        products = content.get('products', [])
        if len(products) == 0:
            validation_details['product_errors'].append('Aucun produit ajouté')
        else:
            for i, product in enumerate(products):
                product_errors = []
                if not product.get('name'):
                    product_errors.append('nom manquant')
                if not product.get('price'):
                    product_errors.append('prix manquant')
                if not product.get('description'):
                    product_errors.append('description manquante')
                
                if product_errors:
                    validation_details['product_errors'].append(f"Produit {i+1}: {', '.join(product_errors)}")
    
    return jsonify({
        'success': True,
        'validation': validation_details
    })

@builder_bp.route('/<int:site_id>/add-sample-products', methods=['POST'])
@login_required
def add_sample_products(site_id):
    """Ajouter des produits d'exemple à la boutique"""
    site = Site.query.get_or_404(site_id)
    if site.user_id != current_user.id:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    try:
        content = site.get_content()
        
        # Produits d'exemple
        sample_products = [
            {
                'id': 1,
                'name': 'Produit Premium',
                'price': 49.99,
                'description': 'Un produit de haute qualité avec des fonctionnalités exceptionnelles.',
                'category': 'Premium',
                'in_stock': True,
                'features': ['Haute qualité', 'Garantie 2 ans', 'Support 24/7']
            },
            {
                'id': 2,
                'name': 'Produit Standard',
                'price': 29.99,
                'description': 'Un produit fiable et abordable pour tous les jours.',
                'category': 'Standard',
                'in_stock': True,
                'features': ['Rapport qualité-prix', 'Facile à utiliser', 'Livraison rapide']
            },
            {
                'id': 3,
                'name': 'Produit Économique',
                'price': 14.99,
                'description': 'La solution parfaite pour les petits budgets.',
                'category': 'Économique',
                'in_stock': True,
                'features': ['Abordable', 'Essentiel', 'Satisfaction garantie']
            }
        ]
        
        # Ajouter les produits d'exemple
        if 'products' not in content:
            content['products'] = []
        
        # S'assurer que les IDs sont uniques
        existing_ids = [p.get('id', 0) for p in content['products']]
        max_existing_id = max(existing_ids) if existing_ids else 0
        
        for product in sample_products:
            product['id'] = max_existing_id + product['id']
            content['products'].append(product)
        
        site.set_content(content)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Produits d\'exemple ajoutés avec succès',
            'products_count': len(content['products'])
        })
        
    except Exception as e:
        current_app.logger.error(f"Erreur ajout produits exemple: {str(e)}")
        return jsonify({'success': False, 'error': 'Erreur lors de l\'ajout des produits'}), 500


@builder_bp.route('/<int:site_id>/fill-defaults', methods=['POST'])
@login_required
def fill_defaults(site_id):
    """Remplir le site avec le contenu e-commerce par défaut (store info + products)."""
    site = Site.query.get_or_404(site_id)
    if site.user_id != current_user.id:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403

    try:
        # Ajouter le contenu par défaut
        site.add_default_ecommerce_content()

        # S'assurer d'au moins quelques produits d'exemple
        content = site.get_content()
        if not content.get('products'):
            content['products'] = []
        if len(content['products']) == 0:
            sample_products = [
                {'id': 1, 'name': 'Produit Premium', 'price': 49.99, 'description': 'Produit premium', 'category': 'Premium', 'in_stock': True},
                {'id': 2, 'name': 'Produit Standard', 'price': 29.99, 'description': 'Produit standard', 'category': 'Standard', 'in_stock': True}
            ]
            content['products'].extend(sample_products)

        site.set_content(content)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Contenu par défaut appliqué'})

    except Exception as e:
        current_app.logger.error(f"Erreur fill-defaults: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Erreur lors de l\'application des valeurs par défaut'}), 500