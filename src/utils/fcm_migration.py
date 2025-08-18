"""
Utilitaire de migration pour ajouter le champ FCM token à la table users
Ce script peut être exécuté pour mettre à jour une base de données existante.
"""

import logging
from sqlalchemy import text
from extensions import db

logger = logging.getLogger(__name__)

def migrate_add_fcm_token():
    """
    Ajouter le champ fcm_token à la table users si il n'existe pas déjà
    
    Returns:
        bool: True si la migration a réussi
    """
    try:
        # Vérifier si la colonne existe déjà
        result = db.session.execute(text("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'users' 
            AND COLUMN_NAME = 'fcm_token'
        """))
        
        if result.fetchone():
            logger.info("✅ Champ fcm_token déjà existant dans la table users")
            return True
        
        logger.info("🔄 Ajout du champ fcm_token à la table users...")
        
        # Ajouter la colonne fcm_token
        db.session.execute(text("""
            ALTER TABLE users 
            ADD COLUMN fcm_token VARCHAR(255) NULL 
            COMMENT 'Token Firebase Cloud Messaging pour notifications push'
        """))
        
        # Ajouter l'index pour les performances
        db.session.execute(text("""
            CREATE INDEX idx_users_fcm_token ON users (fcm_token)
        """))
        
        # Valider les changements
        db.session.commit()
        
        logger.info("✅ Migration fcm_token terminée avec succès")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de la migration fcm_token: {e}")
        db.session.rollback()
        return False

def check_fcm_requirements():
    """
    Vérifier que tous les prérequis FCM sont en place
    
    Returns:
        dict: Status des différents composants
    """
    import os
    from config import Config
    
    status = {
        'database_ready': False,
        'config_ready': False,
        'firebase_config_exists': False,
        'firebase_sdk_available': False
    }
    
    try:
        # Vérifier la base de données
        result = db.session.execute(text("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'users' 
            AND COLUMN_NAME = 'fcm_token'
        """))
        status['database_ready'] = result.fetchone() is not None
        
        # Vérifier la configuration
        config = Config()
        status['config_ready'] = hasattr(config, 'FIREBASE_ENABLED') and hasattr(config, 'FIREBASE_CONFIG_PATH')
        
        # Vérifier le fichier de configuration Firebase
        if status['config_ready']:
            status['firebase_config_exists'] = os.path.exists(config.FIREBASE_CONFIG_PATH)
        
        # Vérifier la disponibilité du SDK Firebase
        try:
            import firebase_admin
            status['firebase_sdk_available'] = True
        except ImportError:
            status['firebase_sdk_available'] = False
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de la vérification FCM: {e}")
    
    return status

def install_fcm_requirements():
    """
    Installer automatiquement le SDK Firebase si manquant
    
    Returns:
        bool: True si l'installation a réussi
    """
    try:
        import subprocess
        import sys
        
        logger.info("🔄 Installation du SDK Firebase Admin...")
        
        # Installer firebase-admin
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', 'firebase-admin'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("✅ SDK Firebase Admin installé avec succès")
            return True
        else:
            logger.error(f"❌ Erreur installation Firebase: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'installation Firebase: {e}")
        return False

def setup_fcm_complete():
    """
    Configuration complète du système FCM
    
    Returns:
        dict: Résultat détaillé de la configuration
    """
    results = {
        'migration': False,
        'requirements_check': {},
        'firebase_install': False,
        'overall_success': False
    }
    
    logger.info("🚀 Début de la configuration complète FCM...")
    
    # 1. Migration de la base de données
    results['migration'] = migrate_add_fcm_token()
    
    # 2. Vérification des prérequis
    results['requirements_check'] = check_fcm_requirements()
    
    # 3. Installation Firebase si nécessaire
    if not results['requirements_check']['firebase_sdk_available']:
        results['firebase_install'] = install_fcm_requirements()
        # Re-vérifier après installation
        results['requirements_check'] = check_fcm_requirements()
    else:
        results['firebase_install'] = True
    
    # 4. Évaluation globale
    results['overall_success'] = (
        results['migration'] and
        results['requirements_check']['database_ready'] and
        results['requirements_check']['config_ready'] and
        results['firebase_install']
    )
    
    if results['overall_success']:
        logger.info("🎉 Configuration FCM terminée avec succès !")
        logger.info("📋 Prochaines étapes:")
        logger.info("   1. Vérifiez que firebase-service-account.json est présent dans src/config/")
        logger.info("   2. Configurez les variables d'environnement FCM dans votre .env")
        logger.info("   3. Redémarrez l'application")
    else:
        logger.warning("⚠️ Configuration FCM incomplète. Vérifiez les erreurs ci-dessus.")
    
    return results

if __name__ == "__main__":
    # Script autonome pour migration rapide
    import sys
    import os
    
    # Ajouter le dossier parent au path pour les imports
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    
    from app import app
    
    with app.app_context():
        setup_fcm_complete() 