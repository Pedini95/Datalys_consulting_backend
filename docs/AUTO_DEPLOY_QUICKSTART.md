# ⚡ Déploiement Automatique - Guide Rapide

**Temps de configuration:** 5 minutes  
**Niveau:** Débutant

---

## 🎯 Objectif

À chaque fois que vous faites un `git push` sur la branche `main`, votre application sera automatiquement déployée sur le serveur VPS.

---

## 🚀 Configuration en 3 Étapes

### Étape 1: Exécuter le script de configuration

```bash
./scripts/setup-github-deploy.sh
```

Ce script va:
- ✅ Générer une clé SSH
- ✅ L'ajouter au serveur
- ✅ Afficher les secrets à configurer sur GitHub

### Étape 2: Configurer GitHub Secrets

1. Allez sur **GitHub.com** → Votre repository
2. Cliquez sur **Settings** (en haut)
3. Dans le menu de gauche: **Secrets and variables** → **Actions**
4. Cliquez sur **"New repository secret"** (bouton vert)
5. Créez ces 3 secrets (copiez-collez depuis le terminal):

| Nom | Valeur |
|-----|--------|
| `SSH_HOST` | `82.112.253.137` |
| `SSH_USER` | `root` |
| `SSH_PRIVATE_KEY` | La clé privée complète (affichée dans le terminal) |

⚠️ **Important:** Pour `SSH_PRIVATE_KEY`, copiez TOUTE la clé, y compris les lignes `-----BEGIN` et `-----END`

### Étape 3: Tester le déploiement

#### Option A: Push automatique
```bash
git add .
git commit -m "feat: activation du déploiement automatique"
git push origin develop
```

#### Option B: Déclenchement manuel
1. Allez sur GitHub → **Actions**
2. Sélectionnez **"🚀 Deploy to Production"**
3. Cliquez sur **"Run workflow"**
4. Sélectionnez `develop` et cliquez sur **"Run workflow"**

---

## 📊 Suivre le Déploiement

1. Allez sur GitHub → **Actions**
2. Cliquez sur le workflow en cours
3. Vous verrez les 7 étapes en temps réel:

```
✅ 1/7: Sauvegarde de la configuration
✅ 2/7: Récupération du code
✅ 3/7: Vérification .env
✅ 4/7: Build Docker
✅ 5/7: Arrêt ancien conteneur
✅ 6/7: Démarrage nouveau conteneur
✅ 7/7: Vérification santé
```

**Durée totale:** ~2-3 minutes

---

## ✅ Vérification

### Tester l'API après déploiement:

```bash
# Health check
curl http://82.112.253.137:8082/health

# Login test
curl -X POST http://82.112.253.137:8082/auth/login \
  -H "Content-Type: application/json" \
  -d '{"identifier":"admin@datalysconsulting.com","password":"Password123"}'
```

---

## 🔄 Workflow de Développement

```
1. Développer localement
   ↓
2. Commiter les changements
   git add .
   git commit -m "feat: nouvelle fonctionnalité"
   ↓
3. Pusher sur main
   git push origin main
   ↓
4. GitHub Actions déploie automatiquement
   (2-3 minutes)
   ↓
5. Vérifier sur http://82.112.253.137:8082
```

---

## 🚨 En Cas de Problème

### Le déploiement échoue?

1. **Vérifier les logs sur GitHub:**
   - GitHub → Actions → Cliquez sur le workflow rouge
   - Lisez l'étape qui a échoué

2. **Problèmes courants:**

| Erreur | Solution |
|--------|----------|
| `Permission denied (publickey)` | Vérifiez que `SSH_PRIVATE_KEY` est correctement configuré |
| `File .env not found` | Exécutez `bash scripts/security/secure-docker-secrets.sh` sur le serveur |
| `docker: command not found` | Vérifiez que Docker est installé sur le serveur |
| `Container not starting` | Vérifiez les logs: `docker logs datalys-api` |

### Rollback (revenir en arrière)

```bash
ssh root@82.112.253.137

# Lister les backups
ls -lh /backup/deployments/

# Restaurer un backup
cd /root/datalys-backend
cp -r /backup/deployments/backup_20251012_120000/* .

# Redémarrer
docker restart datalys-api
```

---

## 📚 Documentation Complète

Pour plus de détails, consultez:
- **Configuration détaillée:** `docs/GITHUB_ACTIONS_SETUP.md`
- **Workflow GitHub:** `.github/workflows/deploy.yml`

---

## 💡 Conseils

### ✅ Bonnes Pratiques

- Testez localement avant de pusher
- Utilisez des messages de commit clairs
- Vérifiez les logs après chaque déploiement
- Gardez un backup avant les gros changements

### ❌ À Éviter

- Ne pushez pas de code non testé sur `main`
- Ne commitez jamais le fichier `.env`
- Ne désactivez pas les secrets GitHub
- Ne modifiez pas le workflow sans le tester

---

## 🎉 C'est Tout !

Vous avez maintenant un déploiement automatique professionnel. Chaque push sur `main` déploie automatiquement votre application en 2-3 minutes.

**Questions?** Consultez `docs/GITHUB_ACTIONS_SETUP.md`

