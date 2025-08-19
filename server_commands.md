# Commandes à exécuter sur le serveur

## 🚀 Navigation vers le projet

```bash
# Naviguer vers le répertoire du projet
cd /root/Datalys_consulting_backend

# Vérifier que vous êtes dans le bon répertoire
ls -la

# Vous devriez voir docker-compose.yml
```

## 🔧 Redémarrage des conteneurs

```bash
# Arrêter les conteneurs actuels
docker-compose down

# Redémarrer avec la nouvelle configuration Redis
docker-compose --profile production up -d

# Vérifier que les conteneurs sont démarrés
docker ps
```

## 🧪 Vérification Redis

```bash
# Vérifier les logs Redis
docker logs redis-db

# Vérifier que Redis écoute sur la bonne IP
netstat -tlnp | grep 6379

# Vous devriez voir quelque chose comme :
# tcp        0      0 82.112.253.137:6379    0.0.0.0:*               LISTEN
```

## 🔍 Test de connexion Redis

```bash
# Test de connexion Redis depuis le serveur
redis-cli -h 82.112.253.137 -p 6379 ping

# Si ça fonctionne, vous devriez voir : PONG
```

## 📊 Vérification de l'application

```bash
# Vérifier les logs de l'API
docker logs datalys-api

# Vérifier le statut de santé
curl http://localhost:8082/health
```

## 🚨 En cas de problème

```bash
# Voir tous les conteneurs (même arrêtés)
docker ps -a

# Redémarrer seulement Redis
docker restart redis-db

# Vérifier la configuration réseau
docker network ls
docker network inspect bridge
```
