from flask import Blueprint, jsonify
from sqlalchemy import text
from extensions import db
import logging
from utils.notification import EmailService

logger = logging.getLogger(__name__)

health_bp = Blueprint('health', __name__)

@health_bp.route('/health', methods=['GET'])
def health_check():
    """Vérification de la santé de l'application et de la base de données"""
    
    health_status = {
        "status": "healthy",
        "timestamp": None,
        "database": {
            "status": "unknown",
            "version": None,
            "tables_count": 0,
            "error": None
        },
        "application": {
            "status": "running",
            "version": "1.0.0"
        }
    }
    
    try:
        # Test de connexion à la base de données
        with db.engine.connect() as connection:
            # Test de version MySQL
            result = connection.execute(text("SELECT VERSION()"))
            version_row = result.fetchone()
            if version_row:
                health_status["database"]["version"] = version_row[0]
            
            # Compter les tables
            result = connection.execute(text("SHOW TABLES"))
            tables = result.fetchall()
            health_status["database"]["tables_count"] = len(tables)
            
            # Test de performance simple
            result = connection.execute(text("SELECT 1"))
            test_row = result.fetchone()
            if test_row and test_row[0] == 1:
                health_status["database"]["status"] = "connected"
            else:
                health_status["database"]["status"] = "error"
                health_status["database"]["error"] = "Test query failed"
                
    except Exception as e:
        health_status["database"]["status"] = "error"
        health_status["database"]["error"] = str(e)
        health_status["status"] = "unhealthy"
        logger.error(f"Database health check failed: {str(e)}")
    
    # Déterminer le statut global
    if health_status["database"]["status"] == "connected":
        health_status["status"] = "healthy"
    else:
        health_status["status"] = "unhealthy"
    
    # Code de statut HTTP approprié
    status_code = 200 if health_status["status"] == "healthy" else 503
    
    return jsonify(health_status), status_code

@health_bp.route('/health/db', methods=['GET'])
def database_health():
    """Vérification détaillée de la base de données"""
    
    try:
        with db.engine.connect() as connection:
            # Informations détaillées sur la base de données
            db_info = {}
            
            # Version MySQL
            result = connection.execute(text("SELECT VERSION()"))
            version_row = result.fetchone()
            if version_row:
                db_info["version"] = version_row[0]
            
            # Base de données actuelle
            result = connection.execute(text("SELECT DATABASE()"))
            db_row = result.fetchone()
            if db_row:
                db_info["current_database"] = db_row[0]
            
            # Tables et leur taille
            result = connection.execute(text("""
                SELECT 
                    table_name,
                    table_rows,
                    ROUND(((data_length + index_length) / 1024 / 1024), 2) AS 'size_mb'
                FROM information_schema.tables 
                WHERE table_schema = DATABASE()
                ORDER BY (data_length + index_length) DESC
            """))
            
            tables_info = []
            for row in result.fetchall():
                tables_info.append({
                    "name": row[0],
                    "rows": row[1],
                    "size_mb": row[2]
                })
            
            db_info["tables"] = tables_info
            db_info["total_tables"] = len(tables_info)
            
            # Test de performance
            import time
            start_time = time.time()
            connection.execute(text("SELECT 1"))
            query_time = (time.time() - start_time) * 1000  # en millisecondes
            
            db_info["query_response_time_ms"] = round(query_time, 2)
            
            return jsonify({
                "status": "success",
                "database": db_info
            }), 200
            
    except Exception as e:
        logger.error(f"Detailed database health check failed: {str(e)}")
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 503 

@health_bp.route('/test-email', methods=['POST'])
def test_email():
    """
    Tester l'envoi d'email
    """
    try:
        from flask import request
        
        data = request.get_json() or {}
        to_email = data.get('to_email', 'test@example.com')
        
        # Créer le service email
        email_service = EmailService()
        
        # Contenu de test
        subject = "Test Email - Datalys Consulting"
        html_content = """
        <html>
        <body>
            <h1>Test Email</h1>
            <p>Ceci est un email de test pour vérifier la configuration SMTP.</p>
            <p>Si vous recevez cet email, la configuration est correcte !</p>
            <br>
            <p>Cordialement,<br>L'équipe Datalys Consulting</p>
        </body>
        </html>
        """
        
        # Envoyer l'email
        success = email_service.send_email(
            to_email=to_email,
            subject=subject,
            html_content=html_content
        )
        
        if success:
            return jsonify({
                'status': 'success',
                'message': f'Email envoyé avec succès à {to_email}'
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': 'Erreur lors de l\'envoi de l\'email'
            }), 500
            
    except Exception as e:
        logger.error(f"Email test failed: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Erreur lors du test email',
            'error': str(e)
        }), 500 