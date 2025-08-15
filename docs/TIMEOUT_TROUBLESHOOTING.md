# 🔍 Guide de résolution des timeouts - Datalys Consulting Backend

## 📋 Vue d'ensemble

Ce guide vous aide à identifier et résoudre les problèmes de timeout lors du déploiement automatique de l'application Datalys Consulting Backend.

## 🚨 Causes principales des timeouts

### 1. **Timeouts Redis trop courts**
- **Problème** : `socket_connect_timeout=5, socket_timeout=5` (trop courts)
- **Solution** : Augmenté à `socket_connect_timeout=30, socket_timeout=60`

### 2. **Timeouts de base de données**
- **Problème** : `TIME_OUT=30` (insuffisant pour les connexions lentes)
- **Solution** : Augmenté à `TIME_OUT=60`

### 3. **Health checks trop agressifs**
- **Problème** : `--health-timeout=10s` (trop court)
- **Solution** : Augmenté à `--health-timeout=30s`

### 4. **Services non démarrés**
- **Problème** : MySQL/Redis non accessibles
- **Solution** : Vérification et redémarrage automatique

## 🛠️ Solutions implémentées

### ✅ **Configuration Redis optimisée**
```python
# src/utils/session_utils.py
self.redis_client = redis.Redis(
    host=redis_host,
    port=redis_port,
    db=redis_db,
    password=redis_password,
    decode_responses=True,
    socket_connect_timeout=30,  # Augmenté de 5 à 30 secondes
    socket_timeout=60,          # Augmenté de 5 à 60 secondes
    retry_on_timeout=True,      # Ajout de retry automatique
    health_check_interval=30    # Vérification de santé toutes les 30s
)
```

### ✅ **Configuration des timeouts**
```python
# src/config.py
TIME_OUT = int(os.getenv('TIME_OUT', 60))  # Augmenté de 30 à 60 secondes

# Timeouts spécifiques pour les connexions
DB_CONNECT_TIMEOUT = int(os.getenv('DB_CONNECT_TIMEOUT', 30))
DB_READ_TIMEOUT = int(os.getenv('DB_READ_TIMEOUT', 60))
REDIS_CONNECT_TIMEOUT = int(os.getenv('REDIS_CONNECT_TIMEOUT', 30))
REDIS_READ_TIMEOUT = int(os.getenv('REDIS_READ_TIMEOUT', 60))
```

### ✅ **Script de déploiement optimisé**
```bash
# scripts/deploy-optimized.sh
--health-cmd="curl -f --connect-timeout 10 --max-time 30 http://localhost:8082/health || exit 1" \
--health-interval=60s \
--health-timeout=30s \
--health-retries=5 \
--health-start-period=120s
```

## 🔧 Outils de diagnostic

### **Script de diagnostic automatique**
```bash
# Exécuter le diagnostic
./scripts/debug-timeouts.sh
```

Ce script vérifie :
- ✅ État des services Docker
- ✅ Ressources système (CPU, mémoire, disque)
- ✅ Logs du conteneur
- ✅ Connectivité réseau
- ✅ Accessibilité des services (MySQL, Redis, API)
- ✅ Variables d'environnement
- ✅ Configuration des timeouts

### **Variables d'environnement optimisées**
```bash
# src/env.production.template
TIME_OUT=60
DB_CONNECT_TIMEOUT=30
DB_READ_TIMEOUT=60
REDIS_CONNECT_TIMEOUT=30
REDIS_READ_TIMEOUT=60
HTTP_TIMEOUT=30
HTTP_CONNECT_TIMEOUT=10
```

## 🚀 Procédure de déploiement optimisée

### **1. Utiliser le script optimisé**
```bash
./scripts/deploy-optimized.sh
```

**Avantages** :
- ✅ Vérification automatique des services
- ✅ Retry automatique en cas d'échec
- ✅ Health checks optimisés
- ✅ Gestion des timeouts appropriés
- ✅ Nettoyage automatique

### **2. Monitoring pendant le déploiement**
```bash
# Surveiller les logs en temps réel
docker logs -f datalys-api

# Vérifier l'état des services
docker ps -a

# Tester la connectivité
curl -f --connect-timeout 10 --max-time 30 http://localhost:8082/health
```

## 🔍 Diagnostic manuel

### **1. Vérifier les services Docker**
```bash
docker ps -a
docker logs redis-db --tail=20
docker logs mysql-db --tail=20
```

### **2. Tester la connectivité**
```bash
# Test MySQL
timeout 10 mysql -h localhost -P 3306 -u root -p -e "SELECT 1;"

# Test Redis
timeout 10 redis-cli ping

# Test API
curl -f --connect-timeout 10 --max-time 30 http://localhost:8082/health
```

### **3. Vérifier les ressources**
```bash
# CPU et mémoire
top -bn1

# Espace disque
df -h

# Ports ouverts
netstat -tlnp | grep -E "(8082|3306|6379)"
```

## 🚨 Actions d'urgence

### **Si l'application ne démarre pas**
1. **Vérifier les logs** : `docker logs datalys-api --tail=50`
2. **Redémarrer les services** : `docker restart redis-db mysql-db`
3. **Vérifier l'espace disque** : `df -h`
4. **Nettoyer Docker** : `docker system prune -f`

### **Si les timeouts persistent**
1. **Augmenter les timeouts** dans `src/config.py`
2. **Vérifier la connectivité réseau**
3. **Redémarrer les conteneurs** : `docker restart datalys-api`
4. **Utiliser le script de diagnostic** : `./scripts/debug-timeouts.sh`

## 📊 Monitoring recommandé

### **Variables à surveiller**
- `TIME_OUT` : Timeout global (60s recommandé)
- `DB_CONNECT_TIMEOUT` : Connexion DB (30s recommandé)
- `REDIS_CONNECT_TIMEOUT` : Connexion Redis (30s recommandé)
- `HTTP_TIMEOUT` : Requêtes HTTP (30s recommandé)

### **Métriques importantes**
- Temps de réponse de l'API
- Utilisation CPU/mémoire
- Espace disque disponible
- État des services Docker

## ✅ Checklist de résolution

- [ ] Exécuter `./scripts/debug-timeouts.sh`
- [ ] Vérifier que tous les services Docker sont démarrés
- [ ] Augmenter les timeouts dans la configuration
- [ ] Utiliser le script de déploiement optimisé
- [ ] Vérifier les logs pour les erreurs spécifiques
- [ ] Tester la connectivité de tous les services
- [ ] Surveiller les ressources système

## 📞 Support

En cas de problème persistant :
1. Exécuter le diagnostic complet
2. Collecter les logs : `docker logs datalys-api > logs.txt`
3. Vérifier la configuration : `cat src/config.py`
4. Tester la connectivité : `./scripts/debug-timeouts.sh`

---

**Dernière mise à jour** : $(date)
**Version** : 1.0 