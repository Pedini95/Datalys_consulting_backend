from flask import Blueprint, request, jsonify
from models.partner import Partner
from services.partner_service import PartnerService
from utils.phone_validator import PhoneValidator, validate_phone_number
from routes.auth import require_auth
import logging

bp = Blueprint('partners', __name__)
partner_service = PartnerService()

@bp.route('/partners/getByCriteria', methods=['POST'])
@require_auth
def get_partners():
    """Récupérer les partenaires selon des critères"""
    from flask import g
    try:
        data = request.get_json()
        index = data.get('index', 0)
        size = data.get('size', 10)
        criteria = data.get('data', {})
        
        partners, total = Partner.get_by_criteria(criteria, index, size)
        
        items = []
        for partner in partners:
            partner_dict = partner.as_dict()
            items.append(partner_dict)
        
        return jsonify({
            'items': items,
            'count': total,
            'message': {'message': 'OPERATION SUCCESSFULLY', 'code': 200},
            'code': 200
        })
    except Exception as e:
        logging.error(f"Erreur lors de la récupération des partenaires: {str(e)}")
        return jsonify({
            'message': {'message': 'Erreur lors de la récupération des partenaires', 'code': 500},
            'code': 500
        }), 500

@bp.route('/partners/create', methods=['POST'])
@require_auth
def create_partner():
    """Créer un nouveau partenaire"""
    from flask import g
    current_user = g.current_user
    try:
        data = request.get_json()

        # Validation du numéro de téléphone
        phone = data.get('phone')
        country_code = data.get('country_code', '+237')

        if phone:
            is_valid, error_message = validate_phone_number(phone, country_code)
            if not is_valid:
                return jsonify({
                    'message': {'message': f'Numéro de téléphone invalide: {error_message}', 'code': 400},
                    'code': 400
                }), 400

        # Normaliser le numéro de téléphone
        if phone:
            from utils.phone_validator import PhoneValidator
            normalized_phone, detected_country = PhoneValidator.normalize_phone(phone, country_code)
            data['phone'] = normalized_phone
            data['country_code'] = detected_country

        # Vérifier si un email est fourni pour créer un utilisateur
        if data.get('email'):
            # Créer le partenaire avec un compte utilisateur
            partner, username, temp_password, success, message = partner_service.create_with_user(data, current_user.id)
            
            if not success:
                return jsonify({
                    'message': {'message': message, 'code': 400},
                    'code': 400
                }), 400
            
            # Récupérer le client_code de l'utilisateur créé
            from models import User
            user = User.query.filter_by(email=data.get('email')).first()
            client_code = user.client_code if user and user.client_code else username
            
            # Envoyer l'email avec les credentials
            email_sent = False
            try:
                from utils.notification import EmailService
                import os
                
                email_service = EmailService()
                app_url = os.getenv('APP_URL', 'http://localhost:3000')
                
                # Vérifier que client_code et temp_password ne sont pas None
                if client_code and temp_password:
                    email_sent = email_service.send_partner_credentials_email(
                        partner_email=data.get('email', ''),
                        partner_name=data.get('name', 'Partenaire'),
                        email=data.get('email', ''),  # Email réel du partenaire
                        password=temp_password,
                        app_url=app_url,
                        client_code=client_code  # Code client pour se connecter
                    )
                    
                    if email_sent:
                        logging.info(f"Email avec credentials envoyé à {data.get('email')} - Code client: {client_code}")
                    else:
                        logging.warning(f"Échec de l'envoi de l'email à {data.get('email')}")
            except Exception as email_error:
                logging.error(f"Erreur lors de l'envoi de l'email: {str(email_error)}")
                # Ne pas échouer la création si l'email échoue
            
            return jsonify({
                'data': partner.as_dict(),
                'credentials': {
                    'client_code': client_code,  # Retourner le client_code au lieu de username
                    'email': username,  # Garder l'email pour référence
                    'temp_password': temp_password,
                    'email_sent': email_sent
                },
                'message': {'message': 'Partenaire et compte utilisateur créés avec succès', 'code': 201},
                'code': 201
            }), 201
        else:
            # Créer le partenaire sans compte utilisateur
            partner, success, message = partner_service.create(data, current_user.id)
            if not success:
                return jsonify({
                    'message': {'message': message, 'code': 400},
                    'code': 400
                }), 400
            
            return jsonify({
                'data': partner.as_dict(),
                'message': {'message': 'Partenaire créé avec succès', 'code': 201},
                'code': 201
            }), 201
    except Exception as e:
        logging.error(f"Erreur lors de la création du partenaire: {str(e)}")
        return jsonify({
            'message': {'message': 'Erreur lors de la création du partenaire', 'code': 500},
            'code': 500
        }), 500

@bp.route('/partners/update', methods=['POST'])
@require_auth
def update_partner():
    """Mettre à jour un partenaire"""
    from flask import g
    current_user = g.current_user
    try:
        data = request.get_json()
        partner_id = data.get('id')

        if not partner_id:
            return jsonify({
                'message': {'message': 'ID du partenaire requis', 'code': 400},
                'code': 400
            }), 400

        # Validation du numéro de téléphone
        phone = data.get('phone')
        country_code = data.get('country_code', '+237')

        if phone:
            is_valid, error_message = validate_phone_number(phone, country_code)
            if not is_valid:
                return jsonify({
                    'message': {'message': f'Numéro de téléphone invalide: {error_message}', 'code': 400},
                    'code': 400
                }), 400

        # Normaliser le numéro de téléphone
        if phone:
            from utils.phone_validator import PhoneValidator
            normalized_phone, detected_country = PhoneValidator.normalize_phone(phone, country_code)
            data['phone'] = normalized_phone
            data['country_code'] = detected_country

        partner, success, message = partner_service.update(partner_id, data, current_user.id)
        if not success:
            return jsonify({
                'message': {'message': message, 'code': 400},
                'code': 400
            }), 400
        
        return jsonify({
            'data': partner.as_dict(),
            'message': {'message': 'Partenaire mis à jour avec succès', 'code': 200},
            'code': 200
        })
    except Exception as e:
        logging.error(f"Erreur lors de la mise à jour du partenaire: {str(e)}")
        return jsonify({
            'message': {'message': 'Erreur lors de la mise à jour du partenaire', 'code': 500},
            'code': 500
        }), 500

@bp.route('/partners/delete', methods=['POST'])
@require_auth
def delete_partner():
    """Supprimer un partenaire"""
    from flask import g
    current_user = g.current_user
    try:
        data = request.get_json()
        partner_id = data.get('id')

        if not partner_id:
            return jsonify({
                'message': {'message': 'ID du partenaire requis', 'code': 400},
                'code': 400
            }), 400

        success, message = partner_service.delete(partner_id, current_user.id)
        if not success:
            return jsonify({
                'message': {'message': message, 'code': 400},
                'code': 400
            }), 400
        
        return jsonify({
            'message': {'message': 'Partenaire supprimé avec succès', 'code': 200},
            'code': 200
        })
    except Exception as e:
        logging.error(f"Erreur lors de la suppression du partenaire: {str(e)}")
        return jsonify({
            'message': {'message': 'Erreur lors de la suppression du partenaire', 'code': 500},
            'code': 500
        }), 500

@bp.route('/partners/countries', methods=['GET'])
@require_auth
def get_supported_countries():
    """Obtenir la liste des pays supportés pour les numéros de téléphone"""
    try:
        countries = PhoneValidator.get_supported_countries()
        
        # Formater la réponse
        countries_list = []
        for code, info in countries.items():
            countries_list.append({
                'code': code,
                'name': info['name'],
                'description': info['description'],
                'example': info['example']
            })
        
        return jsonify({
            'data': countries_list,
            'message': {'message': 'Pays supportés récupérés avec succès', 'code': 200},
            'code': 200
        })
    except Exception as e:
        logging.error(f"Erreur lors de la récupération des pays supportés: {str(e)}")
        return jsonify({
            'message': {'message': 'Erreur lors de la récupération des pays supportés', 'code': 500},
            'code': 500
        }), 500

@bp.route('/partners/upload-logo', methods=['POST'])
@require_auth
def upload_partner_logo():
    """
    Uploader un logo pour un partenaire

    Form data:
    - partner_id: ID du partenaire
    - logo: fichier image (PNG, JPG, JPEG, GIF)
    """
    from flask import g
    from werkzeug.utils import secure_filename
    import os
    import uuid
    from datetime import datetime
    from extensions import db

    current_user = g.current_user

    try:
        partner_id = request.form.get('partner_id')

        if not partner_id:
            return jsonify({
                'message': {'message': 'ID du partenaire requis', 'code': 400},
                'code': 400
            }), 400

        if 'logo' not in request.files:
            return jsonify({
                'message': {'message': 'Aucun fichier logo fourni', 'code': 400},
                'code': 400
            }), 400

        file = request.files['logo']

        if file.filename == '':
            return jsonify({
                'message': {'message': 'Aucun fichier sélectionné', 'code': 400},
                'code': 400
            }), 400

        # Vérifier le type de fichier
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
        file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''

        if file_ext not in allowed_extensions:
            return jsonify({
                'message': {'message': f'Type de fichier non autorisé. Types acceptés: {", ".join(allowed_extensions)}', 'code': 400},
                'code': 400
            }), 400

        # Récupérer le partenaire
        partner = Partner.query.filter_by(id=partner_id, is_deleted=False).first()

        if not partner:
            return jsonify({
                'message': {'message': 'Partenaire non trouvé', 'code': 404},
                'code': 404
            }), 404

        # Supprimer l'ancien logo si existant
        if partner.logo_url:
            old_logo_path = os.path.join('/app/src/static/files/logos', os.path.basename(partner.logo_url))
            if os.path.exists(old_logo_path):
                try:
                    os.remove(old_logo_path)
                    logging.info(f"Ancien logo supprimé: {old_logo_path}")
                except Exception as e:
                    logging.warning(f"Impossible de supprimer l'ancien logo: {e}")

        # Générer un nom unique pour le fichier
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        filename = f"{timestamp}_{unique_id}.{file_ext}"

        # Créer le dossier si nécessaire
        upload_folder = '/app/src/static/files/logos'
        os.makedirs(upload_folder, exist_ok=True)

        # Sauvegarder le fichier
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)

        # Mettre à jour le partenaire avec l'URL du logo
        logo_url = f"/static/files/logos/{filename}"
        partner.logo_url = logo_url
        partner.updated_by = current_user.id
        partner.updated_at = datetime.utcnow()

        db.session.commit()

        logging.info(f"Logo uploadé pour partenaire {partner_id}: {logo_url}")

        return jsonify({
            'data': {
                'logo_url': logo_url,
                'partner_id': partner_id
            },
            'message': {'message': 'Logo uploadé avec succès', 'code': 200},
            'code': 200
        })

    except Exception as e:
        logging.error(f"Erreur lors de l'upload du logo: {str(e)}")
        return jsonify({
            'message': {'message': f'Erreur lors de la sauvegarde: {str(e)}', 'code': 500},
            'code': 500
        }), 500


@bp.route('/partners/delete-logo', methods=['POST'])
@require_auth
def delete_partner_logo():
    """
    Supprimer le logo d'un partenaire

    Body:
    {
        "partner_id": 123
    }
    """
    from flask import g
    import os
    from datetime import datetime
    from extensions import db

    current_user = g.current_user

    try:
        data = request.get_json()
        partner_id = data.get('partner_id') or data.get('id')

        if not partner_id:
            return jsonify({
                'message': {'message': 'ID du partenaire requis', 'code': 400},
                'code': 400
            }), 400

        # Récupérer le partenaire
        partner = Partner.query.filter_by(id=partner_id, is_deleted=False).first()

        if not partner:
            return jsonify({
                'message': {'message': 'Partenaire non trouvé', 'code': 404},
                'code': 404
            }), 404

        if not partner.logo_url:
            return jsonify({
                'message': {'message': 'Ce partenaire n\'a pas de logo', 'code': 400},
                'code': 400
            }), 400

        # Supprimer le fichier physique
        logo_filename = os.path.basename(partner.logo_url)
        logo_path = os.path.join('/app/src/static/files/logos', logo_filename)

        if os.path.exists(logo_path):
            try:
                os.remove(logo_path)
                logging.info(f"Fichier logo supprimé: {logo_path}")
            except Exception as e:
                logging.warning(f"Impossible de supprimer le fichier logo: {e}")

        # Mettre à jour le partenaire
        old_logo_url = partner.logo_url
        partner.logo_url = None
        partner.updated_by = current_user.id
        partner.updated_at = datetime.utcnow()

        db.session.commit()

        logging.info(f"Logo supprimé pour partenaire {partner_id}: {old_logo_url}")

        return jsonify({
            'data': {
                'partner_id': partner_id,
                'deleted_logo': old_logo_url
            },
            'message': {'message': 'Logo supprimé avec succès', 'code': 200},
            'code': 200
        })

    except Exception as e:
        logging.error(f"Erreur lors de la suppression du logo: {str(e)}")
        return jsonify({
            'message': {'message': f'Erreur lors de la suppression: {str(e)}', 'code': 500},
            'code': 500
        }), 500


@bp.route('/partners/validate-phone', methods=['POST'])
@require_auth
def validate_phone_number_route():
    """Valider un numéro de téléphone"""
    try:
        data = request.get_json()
        phone = data.get('phone')
        country_code = data.get('country_code', '+237')
        
        if not phone:
            return jsonify({
                'message': {'message': 'Numéro de téléphone requis', 'code': 400},
                'code': 400
            }), 400
        
        is_valid, message = validate_phone_number(phone, country_code)
        
        return jsonify({
            'data': {
                'is_valid': is_valid,
                'message': message,
                'formatted_phone': PhoneValidator.format_phone(phone, country_code) if is_valid else None
            },
            'message': {'message': 'Validation terminée', 'code': 200},
            'code': 200
        })
    except Exception as e:
        logging.error(f"Erreur lors de la validation du numéro: {str(e)}")
        return jsonify({
            'message': {'message': 'Erreur lors de la validation du numéro', 'code': 500},
            'code': 500
        }), 500 

 