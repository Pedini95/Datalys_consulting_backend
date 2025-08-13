#!/bin/bash

# Script d'installation Kubernetes sur VPS existant
# Usage: ./install-k8s-existing-vps.sh

set -e

# Configuration
BACKUP_DIR="/opt/backups"
CURRENT_APP_DIR="/home/datalys/Datalys_consulting_backend"
K8S_BACKUP_DIR="/opt/k8s-backup"

# Couleurs pour les logs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction de logging
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Vérification des prérequis
check_prerequisites() {
    log "Vérification des prérequis..."
    
    # Vérifier que c'est Ubuntu
    if [[ ! -f /etc/os-release ]] || ! grep -q "Ubuntu" /etc/os-release; then
        error "Ce script nécessite Ubuntu 20.04+"
    fi
    
    # Vérifier les privilèges root
    if [[ $EUID -ne 0 ]]; then
        error "Ce script doit être exécuté en tant que root"
    fi
    
    # Vérifier la mémoire (minimum 4GB)
    MEMORY_KB=$(grep MemTotal /proc/meminfo | awk '{print $2}')
    MEMORY_GB=$((MEMORY_KB / 1024 / 1024))
    
    if [[ $MEMORY_GB -lt 4 ]]; then
        error "Minimum 4GB de RAM requis. Disponible: ${MEMORY_GB}GB"
    fi
    
    # Vérifier l'espace disque (minimum 20GB)
    DISK_GB=$(df / | tail -1 | awk '{print $4}')
    DISK_GB=$((DISK_GB / 1024 / 1024))
    
    if [[ $DISK_GB -lt 20 ]]; then
        error "Minimum 20GB d'espace disque requis. Disponible: ${DISK_GB}GB"
    fi
    
    success "Prérequis vérifiés (RAM: ${MEMORY_GB}GB, Disque: ${DISK_GB}GB)"
}

# Sauvegarde de l'application actuelle
backup_current_application() {
    log "Sauvegarde de l'application actuelle..."
    
    # Créer le répertoire de backup
    mkdir -p "$K8S_BACKUP_DIR"
    
    # Sauvegarder l'application
    if [ -d "$CURRENT_APP_DIR" ]; then
        cp -r "$CURRENT_APP_DIR" "$K8S_BACKUP_DIR/app_backup_$(date +%Y%m%d_%H%M%S)"
        success "Application sauvegardée"
    else
        warning "Répertoire de l'application non trouvé: $CURRENT_APP_DIR"
    fi
    
    # Sauvegarder les configurations PM2
    if command -v pm2 &> /dev/null; then
        pm2 save
        cp ~/.pm2/dump.pm2 "$K8S_BACKUP_DIR/pm2_backup_$(date +%Y%m%d_%H%M%S).json"
        success "Configuration PM2 sauvegardée"
    fi
    
    # Sauvegarder les configurations Nginx
    if [ -f "/etc/nginx/sites-available/default" ]; then
        cp /etc/nginx/sites-available/default "$K8S_BACKUP_DIR/nginx_backup_$(date +%Y%m%d_%H%M%S)"
        success "Configuration Nginx sauvegardée"
    fi
    
    # Sauvegarder les fichiers de configuration
    if [ -f "$CURRENT_APP_DIR/src/.env.local" ]; then
        cp "$CURRENT_APP_DIR/src/.env.local" "$K8S_BACKUP_DIR/env_backup_$(date +%Y%m%d_%H%M%S)"
        success "Variables d'environnement sauvegardées"
    fi
}

# Arrêt propre de l'application actuelle
stop_current_application() {
    log "Arrêt propre de l'application actuelle..."
    
    # Arrêter PM2
    if command -v pm2 &> /dev/null; then
        pm2 stop all || warning "Impossible d'arrêter PM2"
        pm2 delete all || warning "Impossible de supprimer les processus PM2"
    fi
    
    # Arrêter Nginx
    if systemctl is-active --quiet nginx; then
        systemctl stop nginx
        success "Nginx arrêté"
    fi
    
    # Arrêter les autres services si nécessaire
    if systemctl is-active --quiet mysql; then
        systemctl stop mysql
        success "MySQL arrêté"
    fi
    
    if systemctl is-active --quiet redis; then
        systemctl stop redis
        success "Redis arrêté"
    fi
}

# Installation de Docker
install_docker() {
    log "Installation de Docker..."
    
    # Supprimer les anciennes versions
    apt remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true
    
    # Ajouter le repository Docker
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Installer Docker
    apt update
    apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    
    # Démarrer et activer Docker
    systemctl start docker
    systemctl enable docker
    
    # Vérifier l'installation
    if docker --version; then
        success "Docker installé avec succès"
    else
        error "Échec de l'installation de Docker"
    fi
}

# Installation de k3s (Kubernetes léger)
install_k3s() {
    log "Installation de k3s (Kubernetes léger)..."
    
    # Installer k3s avec configuration pour VPS existant
    curl -sfL https://get.k3s.io | INSTALL_K3S_EXEC="--disable traefik --disable servicelb" sh -
    
    # Attendre que k3s démarre
    sleep 15
    
    # Vérifier le statut
    if systemctl is-active --quiet k3s; then
        success "k3s installé et démarré"
    else
        error "Échec du démarrage de k3s"
    fi
    
    # Configurer kubectl
    mkdir -p $HOME/.kube
    cp /etc/rancher/k3s/k3s.yaml $HOME/.kube/config
    chmod 600 $HOME/.kube/config
    
    # Vérifier l'installation
    if kubectl get nodes; then
        success "Kubernetes configuré avec succès"
    else
        error "Échec de la configuration de Kubernetes"
    fi
}

# Installation de Helm
install_helm() {
    log "Installation de Helm..."
    
    # Installer Helm
    curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
    
    # Vérifier l'installation
    if helm version; then
        success "Helm installé avec succès"
    else
        error "Échec de l'installation de Helm"
    fi
}

# Installation de Nginx Ingress Controller
install_nginx_ingress() {
    log "Installation de Nginx Ingress Controller..."
    
    # Ajouter le repository Helm
    helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
    helm repo update
    
    # Installer Nginx Ingress avec configuration pour VPS existant
    helm install nginx-ingress ingress-nginx/ingress-nginx \
        --namespace ingress-nginx \
        --create-namespace \
        --set controller.service.type=NodePort \
        --set controller.service.nodePorts.http=30080 \
        --set controller.service.nodePorts.https=30443 \
        --set controller.resources.requests.cpu=100m \
        --set controller.resources.requests.memory=128Mi \
        --set controller.resources.limits.cpu=200m \
        --set controller.resources.limits.memory=256Mi
    
    # Attendre que l'ingress soit prêt
    log "Attente que Nginx Ingress soit prêt..."
    kubectl wait --namespace ingress-nginx \
        --for=condition=ready pod \
        --selector=app.kubernetes.io/component=controller \
        --timeout=300s
    
    success "Nginx Ingress installé"
}

# Installation de Cert-Manager
install_cert_manager() {
    log "Installation de Cert-Manager..."
    
    # Ajouter le repository cert-manager
    helm repo add jetstack https://charts.jetstack.io
    helm repo update
    
    # Installer cert-manager
    helm install cert-manager jetstack/cert-manager \
        --namespace cert-manager \
        --create-namespace \
        --version v1.13.0 \
        --set installCRDs=true \
        --set resources.requests.cpu=100m \
        --set resources.requests.memory=128Mi \
        --set resources.limits.cpu=200m \
        --set resources.limits.memory=256Mi
    
    # Attendre que cert-manager soit prêt
    log "Attente que Cert-Manager soit prêt..."
    kubectl wait --namespace cert-manager \
        --for=condition=ready pod \
        --selector=app.kubernetes.io/instance=cert-manager \
        --timeout=300s
    
    # Créer le ClusterIssuer pour Let's Encrypt
    log "Configuration du ClusterIssuer Let's Encrypt..."
    cat << EOF | kubectl apply -f -
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: votre-email@datalysconsulting.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF
    
    success "Cert-Manager installé et configuré"
}

# Configuration des namespaces
setup_namespaces() {
    log "Configuration des namespaces..."
    
    # Créer le namespace pour l'application
    kubectl create namespace datalys --dry-run=client -o yaml | kubectl apply -f -
    
    success "Namespaces configurés"
}

# Configuration de Nginx pour rediriger vers Kubernetes
configure_nginx_proxy() {
    log "Configuration de Nginx pour rediriger vers Kubernetes..."
    
    # Créer la configuration Nginx pour rediriger vers Kubernetes
    cat > /etc/nginx/sites-available/kubernetes-proxy << 'EOF'
server {
    listen 80;
    server_name api.datalysconsulting.com;
    
    location / {
        proxy_pass http://127.0.0.1:30080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

server {
    listen 443 ssl;
    server_name api.datalysconsulting.com;
    
    ssl_certificate /etc/letsencrypt/live/api.datalysconsulting.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.datalysconsulting.com/privkey.pem;
    
    location / {
        proxy_pass http://127.0.0.1:30080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF
    
    # Activer la configuration
    ln -sf /etc/nginx/sites-available/kubernetes-proxy /etc/nginx/sites-enabled/
    
    # Tester la configuration
    if nginx -t; then
        systemctl start nginx
        success "Nginx configuré pour rediriger vers Kubernetes"
    else
        error "Erreur dans la configuration Nginx"
    fi
}

# Scripts de maintenance
setup_maintenance_scripts() {
    log "Configuration des scripts de maintenance..."
    
    # Créer le répertoire de maintenance
    mkdir -p /opt/datalys/maintenance
    
    # Script de migration
    cat > /opt/datalys/maintenance/migrate-to-k8s.sh << 'EOF'
#!/bin/bash
echo "🚀 Migration vers Kubernetes..."

# Cloner le projet
cd /opt
git clone https://github.com/Pedini95/Datalys_consulting_backend.git
cd Datalys_consulting_backend

# Générer les secrets
./k8s/generate-secrets.sh

# Déployer l'application
./k8s/deploy.sh deploy

echo "✅ Migration terminée !"
EOF
    
    # Script de rollback
    cat > /opt/datalys/maintenance/rollback.sh << 'EOF'
#!/bin/bash
echo "🔄 Rollback vers l'application originale..."

# Arrêter Kubernetes
systemctl stop k3s

# Restaurer l'application
cp -r /opt/k8s-backup/app_backup_* /home/datalys/Datalys_consulting_backend

# Redémarrer les services
systemctl start nginx
cd /home/datalys/Datalys_consulting_backend
pm2 start ecosystem.config.js

echo "✅ Rollback terminé !"
EOF
    
    # Rendre les scripts exécutables
    chmod +x /opt/datalys/maintenance/*.sh
    
    success "Scripts de maintenance configurés"
}

# Affichage des informations finales
show_final_info() {
    log "=== Installation Kubernetes terminée ! ==="
    
    echo ""
    echo "🎉 Kubernetes est maintenant installé sur votre VPS existant !"
    echo ""
    echo "📋 Informations importantes :"
    echo "   • k3s config: /etc/rancher/k3s/k3s.yaml"
    echo "   • kubectl config: $HOME/.kube/config"
    echo "   • Backup de l'ancienne app: $K8S_BACKUP_DIR"
    echo ""
    echo "🌐 Configuration réseau :"
    echo "   • Nginx Ingress: Port 30080 (HTTP), 30443 (HTTPS)"
    echo "   • Nginx proxy: Port 80/443 → Kubernetes"
    echo ""
    echo "🔧 Commandes utiles :"
    echo "   • Vérifier le statut: kubectl get pods --all-namespaces"
    echo "   • Voir les logs: kubectl logs -f -l app=datalys-api -n datalys"
    echo "   • Migration: /opt/datalys/maintenance/migrate-to-k8s.sh"
    echo "   • Rollback: /opt/datalys/maintenance/rollback.sh"
    echo ""
    echo "📝 Prochaines étapes :"
    echo "   1. Tester Kubernetes: kubectl get nodes"
    echo "   2. Migrer l'application: /opt/datalys/maintenance/migrate-to-k8s.sh"
    echo "   3. Configurer le DNS si nécessaire"
    echo ""
    echo "⚠️  Important :"
    echo "   • Votre ancienne application est sauvegardée dans $K8S_BACKUP_DIR"
    echo "   • Vous pouvez faire un rollback si nécessaire"
    echo "   • Testez d'abord avant de migrer complètement"
}

# Fonction principale
main() {
    log "=== Installation Kubernetes sur VPS existant ==="
    
    check_prerequisites
    backup_current_application
    stop_current_application
    install_docker
    install_k3s
    install_helm
    install_nginx_ingress
    install_cert_manager
    setup_namespaces
    configure_nginx_proxy
    setup_maintenance_scripts
    show_final_info
    
    success "Installation terminée avec succès !"
}

# Gestion des erreurs
trap 'error "Installation interrompue par une erreur"' ERR

# Exécution
main "$@" 