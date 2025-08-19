# Vérification des logs du serveur

## 🔍 Problème persistant

L'application ne peut toujours pas se connecter à Redis malgré la correction. Vérifions les logs.

## 📋 Commandes à exécuter sur le serveur

### 1. Vérifier les logs de l'application

```bash
# Voir les logs récents de l'API
docker logs datalys-api --tail 50

# Chercher spécifiquement les erreurs Redis
docker logs datalys-api --tail 100 | grep -i redis

# Chercher les erreurs de connexion
docker logs datalys-api --tail 100 | grep -i "connection\|connect"
```

### 2. Vérifier la configuration réseau

```bash
# Vérifier que Redis écoute bien sur l'IP externe
netstat -tlnp | grep 6379

# Vérifier que l'application peut accéder à Redis
docker exec datalys-api ping 82.112.253.137

# Tester la connexion Redis depuis le conteneur
docker exec datalys-api redis-cli -h 82.112.253.137 -p 6379 ping
```

### 3. Vérifier les variables d'environnement

```bash
# Vérifier les variables d'environnement du conteneur
docker exec datalys-api env | grep REDIS

# Vérifier la configuration de l'application
docker exec datalys-api cat /app/src/config.py | grep REDIS
```

## 🔧 Solutions possibles

### Option 1: Problème de réseau Docker
Si l'application ne peut pas accéder à l'IP externe depuis le conteneur, essayez :
```bash
# Utiliser l'IP du host depuis le conteneur
docker exec datalys-api redis-cli -h host.docker.internal -p 6379 ping
```

### Option 2: Problème de firewall
Vérifiez que le port 6379 est ouvert :
```bash
# Vérifier le firewall
ufw status | grep 6379
```

### Option 3: Configuration Redis
Vérifiez que Redis accepte les connexions externes :
```bash
# Vérifier la configuration Redis
docker exec redis-db redis-cli config get bind
```

## 📊 Résultat attendu

Après vérification, vous devriez voir :
- ✅ Redis écoute sur `82.112.253.137:6379`
- ✅ L'application peut se connecter à Redis
- ✅ Plus d'erreurs `Redis non disponible` dans les logs
