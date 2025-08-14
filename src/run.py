from app import app
import os 

if __name__ == '__main__':
    # Déterminer si on est en production
    is_production = os.getenv('ENV', 'local') == 'production'
    
    # Configuration pour la production
    if is_production:
        app.run(
            debug=False, 
            host='0.0.0.0', 
            port=int(os.getenv('PORT', 8081)),
            threaded=True
        )
    else:
        # Mode développement
        app.run(
            debug=True, 
            host='0.0.0.0', 
            port=int(os.getenv('PORT', 8081))
        )
