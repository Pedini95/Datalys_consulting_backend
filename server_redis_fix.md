# Correction Redis sur le serveur

## 🔧 Problème identifié

L'application ne peut pas se connecter à Redis car :
- **Application** : Utilise `REDIS_HOST=localhost`
- **Redis** : Mappé sur `82.112.253.137:6379`
- **Résultat** : Connexion impossible

## 🚀 Solution

### 1. Redémarrer l'application avec la correction

```bash
# Sur le serveur (/opt/Datalys_consulting_backend)
docker-compose down
docker-compose --profile production up -d
```

### 2. Vérifier la connexion Redis

```bash
# Vérifier que Redis écoute sur la bonne interface
netstat -tlnp | grep 6379

# Vous devriez voir :
# tcp        0      0 82.112.253.137:6379    0.0.0.0:*               LISTEN
```

### 3. Vérifier les logs de l'application

```bash
# Vérifier que l'application se connecte à Redis
docker logs datalys-api --tail 20 | grep -i redis
```

## ✅ Résultat attendu

Après le redémarrage, vous devriez voir dans les logs :
- ✅ `Session Redis créée avec succès pour l'utilisateur X`
- ✅ Plus d'erreurs `Redis non disponible`
- ✅ `Cache Redis FCM disponible`

## 🧪 Test après correction

Une fois redémarré, testez :

```bash
# Depuis votre machine locale
python3 test_fcm_system.py
```

Vous devriez voir :
- ✅ `FCM Status: enabled`
- ✅ `Cache FCM: available`
- ✅ `Notification envoyée: success`
