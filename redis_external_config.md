# Configuration Redis pour connexions externes

## 🔧 Configuration Redis sur le serveur

### 1. Modifier la configuration Redis

Éditez le fichier de configuration Redis (généralement `/etc/redis/redis.conf`) :

```bash
sudo nano /etc/redis/redis.conf
```

### 2. Modifier les paramètres

Trouvez et modifiez ces lignes :

```conf
# Commenter ou modifier cette ligne pour accepter les connexions externes
# bind 127.0.0.1
bind 0.0.0.0

# Désactiver le mode protégé (optionnel, pour le développement)
protected-mode no

# Configurer un mot de passe pour la sécurité (recommandé)
requirepass votre_mot_de_passe_redis
```

### 3. Redémarrer Redis

```bash
sudo systemctl restart redis
# ou
sudo service redis restart
```

### 4. Vérifier que Redis écoute sur toutes les interfaces

```bash
sudo netstat -tlnp | grep 6379
```

Vous devriez voir quelque chose comme :
```
tcp        0      0 0.0.0.0:6379          0.0.0.0:*               LISTEN
```

### 5. Configurer le firewall (si nécessaire)

```bash
sudo ufw allow 6379
```

## 🔒 Configuration de sécurité recommandée

### Option A : Avec mot de passe Redis

Dans votre `.env.local` :
```env
REDIS_HOST=82.112.253.137
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=votre_mot_de_passe_redis
```

### Option B : Avec restriction IP

Dans `redis.conf` :
```conf
bind 82.112.253.137 127.0.0.1
```

## ⚠️ Avertissements de sécurité

1. **Exposer Redis** : Rend Redis accessible depuis l'extérieur
2. **Sécurité** : Utilisez toujours un mot de passe fort
3. **Firewall** : Limitez l'accès aux IPs autorisées
4. **Production** : Considérez utiliser un VPN ou tunnel SSH

## 🚀 Alternative recommandée : Tunnel SSH

Pour plus de sécurité, utilisez un tunnel SSH :

```bash
ssh -L 6379:localhost:6379 user@82.112.253.137
```

Puis dans votre `.env.local` :
```env
REDIS_HOST=localhost
REDIS_PORT=6379
```

## ✅ Test de la configuration

Utilisez le script `test_redis_server.py` pour tester la connexion.
