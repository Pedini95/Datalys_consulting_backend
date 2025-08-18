# 🚀 Scripts de Déploiement Datalys Consulting

## 📋 Scripts Disponibles

### 1. `deploy-simple.sh` 
**Déploiement rapide et simple**
```bash
./scripts/deploy-simple.sh
```
- ✅ Déploiement standard en production
- ✅ Vérification MySQL automatique
- ✅ Rebuild complet des containers
- ✅ **Préservation automatique des permissions d'upload**

### 2. `deploy-zero-downtime.sh`
**Déploiement sans interruption de service**
```bash
./scripts/deploy-zero-downtime.sh
```
- ✅ Rolling deployment
- ✅ Health checks automatiques
- ✅ Rollback en cas d'échec
- ✅ **Préservation automatique des permissions d'upload**

### 3. `configure-mysql.sh`
**Configuration MySQL sur IP publique**
```bash
./scripts/configure-mysql.sh
```
- ✅ Reconfigure MySQL pour écouter sur l'IP publique
- ✅ Détection automatique de l'état
- ✅ Script de récupération

### 4. `fix-permissions.sh`
**Correction manuelle des permissions d'upload**
```bash
./scripts/fix-permissions.sh
```
- ✅ Correction des permissions pour les fichiers uploadés
- ✅ Création des dossiers nécessaires
- ✅ Redémarrage complet des services

## 🎯 Usage Recommandé

**Déploiement normal :** `deploy-simple.sh`  
**Production critique :** `deploy-zero-downtime.sh`  
**Problème MySQL :** `configure-mysql.sh`  
**Problème permissions :** `fix-permissions.sh` (normalement pas nécessaire car intégré aux autres scripts)

## 🔐 Gestion Automatique des Permissions

Depuis la version récente, **tous les scripts de déploiement** préservent automatiquement les permissions des fichiers d'upload :
- Dossiers : `./src/static/files/logos`, `./src/static/files/files`, `./src/static/files/projects`
- Propriétaire : `1000:1000` (utilisateur app dans le container)
- Permissions : `775` (lecture/écriture/exécution)

**Plus besoin de s'inquiéter des permissions d'upload lors des déploiements automatiques !** 🎉

## 🛠️ CI/CD

Le déploiement automatique utilise GitHub Actions pour les pushs sur `develop`. 