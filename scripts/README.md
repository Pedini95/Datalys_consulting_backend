# 📜 Scripts de Déploiement - Datalys Consulting Backend

Ce dossier contient les scripts essentiels pour le déploiement et la maintenance du backend.

## 🚀 Scripts disponibles

### 1. `deploy.sh` - Déploiement principal
**Usage quotidien** - Déploie vos modifications sur le serveur VPS

```bash
./scripts/deploy.sh
```

**Ce qu'il fait :**
- ✅ Transfère les fichiers modifiés vers le serveur
- ✅ Redémarre le backend
- ✅ Vérifie que l'API fonctionne
- ⏱️ Temps : ~30 secondes

**Quand l'utiliser :**
- Après avoir modifié du code Python
- Après avoir modifié des templates HTML
- Pour tout changement de fichier dans `src/`

---

### 2. `configure-mysql.sh` - Configuration MySQL
**Setup initial uniquement**

```bash
./scripts/configure-mysql.sh
```

**Ce qu'il fait :**
- Configure la base de données MySQL
- Crée les tables nécessaires

**Quand l'utiliser :**
- Lors du premier déploiement
- Après avoir supprimé la base de données

---

### 3. `fix-permissions.sh` - Correction des permissions
**Dépannage**

```bash
./scripts/fix-permissions.sh
```

**Ce qu'il fait :**
- Corrige les permissions des fichiers et dossiers
- Résout les problèmes d'accès en écriture

**Quand l'utiliser :**
- En cas d'erreurs de permissions
- Après avoir modifié la structure des dossiers

---

## 📊 Workflow de déploiement recommandé

### Déploiement quotidien (30 secondes)

```bash
# 1. Modifier votre code localement
# 2. Tester localement
# 3. Commit et push
git add .
git commit -m "Description des modifications"
git push origin develop

# 4. Déployer
./scripts/deploy.sh
```

### Premier déploiement complet

```bash
# 1. Déployer les fichiers
./scripts/deploy.sh

# 2. Configurer MySQL (si besoin)
ssh root@82.112.253.137
./scripts/configure-mysql.sh
```

---

## ⚙️ Configuration

### Variables d'environnement (serveur VPS)

Les variables sont configurées dans le fichier `.env` sur le serveur :
- `DATABASE_URL` - Connexion MySQL
- `REDIS_URL` - Connexion Redis
- `SECRET_KEY` - Clé secrète JWT
- `FIREBASE_CREDENTIALS` - Credentials Firebase

### Serveur VPS

- **IP**: 82.112.253.137
- **SSH**: root@82.112.253.137
- **API**: http://82.112.253.137:8082
- **Health Check**: http://82.112.253.137:8082/health

---

## 🔧 Dépannage

### Le déploiement échoue

```bash
# Vérifier l'état des services
ssh root@82.112.253.137 "docker ps"

# Voir les logs du backend
ssh root@82.112.253.137 "docker logs datalys-api --tail 50"
```

### L'API ne répond pas

```bash
# Redémarrer manuellement
ssh root@82.112.253.137 "cd /root/Datalys_consulting_backend && docker-compose restart datalys-api"
```

### Erreurs de permissions

```bash
./scripts/fix-permissions.sh
```

---

## 📝 Notes

- **Watchtower désactivé** : Le déploiement automatique via Watchtower était trop lent (10 min). Utilisez `deploy.sh` à la place (30 sec).
- **Pas de rebuild Docker** : Le script transfère uniquement les fichiers et redémarre, ce qui est beaucoup plus rapide.
- **Rebuild complet** : Si vous modifiez `requirements.txt` ou `Dockerfile`, faites un rebuild complet sur le serveur.

---

## 🚨 Important

⚠️ **Ne committez JAMAIS** les fichiers `.env` ou les credentials Firebase !

✅ **Toujours tester localement** avant de déployer en production
