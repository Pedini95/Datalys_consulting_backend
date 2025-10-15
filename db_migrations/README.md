# Migrations de Base de Données

Ce dossier contient les scripts SQL pour les migrations de base de données.

## Comment exécuter une migration sur le serveur

### Étape 1: Copier le fichier de migration sur le serveur

```bash
scp db_migrations/001_add_partner_phone_columns.sql root@srv622104:/tmp/
```

### Étape 2: Se connecter au serveur

```bash
ssh root@srv622104
```

### Étape 3: Exécuter la migration

Remplacez `votre_base_de_donnees`, `votre_utilisateur` et `votre_mot_de_passe` par vos valeurs réelles :

```bash
mysql -u votre_utilisateur -p votre_base_de_donnees < /tmp/001_add_partner_phone_columns.sql
```

Ou en mode interactif :

```bash
mysql -u votre_utilisateur -p
```

Puis dans le shell MySQL :

```sql
USE votre_base_de_donnees;
SOURCE /tmp/001_add_partner_phone_columns.sql;
```

### Étape 4: Vérifier que la migration a réussi

```sql
DESCRIBE partners;
```

Vous devriez voir les colonnes `phone` et `country_code` dans la liste.

### Étape 5: Redémarrer l'application Flask

```bash
supervisorctl restart datalys_consulting
```

## Liste des migrations

| Fichier | Date | Description | Statut |
|---------|------|-------------|--------|
| 001_add_partner_phone_columns.sql | 2025-10-15 | Ajout des colonnes phone et country_code à la table partners | ✅ Appliquée |
| 002_add_remaining_partner_columns.sql | 2025-10-15 | Ajout des colonnes address, logo_url, is_deleted, created_at, created_by, updated_at, updated_by à la table partners | ✅ Appliquée |
| 003_add_incident_refusal_columns.sql | 2025-10-15 | Ajout des colonnes refusal_count, refusal_reason, last_refusal_at à la table incidents | ✅ Appliquée |

## Notes importantes

- Les scripts de migration sont idempotents (peuvent être exécutés plusieurs fois sans erreur)
- Toujours faire une sauvegarde de la base de données avant d'exécuter une migration
- Tester la migration dans un environnement de développement avant la production
