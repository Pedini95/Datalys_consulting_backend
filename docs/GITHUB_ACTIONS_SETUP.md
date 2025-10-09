# 🚀 Configuration du déploiement automatique avec GitHub Actions

## 📋 Vue d'ensemble

Ce guide explique comment configurer le déploiement automatique de votre backend sur le VPS via GitHub Actions.

---

## 🎯 Fonctionnement

```
┌─────────────────┐
│   DÉVELOPPEUR   │
│                 │
│  git push       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  GITHUB REPO    │
│                 │
│  Détecte push   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ GITHUB ACTIONS  │
│                 │
│  Exécute        │
│  workflow       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   VPS SERVER    │
│ 82.112.253.137  │
│                 │
│  1. git pull    │
│  2. restart     │
│  3. verify      │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│  ✅ DÉPLOYÉ     │
└─────────────────┘
```

---

## ⚙️ Étape 1 : Configurer les secrets GitHub

### 1.1 Aller sur GitHub

1. Ouvrez votre repository sur GitHub
2. Cliquez sur **Settings** (⚙️)
3. Dans le menu de gauche, cliquez sur **Secrets and variables** → **Actions**
4. Cliquez sur **New repository secret**

### 1.2 Ajouter les secrets

Ajoutez les 3 secrets suivants :

#### Secret 1 : `SSH_HOST`
```
Name: SSH_HOST
Value: 82.112.253.137
```

#### Secret 2 : `SSH_USER`
```
Name: SSH_USER
Value: root
```

#### Secret 3 : `SSH_PASSWORD`
```
Name: SSH_PASSWORD
Value: [Votre mot de passe root du VPS]
```

> ⚠️ **Important** : Ne partagez JAMAIS ces secrets publiquement !

---

## 🔐 Alternative : Utiliser une clé SSH (Plus sécurisé)

### Option A : Clé SSH existante

Si vous avez déjà une clé SSH configurée :

```bash
# Afficher votre clé privée
cat ~/.ssh/id_rsa
```

Copiez tout le contenu (y compris `-----BEGIN` et `-----END`)

### Option B : Créer une nouvelle clé SSH

```bash
# Générer une nouvelle clé SSH
ssh-keygen -t rsa -b 4096 -C "github-actions" -f ~/.ssh/github_actions_key -N ""

# Afficher la clé privée
cat ~/.ssh/github_actions_key

# Afficher la clé publique
cat ~/.ssh/github_actions_key.pub
```

### Ajouter la clé publique au VPS

```bash
# Sur votre machine locale
ssh-copy-id -i ~/.ssh/github_actions_key.pub root@82.112.253.137

# Ou manuellement sur le VPS
ssh root@82.112.253.137
echo "VOTRE_CLE_PUBLIQUE" >> ~/.ssh/authorized_keys
```

### Ajouter la clé privée comme secret GitHub

```
Name: SSH_PRIVATE_KEY
Value: [Contenu complet de la clé privée]
```

### Modifier le workflow pour utiliser la clé SSH

Remplacez dans `.github/workflows/deploy.yml` :

```yaml
# Remplacer cette ligne :
password: ${{ secrets.SSH_PASSWORD }}

# Par :
key: ${{ secrets.SSH_PRIVATE_KEY }}
```

---

## 📝 Étape 2 : Configurer Git sur le VPS

Sur le VPS, assurez-vous que le projet est un repository Git :

```bash
# Se connecter au VPS
ssh root@82.112.253.137

# Aller dans le dossier du projet
cd /root/Datalys_consulting_backend

# Vérifier que c'est un repo Git
git status

# Si ce n'est pas un repo Git, l'initialiser
git init
git remote add origin https://github.com/VOTRE_USERNAME/VOTRE_REPO.git
git fetch origin
git checkout -b develop origin/develop
```

### Configuration Git pour éviter les conflits

```bash
# Sur le VPS
cd /root/Datalys_consulting_backend

# Configurer Git pour accepter les reset
git config --local receive.denyCurrentBranch ignore

# Ignorer les modifications locales lors du pull
git config --local pull.rebase false
```

---

## 🚀 Étape 3 : Tester le déploiement automatique

### 3.1 Déclenchement automatique

Le déploiement se déclenche automatiquement lors d'un push sur :
- `main`
- `master`
- `develop`

```bash
# Sur votre machine locale
cd /Users/pkone/Documents/workspace_flask_python/Datalys_consulting_backend

# Faire une modification
echo "# Test déploiement automatique" >> README.md

# Commit et push
git add .
git commit -m "Test: déploiement automatique"
git push origin develop
```

### 3.2 Déclenchement manuel

Vous pouvez aussi déclencher manuellement le déploiement :

1. Allez sur GitHub → **Actions**
2. Sélectionnez le workflow **🚀 Déploiement automatique**
3. Cliquez sur **Run workflow**
4. Sélectionnez la branche
5. Cliquez sur **Run workflow**

---

## 📊 Étape 4 : Surveiller le déploiement

### Sur GitHub

1. Allez sur **Actions** dans votre repository
2. Vous verrez la liste des workflows en cours/terminés
3. Cliquez sur un workflow pour voir les détails
4. Chaque étape affiche ses logs

### Exemple de logs réussis

```
✅ Checkout du code
✅ Déploiement via SSH
   🔄 Début du déploiement...
   💾 Sauvegarde des fichiers sensibles...
   📥 Récupération des modifications...
   ♻️ Restauration des fichiers sensibles...
   🔄 Redémarrage du backend...
   ⏳ Attente du démarrage...
   🏥 Vérification de la santé de l'API...
   ✅ Déploiement terminé avec succès !
✅ Notification de succès
   🎉 Déploiement réussi sur 82.112.253.137
   🌐 API: http://82.112.253.137:8082
```

---

## 🔧 Workflow détaillé

Le workflow `.github/workflows/deploy.yml` effectue les actions suivantes :

### 1. **Checkout du code**
```yaml
- name: 📥 Checkout du code
  uses: actions/checkout@v3
```
Récupère le code depuis GitHub

### 2. **Connexion SSH au VPS**
```yaml
- name: 🚀 Déploiement via SSH
  uses: appleboy/ssh-action@master
```
Se connecte au VPS via SSH

### 3. **Sauvegarde des fichiers sensibles**
```bash
cp src/.env /tmp/.env.backup
```
Sauvegarde le fichier `.env` pour ne pas l'écraser

### 4. **Pull des modifications**
```bash
git fetch origin
git reset --hard origin/develop
```
Récupère les dernières modifications depuis GitHub

### 5. **Restauration des fichiers sensibles**
```bash
cp /tmp/.env.backup src/.env
```
Restaure le fichier `.env`

### 6. **Redémarrage du backend**
```bash
docker-compose restart datalys-api
```
Redémarre le container Docker

### 7. **Vérification de santé**
```bash
curl -f http://localhost:8082/health
```
Vérifie que l'API fonctionne correctement

---

## 🛠️ Personnalisation du workflow

### Changer les branches de déploiement

```yaml
on:
  push:
    branches:
      - main          # Déployer sur push vers main
      - production    # Déployer sur push vers production
```

### Ajouter des notifications Slack/Discord

```yaml
- name: 📢 Notification Slack
  if: success()
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
    text: "✅ Déploiement réussi sur le VPS"
```

### Exécuter des migrations SQL automatiquement

Ajoutez dans le script SSH :

```yaml
script: |
  # ... (code existant)
  
  # Exécuter les migrations SQL
  echo "🗄️ Exécution des migrations..."
  docker exec mysql-db mysql -u root -p'root' datalys_consulting < src/migrations/VOTRE_MIGRATION.sql
  
  # Redémarrer le backend
  docker-compose restart datalys-api
```

---

## ❌ Résolution des problèmes

### Erreur : "can't connect without a private SSH key or password"

**Cause** : Les secrets GitHub ne sont pas configurés

**Solution** :
1. Vérifiez que vous avez ajouté les secrets `SSH_HOST`, `SSH_USER`, et `SSH_PASSWORD` (ou `SSH_PRIVATE_KEY`)
2. Vérifiez l'orthographe des noms de secrets
3. Assurez-vous que les secrets sont dans le bon repository

### Erreur : "Permission denied (publickey,password)"

**Cause** : Mot de passe incorrect ou clé SSH non autorisée

**Solution** :
1. Vérifiez que le mot de passe est correct
2. Si vous utilisez une clé SSH, assurez-vous qu'elle est ajoutée aux `authorized_keys` du VPS

### Erreur : "fatal: not a git repository"

**Cause** : Le dossier sur le VPS n'est pas un repository Git

**Solution** :
```bash
ssh root@82.112.253.137
cd /root/Datalys_consulting_backend
git init
git remote add origin https://github.com/VOTRE_USERNAME/VOTRE_REPO.git
git fetch origin
git checkout develop
```

### Erreur : "curl: (7) Failed to connect"

**Cause** : L'API n'a pas démarré correctement

**Solution** :
1. Augmentez le temps d'attente (`sleep 15` → `sleep 30`)
2. Vérifiez les logs Docker : `docker logs datalys-api`
3. Vérifiez que MySQL et Redis sont actifs

---

## 🔒 Sécurité

### ✅ Bonnes pratiques

1. **Utilisez des clés SSH** plutôt que des mots de passe
2. **Ne commitez JAMAIS** les secrets dans le code
3. **Limitez les permissions** de la clé SSH (lecture seule si possible)
4. **Utilisez des secrets GitHub** pour toutes les informations sensibles
5. **Activez la 2FA** sur votre compte GitHub

### ❌ À éviter

1. ❌ Ne mettez pas de mots de passe dans le workflow
2. ❌ Ne partagez pas vos secrets GitHub
3. ❌ N'utilisez pas le compte root en production (créez un utilisateur dédié)
4. ❌ Ne désactivez pas la vérification de santé

---

## 📈 Améliorations futures

### 1. **Déploiement Blue-Green**

Déployer sur un second container, tester, puis basculer :

```yaml
script: |
  # Démarrer un nouveau container
  docker-compose up -d datalys-api-new
  
  # Tester
  curl -f http://localhost:8083/health
  
  # Basculer
  docker-compose stop datalys-api
  docker-compose rm -f datalys-api
  docker rename datalys-api-new datalys-api
```

### 2. **Tests automatiques avant déploiement**

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: 🧪 Tests unitaires
        run: pytest tests/
  
  deploy:
    needs: test
    runs-on: ubuntu-latest
    # ... (déploiement)
```

### 3. **Rollback automatique en cas d'échec**

```yaml
- name: 🔄 Rollback en cas d'échec
  if: failure()
  run: |
    ssh root@82.112.253.137 "cd /root/Datalys_consulting_backend && git reset --hard HEAD~1 && docker-compose restart datalys-api"
```

---

## 📞 Support

Pour toute question :
- **Documentation** : `/docs/GITHUB_ACTIONS_SETUP.md`
- **GitHub Actions Docs** : https://docs.github.com/en/actions
- **SSH Action Docs** : https://github.com/appleboy/ssh-action

---

## ✅ Checklist de configuration

- [ ] Secrets GitHub configurés (`SSH_HOST`, `SSH_USER`, `SSH_PASSWORD` ou `SSH_PRIVATE_KEY`)
- [ ] Repository Git initialisé sur le VPS
- [ ] Remote Git configuré sur le VPS
- [ ] Workflow `.github/workflows/deploy.yml` créé
- [ ] Workflow commité et pushé sur GitHub
- [ ] Test de déploiement manuel réussi
- [ ] Test de déploiement automatique réussi
- [ ] Notifications configurées (optionnel)

---

**Date de création** : 9 octobre 2025  
**Version** : 1.0.0  
**Statut** : ✅ Prêt à l'emploi

