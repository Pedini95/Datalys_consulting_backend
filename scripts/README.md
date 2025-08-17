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

### 2. `deploy-zero-downtime.sh`
**Déploiement sans interruption de service**
```bash
./scripts/deploy-zero-downtime.sh
```
- ✅ Rolling deployment
- ✅ Health checks automatiques
- ✅ Rollback en cas d'échec

### 3. `configure-mysql.sh`
**Configuration MySQL sur IP publique**
```bash
./scripts/configure-mysql.sh
```
- ✅ Reconfigure MySQL pour écouter sur l'IP publique
- ✅ Détection automatique de l'état
- ✅ Script de récupération

## 🎯 Usage Recommandé

**Déploiement normal :** `deploy-simple.sh`  
**Production critique :** `deploy-zero-downtime.sh`  
**Problème MySQL :** `configure-mysql.sh`

## 🛠️ CI/CD

Le déploiement automatique utilise GitHub Actions pour les pushs sur `develop`. 