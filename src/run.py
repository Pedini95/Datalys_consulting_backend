import sys
import os

# Ajouter le répertoire courant au path Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# Ajouter le répertoire parent au path Python pour permettre les imports de modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

if __name__ == '__main__':
    # Déterminer si on est en production
    is_production = os.getenv('ENV', 'local') == 'production'
    
    # Configuration pour la production
    if is_production:
        app.run(
            debug=False, 
            host='0.0.0.0', 
            port=int(os.getenv('PORT', 8082)),
            threaded=True
        )
    else:
        # Mode développement
        app.run(
            debug=True, 
            host='0.0.0.0', 
            port=int(os.getenv('PORT', 8082))
        )
