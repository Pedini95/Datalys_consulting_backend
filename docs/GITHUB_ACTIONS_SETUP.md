# 🚀 Configuration du Déploiement Automatique avec GitHub Actions

**Date:** 12 octobre 2025  
**Objectif:** Déployer automatiquement sur le VPS à chaque push sur `main`

---

## 📋 Prérequis

- [x] Compte GitHub avec accès au repository
- [x] Accès SSH au serveur VPS (82.112.253.137)
- [x] Droits administrateur sur le repository GitHub

---

## 🔐 Étape 1: Générer une Clé SSH pour GitHub Actions

### Sur votre machine locale ou le serveur :

```bash
# Générer une nouvelle paire de clés SSH (sans passphrase)
ssh-keygen -t ed25519 -C "github-actions@datalysconsulting.com" -f ~/.ssh/github_actions_deploy

# Afficher la clé PUBLIQUE
cat ~/.ssh/github_actions_deploy.pub

# Afficher la clé PRIVÉE (à copier dans GitHub Secrets)
cat ~/.ssh/github_actions_deploy
```

### Ajouter la clé publique au serveur :

```bash
# Se connecter au serveur
ssh root@82.112.253.137

# Ajouter la clé publique aux clés autorisées
cat >> ~/.ssh/authorized_keys << 'EOF'
# Coller ici la clé PUBLIQUE (github_actions_deploy.pub)
EOF

# Sécuriser les permissions
chmod 600 ~/.ssh/authorized_keys
chmod 700 ~/.ssh

# Tester la connexion depuis votre machine
ssh -i ~/.ssh/github_actions_deploy root@82.112.253.137
```

---

## 🔧 Étape 2: Configurer les Secrets GitHub

### Aller sur GitHub :

1. Ouvrir votre repository sur GitHub
2. Aller dans **Settings** → **Secrets and variables** → **Actions**
3. Cliquer sur **New repository secret**

### Créer 3 secrets :

#### Secret 1: `SSH_HOST`
```
Nom: SSH_HOST
Valeur: 82.112.253.137
```

#### Secret 2: `SSH_USER`
```
Nom: SSH_USER
Valeur: root
```

#### Secret 3: `SSH_PRIVATE_KEY`
```
Nom: SSH_PRIVATE_KEY
Valeur: [Copier TOUT le contenu de ~/.ssh/github_actions_deploy]
```

**Format de la clé privée :**
```
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
...
(plusieurs lignes)
...
-----END OPENSSH PRIVATE KEY-----
```

⚠️ **IMPORTANT:** Copiez TOUTE la clé, y compris les lignes BEGIN et END !

---

## 📸 Captures d'écran du processus

### 1. Accéder aux Secrets
```
GitHub Repository → Settings → Secrets and variables → Actions
```

### 2. Ajouter un Secret
```
Click "New repository secret"
Name: SSH_HOST
Secret: 82.112.253.137
Click "Add secret"
```

### 3. Vérifier les Secrets
Vous devriez voir 3 secrets :
- ✅ SSH_HOST
- ✅ SSH_USER  
- ✅ SSH_PRIVATE_KEY

---

## 🧪 Étape 3: Tester le Déploiement

### Option 1: Push sur main

```bash
# Faire un commit et push
git add .
git commit -m "test: déploiement automatique"
git push origin main
```

### Option 2: Déclenchement manuel

1. Aller sur GitHub → **Actions**
2. Sélectionner le workflow **"🚀 Deploy to Production"**
3. Cliquer sur **"Run workflow"**
4. Sélectionner la branche `main`
5. Cliquer sur **"Run workflow"**

---

## 📊 Étape 4: Suivre le Déploiement

### Sur GitHub :

1. Aller dans l'onglet **Actions**
2. Cliquer sur le workflow en cours
3. Suivre les logs en temps réel

### Étapes du déploiement :

```
✅ 1/7: Sauvegarde de la configuration actuelle
✅ 2/7: Récupération du code depuis Git
✅ 3/7: Vérification du fichier .env
✅ 4/7: Reconstruction de l'image Docker
✅ 5/7: Arrêt du conteneur actuel
✅ 6/7: Démarrage du nouveau conteneur
✅ 7/7: Vérification du démarrage
```

---

## 🔍 Vérification Post-Déploiement

### Sur le serveur :

```bash
# Vérifier que le conteneur tourne
docker ps | grep datalys-api

# Vérifier les logs
docker logs datalys-api --tail 50

# Tester l'API
curl http://localhost:8082/health
```

### Depuis l'extérieur :

```bash
# Tester l'API
curl http://82.112.253.137:8082/health

# Tester le login
curl -X POST http://82.112.253.137:8082/auth/login \
  -H "Content-Type: application/json" \
  -d '{"identifier":"admin@datalysconsulting.com","password":"Password123"}'
```

---

## 🚨 Dépannage

### Erreur: "Permission denied (publickey)"

**Cause:** La clé SSH n'est pas correctement configurée

**Solution:**
```bash
# Vérifier que la clé publique est sur le serveur
ssh root@82.112.253.137 "cat ~/.ssh/authorized_keys"

# Vérifier les permissions
ssh root@82.112.253.137 "ls -la ~/.ssh/"
```

### Erreur: "docker: command not found"

**Cause:** Docker n'est pas installé ou pas dans le PATH

**Solution:**
```bash
ssh root@82.112.253.137 "which docker"
```

### Erreur: "File .env not found"

**Cause:** Le fichier .env n'existe pas sur le serveur

**Solution:**
```bash
# Créer le fichier .env sur le serveur
ssh root@82.112.253.137
cd /root/datalys-backend
bash scripts/security/secure-docker-secrets.sh
```

### Le conteneur ne démarre pas

**Solution:**
```bash
# Voir les logs complets
ssh root@82.112.253.137 "docker logs datalys-api"

# Vérifier la configuration
ssh root@82.112.253.137 "docker inspect datalys-api"
```

---

## 🔄 Rollback en cas de problème

### Revenir à la version précédente :

```bash
ssh root@82.112.253.137

# Lister les backups
ls -lh /backup/deployments/

# Restaurer un backup
cd /root/datalys-backend
cp -r /backup/deployments/backup_YYYYMMDD_HHMMSS/* .

# Redémarrer
docker stop datalys-api
docker rm datalys-api
docker run -d --name datalys-api \
  --network bridge \
  -p 8082:8082 \
  --env-file .env \
  --restart unless-stopped \
  -e DB_HOST=172.17.0.2 \
  datalys_consulting_backend-datalys-api:latest
```

---

## 📈 Améliorations Futures

### À implémenter :

- [ ] **Tests automatiques** avant déploiement
- [ ] **Notifications Slack/Email** en cas d'échec
- [ ] **Déploiement Blue-Green** (zéro downtime)
- [ ] **Variables d'environnement** par branche (dev/staging/prod)
- [ ] **Health checks** automatiques post-déploiement
- [ ] **Métriques de déploiement** (temps, succès/échec)

### Exemple avec tests :

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          python -m pytest tests/
  
  deploy:
    needs: test  # Ne déploie que si les tests passent
    runs-on: ubuntu-latest
    # ... reste du workflow
```

---

## 📚 Ressources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [SSH Agent Action](https://github.com/webfactory/ssh-agent)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)

---

## ✅ Checklist de Configuration

- [ ] Clé SSH générée
- [ ] Clé publique ajoutée au serveur
- [ ] 3 secrets GitHub configurés (SSH_HOST, SSH_USER, SSH_PRIVATE_KEY)
- [ ] Fichier .env présent sur le serveur
- [ ] Workflow GitHub Actions créé (.github/workflows/deploy.yml)
- [ ] Premier déploiement testé
- [ ] Rollback testé
- [ ] Documentation lue et comprise

---

**Créé le:** 12 octobre 2025  
**Dernière mise à jour:** 12 octobre 2025  
**Statut:** ✅ Prêt à l'emploi
