#!/bin/bash

# ============================================================================
# Script de Configuration de Fail2ban
# Date: 2025-10-12
# Protection contre les attaques brute force (SSH, MySQL, API)
# Usage: ./scripts/security/setup-fail2ban.sh
# ============================================================================

set -e

echo "════════════════════════════════════════════════════════════"
echo "🛡️ CONFIGURATION DE FAIL2BAN"
echo "════════════════════════════════════════════════════════════"
echo ""

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Vérifier si on est root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}❌ Ce script doit être exécuté en tant que root${NC}"
    exit 1
fi

# Installer fail2ban
echo "📦 Installation de fail2ban..."
apt-get update > /dev/null 2>&1
if apt-get install -y fail2ban > /dev/null 2>&1; then
    echo -e "${GREEN}✅ fail2ban installé${NC}"
else
    echo -e "${RED}❌ Échec de l'installation${NC}"
    exit 1
fi
echo ""

# Configuration SSH
echo "🔐 Configuration de la protection SSH..."
cat > /etc/fail2ban/jail.d/sshd.conf << 'EOF'
[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
bantime = 3600
findtime = 600
EOF
echo -e "${GREEN}✅ Protection SSH configurée${NC}"
echo "   - Max tentatives: 3"
echo "   - Durée du ban: 1 heure"
echo "   - Fenêtre de détection: 10 minutes"
echo ""

# Configuration MySQL
echo "🗄️ Configuration de la protection MySQL..."
cat > /etc/fail2ban/filter.d/mysql-auth.conf << 'EOF'
[Definition]
failregex = ^%(__prefix_line)s.*Access denied for user .* \(using password: YES\)\s*$
            ^%(__prefix_line)s.*Access denied for user .* \(using password: NO\)\s*$
ignoreregex =
EOF

cat > /etc/fail2ban/jail.d/mysql.conf << 'EOF'
[mysql-auth]
enabled = true
filter = mysql-auth
logpath = /var/log/mysql/error.log
maxretry = 5
bantime = 3600
findtime = 600
EOF
echo -e "${GREEN}✅ Protection MySQL configurée${NC}"
echo "   - Max tentatives: 5"
echo "   - Durée du ban: 1 heure"
echo ""

# Configuration pour l'API (rate limiting)
echo "🌐 Configuration de la protection API..."
cat > /etc/fail2ban/filter.d/datalys-api.conf << 'EOF'
[Definition]
# Détecter trop de tentatives de login échouées
failregex = ^.*"POST /auth/login HTTP/1\.[01]" 401.*$
            ^.*"POST /auth/verify-mfa HTTP/1\.[01]" 401.*$
            ^.*Identifiant ou mot de passe incorrect.*from <HOST>.*$
ignoreregex =
EOF

cat > /etc/fail2ban/jail.d/datalys-api.conf << 'EOF'
[datalys-api]
enabled = true
filter = datalys-api
logpath = /var/log/nginx/access.log
          /root/datalys-backend/src/logs/*.log
maxretry = 10
bantime = 1800
findtime = 300
EOF
echo -e "${GREEN}✅ Protection API configurée${NC}"
echo "   - Max tentatives: 10"
echo "   - Durée du ban: 30 minutes"
echo ""

# Configurer les notifications par email (optionnel)
echo "📧 Configuration des notifications..."
read -p "Email pour les notifications (laisser vide pour skip): " ADMIN_EMAIL

if [ ! -z "$ADMIN_EMAIL" ]; then
    cat > /etc/fail2ban/jail.local << EOF
[DEFAULT]
destemail = $ADMIN_EMAIL
sendername = Fail2ban Datalys
action = %(action_mwl)s
EOF
    echo -e "${GREEN}✅ Notifications configurées pour: $ADMIN_EMAIL${NC}"
else
    echo -e "${YELLOW}⚠️  Notifications email désactivées${NC}"
fi
echo ""

# Démarrer fail2ban
echo "🚀 Démarrage de fail2ban..."
systemctl enable fail2ban > /dev/null 2>&1
systemctl restart fail2ban
sleep 2
echo -e "${GREEN}✅ fail2ban démarré${NC}"
echo ""

# Vérifier le statut
echo "📊 Statut de fail2ban:"
fail2ban-client status
echo ""

# Créer un script de monitoring
echo "📝 Création du script de monitoring..."
cat > /usr/local/bin/fail2ban-status.sh << 'EOFSTATUS'
#!/bin/bash

echo "════════════════════════════════════════════════════════════"
echo "🛡️ STATUT FAIL2BAN"
echo "════════════════════════════════════════════════════════════"
echo ""

# Services actifs
echo "📋 Services actifs:"
fail2ban-client status | grep "Jail list:" | sed 's/.*://g'
echo ""

# Détails par service
for jail in $(fail2ban-client status | grep "Jail list:" | sed 's/.*://g' | tr ',' ' '); do
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🔒 $jail"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    fail2ban-client status $jail
    echo ""
done

# IPs bannies
echo "🚫 IPs actuellement bannies:"
BANNED_IPS=$(fail2ban-client status | grep "Jail list:" | sed 's/.*://g' | tr ',' ' ' | while read jail; do
    fail2ban-client status $jail | grep "Banned IP list:" | sed 's/.*://g'
done | tr ' ' '\n' | sort -u | grep -v "^$")

if [ -z "$BANNED_IPS" ]; then
    echo "   Aucune IP bannie actuellement"
else
    echo "$BANNED_IPS"
fi
echo ""

# Statistiques récentes
echo "📈 Bannissements récents (dernières 24h):"
journalctl -u fail2ban --since "24 hours ago" | grep "Ban " | tail -10
echo ""
EOFSTATUS

chmod +x /usr/local/bin/fail2ban-status.sh
echo -e "${GREEN}✅ Script de monitoring créé: /usr/local/bin/fail2ban-status.sh${NC}"
echo ""

# Script pour débannir une IP
echo "📝 Création du script de débannissement..."
cat > /usr/local/bin/fail2ban-unban.sh << 'EOFUNBAN'
#!/bin/bash

if [ -z "$1" ]; then
    echo "Usage: $0 <IP_ADDRESS>"
    echo ""
    echo "IPs actuellement bannies:"
    /usr/local/bin/fail2ban-status.sh | grep -A 100 "IPs actuellement bannies"
    exit 1
fi

IP="$1"
echo "🔓 Débannissement de $IP..."

for jail in $(fail2ban-client status | grep "Jail list:" | sed 's/.*://g' | tr ',' ' '); do
    if fail2ban-client set $jail unbanip $IP 2>/dev/null; then
        echo "✅ IP $IP débannie de $jail"
    fi
done

echo "✅ Terminé"
EOFUNBAN

chmod +x /usr/local/bin/fail2ban-unban.sh
echo -e "${GREEN}✅ Script de débannissement créé: /usr/local/bin/fail2ban-unban.sh${NC}"
echo ""

# Résumé
echo "════════════════════════════════════════════════════════════"
echo "✅ FAIL2BAN CONFIGURÉ ET ACTIF"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "🛡️ Protections actives:"
echo "   • SSH (3 tentatives / 10min → ban 1h)"
echo "   • MySQL (5 tentatives / 10min → ban 1h)"
echo "   • API Datalys (10 tentatives / 5min → ban 30min)"
echo ""
echo "📋 Commandes utiles:"
echo "   • Statut global: fail2ban-client status"
echo "   • Statut détaillé: /usr/local/bin/fail2ban-status.sh"
echo "   • Débannir une IP: /usr/local/bin/fail2ban-unban.sh <IP>"
echo "   • Bannir manuellement: fail2ban-client set <jail> banip <IP>"
echo "   • Voir les logs: tail -f /var/log/fail2ban.log"
echo ""
echo "⚠️  IMPORTANT:"
echo "   • Testez depuis une IP différente pour éviter de vous bannir"
echo "   • Gardez une session SSH active pendant les tests"
echo "   • Notez l'IP de confiance pour la whitelist si nécessaire"
echo ""

