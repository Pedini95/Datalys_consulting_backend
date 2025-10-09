# 🚀 Guide de Test des APIs - Datalys Consulting

**Version** : 2.0.0  
**Date** : 9 Octobre 2025

---

## 📋 Fichiers Disponibles

| Fichier | Description | Taille |
|---------|-------------|--------|
| `DOCUMENTATION_API_COMPLETE.md` | **📘 Documentation complète** avec tous les endpoints, exemples cURL, codes d'erreur | 31 KB |
| `API_ROUTES_SUMMARY.md` | **📝 Résumé rapide** des routes principales | 7.2 KB |
| `Datalys_Consulting_API_Collection_Complete.json` | **📦 Collection Postman** avec tous les endpoints | 22 KB |
| `Datalys_Environment_Production.json` | **⚙️ Environnement Postman** avec variables pré-configurées | 1.2 KB |
| `test_all_endpoints.sh` | **🧪 Script de test** automatique de tous les endpoints | 9.8 KB |
| `docs/GUIDE_TEST_API.md` | **📖 Guide détaillé** avec scénarios de test | 12 KB |

---

## 🎯 Démarrage Rapide (3 minutes)

### Option 1 : Postman (Recommandé) 👍

1. **Télécharger Postman** : https://www.postman.com/downloads/

2. **Importer la collection** :
   ```
   Postman → Import → Sélectionner "Datalys_Consulting_API_Collection_Complete.json"
   ```

3. **Importer l'environnement** :
   ```
   Postman → Import → Sélectionner "Datalys_Environment_Production.json"
   ```

4. **Sélectionner l'environnement** :
   ```
   En haut à droite → Sélectionner "Datalys Consulting - Production"
   ```

5. **Tester** :
   ```
   🔐 Authentication → Login avec Email → Send
   ```
   Le token sera automatiquement enregistré ! ✅

---

### Option 2 : cURL (Ligne de commande) 💻

```bash
# 1. Tester le Health Check
curl http://82.112.253.137:8082/health | jq '.'

# 2. Login
TOKEN=$(curl -s -X POST http://82.112.253.137:8082/auth/login \
  -H "Content-Type: application/json" \
  -d '{"identifier": "nonssekone@gmail.com", "password": "Password123"}' \
  | jq -r '.data.token')

echo "Token: $TOKEN"

# 3. Tester les métadonnées P0-P4
curl -H "Authorization: Bearer $TOKEN" \
  http://82.112.253.137:8082/incidents/metadata | jq '.data.priorities'
```

---

### Option 3 : Script Automatique 🤖

```bash
# Exécuter le script de test complet
chmod +x test_all_endpoints.sh
./test_all_endpoints.sh
```

**Résultat** : Teste automatiquement 10 endpoints en 30 secondes ! ⚡

---

## 📚 Documentation

### 1. Documentation Complète (Lire en premier !)

**Fichier** : `DOCUMENTATION_API_COMPLETE.md`

**Contenu** :
- ✅ Tous les endpoints avec description détaillée
- ✅ Exemples cURL prêts à copier-coller
- ✅ Codes d'erreur et leur signification
- ✅ Scénarios complets (créer partenaire + incident)
- ✅ Nouvelles fonctionnalités (P0-P4, Code Client, MFA)

**Ouvrir** :
```bash
# macOS
open DOCUMENTATION_API_COMPLETE.md

# Linux
xdg-open DOCUMENTATION_API_COMPLETE.md

# Ou dans votre éditeur
code DOCUMENTATION_API_COMPLETE.md
```

---

### 2. Résumé Rapide

**Fichier** : `API_ROUTES_SUMMARY.md`

**Contenu** :
- ✅ Liste de toutes les routes
- ✅ Exemples cURL concis
- ✅ Utilisateurs de test

**Idéal pour** : Référence rapide pendant le développement

---

## 🧪 Tests Automatiques

### Exécuter les Tests

```bash
./test_all_endpoints.sh
```

**Ce qui est testé** :
1. ✅ Health Check (API opérationnelle)
2. ✅ Login Admin
3. ✅ Métadonnées P0-P4
4. ✅ Liste des rôles
5. ✅ Liste des utilisateurs
6. ✅ Création d'un partenaire (avec code client)
7. ✅ Login avec code client
8. ✅ Liste des partenaires
9. ✅ Liste des projets
10. ✅ Liste des incidents

**Durée** : ~30 secondes ⚡

---

## 🔑 Utilisateurs de Test

| Nom | Email | Code Client | Mot de Passe | Rôle | MFA |
|-----|-------|-------------|--------------|------|-----|
| **Pedini Nonsse** | nonssekone@gmail.com | null | Password123 | Admin | ❌ Désactivé |
| Administrateur | admin@datalys.com | null | Admin@123 | Admin | ✅ Activé |
| Marie Martin | marie.martin@datalys.com | DATALYS-2025-003 | Test@123 | User | ✅ Activé |

**Recommandation** : Utiliser **Pedini Nonsse** pour les tests (MFA désactivé).

---

## 🆕 Nouvelles Fonctionnalités

### 1. Code Client Unique ✅

**Format** : `DATALYS-YYYY-NNN` (ex: `DATALYS-2025-003`)

**Pour qui** : Uniquement les partenaires (rôle "User")

**Avantage** : Login possible avec email OU code client

**Test** :
```bash
# Login avec email
curl -X POST http://82.112.253.137:8082/auth/login \
  -H "Content-Type: application/json" \
  -d '{"identifier": "marie.martin@datalys.com", "password": "Test@123"}'

# Login avec code client
curl -X POST http://82.112.253.137:8082/auth/login \
  -H "Content-Type: application/json" \
  -d '{"identifier": "DATALYS-2025-003", "password": "Test@123"}'
```

---

### 2. Système P0-P4 ✅

| Priorité | Label | Couleur |
|----------|-------|---------|
| P0 | Arrêt de service (immédiat) | 🔴 |
| P1 | Forte dégradation de service | 🟠 |
| P2 | Dégradation de service | 🟡 |
| P3 | Incident ordinaire | 🔵 |
| P4 | Incident mineur | 🟢 |

**Test** :
```bash
TOKEN="votre_token"
curl -H "Authorization: Bearer $TOKEN" \
  http://82.112.253.137:8082/incidents/metadata | jq '.data.priorities'
```

---

### 3. Numéro d'Incident Auto-généré ✅

**Format** : `INC-YYYY-NNNNN` (ex: `INC-2025-00001`)

**Automatique** : Généré à la création

**Test** :
```bash
TOKEN="votre_token"
curl -X POST http://82.112.253.137:8082/incidents/create \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Incident",
    "description": "Description",
    "type": "incident",
    "priority": "P3",
    "category": "Test",
    "project_id": 1
  }' | jq '.data.incident_number'
```

---

### 4. MFA par Email ✅

**Fonctionnement** :
1. Login → Code à 6 chiffres envoyé par email
2. Email envoyé en **~1.7 secondes** (asynchrone)
3. Code valide pendant **5 minutes**
4. **3 tentatives** maximum

**Test** :
```bash
# 1. Login (déclenche l'envoi du code MFA)
curl -X POST http://82.112.253.137:8082/auth/login \
  -H "Content-Type: application/json" \
  -d '{"identifier": "admin@datalys.com", "password": "Admin@123"}'

# 2. Vérifier le code (remplacer 123456 par le code reçu)
curl -X POST http://82.112.253.137:8082/auth/verify-mfa \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "mfa_code": "123456"}'
```

**Désactiver le MFA** (pour tests) :
```sql
UPDATE users SET mfa_enabled = 0 WHERE email = 'votre.email@example.com';
```

---

### 5. Notifications Automatiques ✅

**Lors de la création d'un incident** :
- ✅ Email envoyé à tous les **Admin** et **Manager**
- ✅ Email envoyé au **partenaire** du projet
- ✅ Notification push (si FCM configuré)
- ✅ Envoi **asynchrone** (non-bloquant)

---

## 🎓 Exemples de Scénarios

### Scénario 1 : Créer un Partenaire et un Incident P0

```bash
# 1. Login
TOKEN=$(curl -s -X POST http://82.112.253.137:8082/auth/login \
  -H "Content-Type: application/json" \
  -d '{"identifier": "nonssekone@gmail.com", "password": "Password123"}' \
  | jq -r '.data.token')

# 2. Créer un utilisateur partenaire
USER_RESPONSE=$(curl -s -X POST http://82.112.253.137:8082/users/create \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Partenaire",
    "email": "test@example.com",
    "password": "Test@123",
    "role_name": "User",
    "is_active": true,
    "is_temp_password": false
  }')

CLIENT_CODE=$(echo $USER_RESPONSE | jq -r '.data.client_code')
echo "Code Client: $CLIENT_CODE"

# 3. Login avec le code client
curl -X POST http://82.112.253.137:8082/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"identifier\": \"$CLIENT_CODE\", \"password\": \"Test@123\"}"
```

**Voir plus d'exemples** : `DOCUMENTATION_API_COMPLETE.md` → Section "Exemples Complets"

---

## 🔧 Configuration

### Base URL
```
http://82.112.253.137:8082
```

### Authentification
```
Authorization: Bearer <votre_token_jwt>
```

### Rate Limiting
- **5 tentatives** de login par 15 minutes
- Ensuite : blocage temporaire

### Upload
- **Limite** : 50 MB par fichier

### Token JWT
- **Validité** : 2 heures
- **Renouvellement** : Re-login après expiration

---

## 📞 Support

### Problèmes Courants

**1. "Token invalide" ou "401 Unauthorized"**
```bash
# Solution : Re-login pour obtenir un nouveau token
TOKEN=$(curl -s -X POST http://82.112.253.137:8082/auth/login \
  -H "Content-Type: application/json" \
  -d '{"identifier": "nonssekone@gmail.com", "password": "Password123"}' \
  | jq -r '.data.token')
```

**2. "Email manquant" lors du login**
```bash
# ❌ Ancien format
{"email": "...", "password": "..."}

# ✅ Nouveau format
{"identifier": "...", "password": "..."}
```

**3. MFA trop lent**
- ✅ **Déjà corrigé** ! L'envoi est maintenant asynchrone (~100ms de réponse)

**4. Email MFA non reçu**
- ✅ Vérifier les **SPAMS**
- Vérifier les logs : `docker logs datalys-api | grep Email`

---

## 🎯 Checklist de Test

### Authentification
- [ ] Login avec email (Admin)
- [ ] Login avec email (Partenaire)
- [ ] Login avec code client (Partenaire)
- [ ] MFA : Réception email
- [ ] MFA : Vérification code
- [ ] Logout

### Utilisateurs
- [ ] Liste des utilisateurs
- [ ] Créer Admin (sans code client)
- [ ] Créer Partenaire (avec code client)
- [ ] Modifier utilisateur
- [ ] Supprimer utilisateur

### Incidents
- [ ] Métadonnées (P0-P4)
- [ ] Liste des incidents
- [ ] Créer incident P0
- [ ] Vérifier numéro auto-généré
- [ ] Vérifier email aux experts
- [ ] Modifier incident
- [ ] Résoudre incident

### Autres
- [ ] Liste des projets
- [ ] Liste des partenaires
- [ ] Dashboard
- [ ] Health check

---

## 🚀 Prochaines Étapes

1. **Lire** : `DOCUMENTATION_API_COMPLETE.md`
2. **Importer** : Collection et environnement Postman
3. **Tester** : Exécuter `./test_all_endpoints.sh`
4. **Développer** : Intégrer les APIs dans votre frontend

---

## 📊 Statistiques

- **Total endpoints** : 30+
- **Documentation** : 1698 lignes
- **Collection Postman** : 22 KB
- **Tests automatiques** : 10 endpoints en 30s

---

**Bon développement ! 🎉**

---

**Dernière mise à jour** : 9 Octobre 2025  
**Version** : 2.0.0  
**Auteur** : Équipe Datalys Consulting

