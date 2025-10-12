#!/bin/bash

# ============================================================================
# Script de Configuration des Sauvegardes Automatiques MySQL
# Date: 2025-10-12
# Usage: ./scripts/security/setup-backups.sh
# ============================================================================

set -e

echo "════════════════════════════════════════════════════════════"
echo "🔒 CONFIGURATION DES SAUVEGARDES AUTOMATIQUES"
echo "════════════════════════════════════════════════════════════"
echo ""

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Variables
BACKUP_DIR="/backup/mysql"
MYSQL_PASSWORD="Datalys@2025"
DB_NAME="datalys_consulting"
RETENTION_DAYS=7

# Créer le répertoire de backup
echo "📁 Création du répertoire de backup..."
mkdir -p $BACKUP_DIR
chmod 700 $BACKUP_DIR
echo -e "${GREEN}✅ Répertoire créé: $BACKUP_DIR${NC}"
echo ""

# Créer le script de backup
echo "📝 Création du script de backup..."
cat > /usr/local/bin/backup-mysql.sh << 'EOFBACKUP'
#!/bin/bash

# Configuration
BACKUP_DIR="/backup/mysql"
DATE=$(date +%Y%m%d_%H%M%S)
MYSQL_PASSWORD="Datalys@2025"
DB_NAME="datalys_consulting"
RETENTION_DAYS=7
LOG_FILE="/var/log/mysql-backup.log"

# Fonction de log
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a $LOG_FILE
}

log "🔄 Début de la sauvegarde MySQL"

# Créer le backup
BACKUP_FILE="$BACKUP_DIR/datalys_${DATE}.sql.gz"

if mysqldump -u root -p"$MYSQL_PASSWORD" "$DB_NAME" | gzip > "$BACKUP_FILE"; then
    BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    log "✅ Backup créé: $BACKUP_FILE (Taille: $BACKUP_SIZE)"
    
    # Vérifier l'intégrité
    if gunzip -t "$BACKUP_FILE" 2>/dev/null; then
        log "✅ Intégrité du backup vérifiée"
    else
        log "❌ ERREUR: Backup corrompu!"
        exit 1
    fi
else
    log "❌ ERREUR: Échec de la création du backup"
    exit 1
fi

# Nettoyer les anciens backups
log "🧹 Nettoyage des backups de plus de $RETENTION_DAYS jours..."
DELETED=$(find $BACKUP_DIR -name "datalys_*.sql.gz" -mtime +$RETENTION_DAYS -delete -print | wc -l)
if [ "$DELETED" -gt 0 ]; then
    log "✅ $DELETED ancien(s) backup(s) supprimé(s)"
else
    log "ℹ️  Aucun ancien backup à supprimer"
fi

# Statistiques
TOTAL_BACKUPS=$(ls -1 $BACKUP_DIR/datalys_*.sql.gz 2>/dev/null | wc -l)
TOTAL_SIZE=$(du -sh $BACKUP_DIR | cut -f1)
log "📊 Total: $TOTAL_BACKUPS backups - Espace utilisé: $TOTAL_SIZE"

log "✅ Sauvegarde terminée avec succès"
echo ""
EOFBACKUP

chmod +x /usr/local/bin/backup-mysql.sh
echo -e "${GREEN}✅ Script de backup créé: /usr/local/bin/backup-mysql.sh${NC}"
echo ""

# Tester le script
echo "🧪 Test du script de backup..."
if /usr/local/bin/backup-mysql.sh; then
    echo -e "${GREEN}✅ Test réussi !${NC}"
else
    echo -e "${RED}❌ Échec du test${NC}"
    exit 1
fi
echo ""

# Configurer le cron
echo "⏰ Configuration du cron (sauvegarde quotidienne à 3h00)..."
CRON_JOB="0 3 * * * /usr/local/bin/backup-mysql.sh > /dev/null 2>&1"

# Vérifier si le cron existe déjà
if crontab -l 2>/dev/null | grep -q "backup-mysql.sh"; then
    echo -e "${YELLOW}⚠️  Cron déjà configuré${NC}"
else
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
    echo -e "${GREEN}✅ Cron configuré${NC}"
fi
echo ""

# Créer un script de restauration
echo "📝 Création du script de restauration..."
cat > /usr/local/bin/restore-mysql.sh << 'EOFRESTORE'
#!/bin/bash

# Script de restauration MySQL
# Usage: ./restore-mysql.sh <fichier_backup.sql.gz>

if [ -z "$1" ]; then
    echo "Usage: $0 <fichier_backup.sql.gz>"
    echo ""
    echo "Backups disponibles:"
    ls -lh /backup/mysql/datalys_*.sql.gz 2>/dev/null | tail -10
    exit 1
fi

BACKUP_FILE="$1"
MYSQL_PASSWORD="Datalys@2025"
DB_NAME="datalys_consulting"

if [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ Fichier non trouvé: $BACKUP_FILE"
    exit 1
fi

echo "⚠️  ATTENTION: Cette opération va ÉCRASER la base de données actuelle!"
echo "Backup à restaurer: $BACKUP_FILE"
read -p "Continuer? (tapez 'OUI' en majuscules): " CONFIRM

if [ "$CONFIRM" != "OUI" ]; then
    echo "Restauration annulée"
    exit 0
fi

echo "🔄 Restauration en cours..."

# Décompresser et restaurer
if gunzip < "$BACKUP_FILE" | mysql -u root -p"$MYSQL_PASSWORD" "$DB_NAME"; then
    echo "✅ Restauration terminée avec succès"
else
    echo "❌ Échec de la restauration"
    exit 1
fi
EOFRESTORE

chmod +x /usr/local/bin/restore-mysql.sh
echo -e "${GREEN}✅ Script de restauration créé: /usr/local/bin/restore-mysql.sh${NC}"
echo ""

# Résumé
echo "════════════════════════════════════════════════════════════"
echo "✅ CONFIGURATION TERMINÉE"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "📁 Répertoire de backup: $BACKUP_DIR"
echo "⏰ Sauvegarde automatique: Tous les jours à 3h00"
echo "🗄️  Rétention: $RETENTION_DAYS jours"
echo ""
echo "📋 Commandes utiles:"
echo "  • Backup manuel: /usr/local/bin/backup-mysql.sh"
echo "  • Restaurer: /usr/local/bin/restore-mysql.sh <fichier>"
echo "  • Voir les logs: tail -f /var/log/mysql-backup.log"
echo "  • Lister backups: ls -lh $BACKUP_DIR/"
echo ""
echo "⚠️  IMPORTANT:"
echo "  • Testez régulièrement la restauration"
echo "  • Copiez les backups vers un stockage externe"
echo "  • Surveillez l'espace disque"
echo ""

