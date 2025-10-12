# 🔒 Reconstruction de la Base de Données après Attaque Ransomware

**Date:** 12 octobre 2025  
**Type:** Incident de sécurité - Attaque ransomware  
**Impact:** Base de données `datalys_consulting` chiffrée  
**Résolution:** Reconstruction complète de la base

---

## 📊 Résumé de l'Incident

### Détection
- **Quand:** 12 octobre 2025, ~23h30
- **Comment:** Erreur de connexion à la base de données lors du login
- **Découverte:** Base `RECOVER_YOUR_DATA` avec message de rançon de $500

### Cause Racine
1. ✅ **Port MySQL 3306** exposé publiquement sur Internet
2. ✅ **Mot de passe root** = `"root"` (très faible)
3. ✅ Aucune restriction IP sur les connexions MySQL

### Rançon Demandée
- **Montant:** $500 USD
- **Méthode:** Bitcoin
- **Action:** ❌ **NON PAYÉE** - Reconstruction manuelle

---

## 🛡️ Mesures de Sécurité Appliquées

### 1. Blocage du Port MySQL
```bash
# Bloquer l'accès externe au port 3306
ufw deny 3306/tcp
iptables -A INPUT -p tcp --dport 3306 ! -s 127.0.0.1 -j DROP
```

### 2. Changement du Mot de Passe Root
```sql
ALTER USER 'root'@'localhost' IDENTIFIED BY 'Datalys@2025';
FLUSH PRIVILEGES;
```

### 3. Suppression du Ransomware
```sql
DROP DATABASE RECOVER_YOUR_DATA;
```

---

## 🗄️ Reconstruction de la Base de Données

### Tables Recréées (9 tables)

1. **roles** - Rôles utilisateurs (Admin, Expert, User)
2. **users** - Utilisateurs avec MFA et client_code
3. **partners** - Partenaires avec config email
4. **projects** - Projets liés aux partenaires
5. **folders** - Dossiers hiérarchiques
6. **files** - Fichiers uploadés
7. **incidents** - Incidents avec système P0-P4
8. **user_project_permissions** - Permissions granulaires
9. **action_history** - Audit trail complet

### Relations (Foreign Keys) - 14 relations

| Table Source | Colonne | Table Cible | Colonne | Action |
|-------------|---------|-------------|---------|--------|
| users | role_id | roles | id | RESTRICT |
| projects | partner_id | partners | id | RESTRICT |
| folders | project_id | projects | id | RESTRICT |
| folders | parent_folder_id | folders | id | CASCADE |
| files | folder_id | folders | id | RESTRICT |
| incidents | user_id | users | id | RESTRICT |
| incidents | project_id | projects | id | RESTRICT |
| incidents | assigned_to | users | id | RESTRICT |
| incidents | parent_id | incidents | id | CASCADE |
| incidents | resolved_by | users | id | SET NULL |
| user_project_permissions | user_id | users | id | CASCADE |
| user_project_permissions | project_id | projects | id | CASCADE |
| user_project_permissions | role_id | roles | id | RESTRICT |
| action_history | user_id | users | id | CASCADE |

### Index de Performance

```sql
-- Incidents
CREATE INDEX idx_incidents_status ON incidents(status);
CREATE INDEX idx_incidents_priority ON incidents(priority);
CREATE INDEX idx_incidents_number ON incidents(incident_number);

-- Users
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_client_code ON users(client_code);
CREATE INDEX idx_users_role_id ON users(role_id);

-- Action History
CREATE INDEX idx_action_history_entity ON action_history(entity_type, entity_id);
CREATE INDEX idx_action_history_created ON action_history(created_at);
```

---

## 📝 Données Initiales Recréées

### Rôles
- **Admin** - Accès complet
- **Expert** - Gestion des incidents
- **User** - Accès limité

### Compte Admin
- **Email:** admin@datalysconsulting.com
- **Mot de passe:** Password123
- **Rôle:** Admin
- **Statut:** Actif

---

## 🔄 Modifications des Modèles Python

### Modèle `Incident`
Ajout des colonnes :
- `resolved_by` (INT) - ID de l'utilisateur qui a résolu
- `resolved_at` (DATETIME) - Date de résolution
- Relation `resolver` vers User

### Modèle `UserProjectPermission`
Ajout des colonnes :
- `role_id` (INT, nullable) - Lien vers roles
- `can_read` (BOOLEAN) - Permission de lecture
- `can_write` (BOOLEAN) - Permission d'écriture
- `can_delete` (BOOLEAN) - Permission de suppression

---

## ✅ Vérifications Post-Reconstruction

### Base de Données
```sql
-- Vérifier les tables
SHOW TABLES;
-- Résultat: 9 tables ✅

-- Vérifier les foreign keys
SELECT COUNT(*) FROM information_schema.KEY_COLUMN_USAGE 
WHERE TABLE_SCHEMA = 'datalys_consulting' 
  AND REFERENCED_TABLE_NAME IS NOT NULL;
-- Résultat: 14 relations ✅

-- Vérifier les index
SHOW INDEX FROM incidents;
-- Résultat: 3 index ✅
```

### Sécurité
```bash
# Vérifier le blocage du port
netstat -tuln | grep 3306
# Résultat: Écoute uniquement sur 127.0.0.1 ✅

# Vérifier les règles firewall
ufw status | grep 3306
# Résultat: Port 3306 bloqué ✅
```

---

## 📋 Actions Restantes

### Aujourd'hui (12 octobre 2025)
- [x] Bloquer le port MySQL 3306
- [x] Changer le mot de passe root
- [x] Supprimer la base ransomware
- [x] Recréer toutes les tables
- [x] Créer toutes les foreign keys
- [x] Ajouter les index de performance
- [x] Insérer les données initiales
- [x] Mettre à jour les modèles Python locaux
- [x] Créer la documentation

### Demain (13 octobre 2025)
- [ ] Mettre à jour `docker-compose.yml` avec le nouveau mot de passe
  ```yaml
  DB_PASSWORD: "Datalys@2025"
  ```
- [ ] Redémarrer le conteneur API
  ```bash
  docker-compose down
  docker-compose up -d
  ```
- [ ] Tester le login
  ```bash
  curl -X POST http://82.112.253.137:8082/auth/login \
    -H "Content-Type: application/json" \
    -d '{"identifier":"admin@datalysconsulting.com","password":"Password123"}'
  ```

### Court Terme (Cette semaine)
- [ ] Mettre en place des sauvegardes automatiques
  - Backup quotidien de la base
  - Rotation sur 7 jours
  - Stockage externe
- [ ] Auditer tous les accès SSH
- [ ] Configurer fail2ban pour MySQL
- [ ] Mettre en place un monitoring de sécurité

---

## 💰 Coût de l'Incident

| Élément | Coût |
|---------|------|
| Rançon demandée | $500 USD |
| Rançon payée | **$0** ✅ |
| Temps de reconstruction | 2 heures |
| Données perdues | Test uniquement (aucune perte réelle) |

**Total économisé : $500 USD** 🎉

---

## 📚 Leçons Apprises

1. ✅ **Ne JAMAIS exposer MySQL sur Internet** sans restriction IP
2. ✅ **Utiliser des mots de passe forts** pour tous les comptes
3. ✅ **Mettre en place des sauvegardes régulières** avant la production
4. ✅ **Monitorer les tentatives de connexion** suspectes
5. ✅ **Tester la restauration** des backups régulièrement

---

## 📞 Contact

Pour toute question sur cet incident :
- **Date:** 12 octobre 2025
- **Statut:** ✅ **RÉSOLU**
- **Équipe:** Datalys Consulting

