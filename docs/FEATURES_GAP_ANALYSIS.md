# 📋 Analyse des Fonctionnalités Manquantes - WORKSPACE PRO

**Date**: 9 Octobre 2025  
**Comparaison**: Cahier des charges vs Backend actuel

---

## ✅ **CE QUI EST DÉJÀ IMPLÉMENTÉ**

### 1. **Gestion des Projets** ✅
- ✅ CRUD complet des projets
- ✅ Association projets ↔ partenaires
- ✅ Gestion des dossiers et sous-dossiers
- ✅ Upload de fichiers (PDF, Word, Excel, images, etc.)
- ✅ Recherche sur projets
- ✅ Historique d'actions automatique
- ✅ Notes sur les projets (via champ `description`)

### 2. **Gestion des Incidents** ✅ (Partiel)
- ✅ CRUD complet des incidents
- ✅ Association incidents ↔ projets
- ✅ Statuts : `ouvert`, `en_cours`, `resolu`, `ferme`
- ✅ Priorités : `basse`, `moyenne`, `haute`, `critique`
- ✅ Assignation à un expert (`assigned_to`)
- ✅ Notes de résolution (`resolution_notes`)
- ✅ Chat/Messages (via `parent_id` pour réponses)
- ✅ Notifications push automatiques (Firebase FCM)

### 3. **Gestion des Supports** ✅ (Partiel)
- ✅ Création de demandes de support (`type='support'`)
- ✅ Priorités : `basse`, `moyenne`, `haute`, `critique`
- ✅ Statuts : `ouvert`, `en_cours`, `resolu`, `ferme`
- ✅ Notifications push si priorité haute/critique

### 4. **Sécurité & Authentification** ✅
- ✅ JWT Authentication
- ✅ Gestion des rôles (Admin, Manager, User)
- ✅ Changement de mot de passe obligatoire (première connexion)
- ✅ Rate limiting (protection anti-brute force)
- ✅ Sessions Redis
- ✅ Réinitialisation de mot de passe par email

### 5. **Productivité & Ergonomie** ✅
- ✅ Dashboard récapitulatif
- ✅ Statistiques sur projets/incidents/supports
- ✅ Historique d'actions automatique
- ✅ Notifications push (Firebase FCM)
- ✅ API RESTful complète

---

## ❌ **CE QUI MANQUE (À IMPLÉMENTER)**

### 🚨 **1. INCIDENTS - Système de Criticité P0-P4** ❌

**Cahier des charges** :
- P0 : Arrêt de service (prise en charge immédiate)
- P1 : Forte dégradation de service
- P2 : Dégradation de service
- P3 : Incident ordinaire sans impact
- P4 : Incident mineur

**État actuel** :
- ❌ Priorités génériques : `basse`, `moyenne`, `haute`, `critique`
- ❌ Pas de mapping P0-P4
- ❌ Pas de description détaillée des niveaux

**Action requise** :
```python
# Modifier models/incident.py
priority = db.Column(db.String(20), default='P3')  
# Valeurs : 'P0', 'P1', 'P2', 'P3', 'P4'

# Ajouter un champ impact
impact = db.Column(db.String(50), nullable=True)
# Valeurs : 'arret_service', 'service_degrade', 'majeur', 'mineur'
```

---

### 🚨 **2. INCIDENTS - Numéro d'incident auto-généré** ❌

**Cahier des charges** :
> "Le numéro de l'incident généré automatiquement à chaque création d'incident et ne peut être modifié"

**État actuel** :
- ❌ Pas de champ `incident_number` (ex: `INC-2025-00001`)
- ✅ ID numérique simple existe (`id`)

**Action requise** :
```python
# Ajouter dans models/incident.py
incident_number = db.Column(db.String(50), unique=True, nullable=False)

# Générer automatiquement : INC-2025-00001, INC-2025-00002, etc.
def generate_incident_number():
    year = datetime.now().year
    last_incident = Incident.query.filter(
        Incident.incident_number.like(f'INC-{year}-%')
    ).order_by(Incident.id.desc()).first()
    
    if last_incident:
        last_num = int(last_incident.incident_number.split('-')[-1])
        new_num = last_num + 1
    else:
        new_num = 1
    
    return f'INC-{year}-{new_num:05d}'
```

---

### 🚨 **3. INCIDENTS - Champs obligatoires manquants** ❌

**Cahier des charges** :
- ✅ Numéro d'incident (à ajouter)
- ✅ Association au compte client (existe : `user_id`)
- ✅ Projet ou support concerné (existe : `project_id`)
- ❌ **Nom du déclarant** (pas de champ dédié)
- ❌ **Domaine concerné** : Réseau, Infrastructure système, Cloud, Energie
- ✅ Affectation d'un expert (existe : `assigned_to`)
- ❌ **Criticité P0-P4** (à remplacer)
- ❌ **Impact** : arrêt de service, service fortement dégradé, majeur, mineur

**Action requise** :
```python
# Ajouter dans models/incident.py
declarant_name = db.Column(db.String(255), nullable=False)  # Nom du déclarant
domain = db.Column(db.String(50), nullable=False)  
# Valeurs : 'reseau', 'infrastructure', 'cloud', 'energie'
impact = db.Column(db.String(50), nullable=False)
# Valeurs : 'arret_service', 'service_degrade', 'majeur', 'mineur'
```

---

### 🚨 **4. INCIDENTS - Statuts spécifiques** ❌

**Cahier des charges** :
- Nouveau (couleur Bleue)
- En cours (couleur Orange)
- En attente (couleur Grise) + motif de mise en attente
- En Arbitrage (couleur Violet)

**État actuel** :
- ✅ `ouvert`, `en_cours`, `resolu`, `ferme`
- ❌ Pas de statut `nouveau`
- ❌ Pas de statut `en_attente`
- ❌ Pas de statut `en_arbitrage`
- ❌ Pas de champ `motif_attente`

**Action requise** :
```python
# Modifier models/incident.py
status = db.Column(db.String(20), default='nouveau')
# Valeurs : 'nouveau', 'en_cours', 'en_attente', 'en_arbitrage', 'resolu', 'ferme'

motif_attente = db.Column(db.Text, nullable=True)  # Motif si en_attente
```

---

### 🚨 **5. SUPPORT - SLA avec Délais et Compteurs** ❌

**Cahier des charges** :

| Priorité | Prise en charge | Résolution estimée |
|----------|----------------|-------------------|
| P1       | 30 min (24/7)  | 4h ouvrées        |
| P2       | 1h ouvrée      | 1 jour ouvré      |
| P3       | 4h ouvrées     | 3 jours ouvrés    |
| P4       | 1 jour ouvré   | 5 jours ouvrés    |

**Compteur** : Vert si dans les temps, Rouge si dépassement

**État actuel** :
- ❌ Pas de champ `sla_prise_en_charge_deadline`
- ❌ Pas de champ `sla_resolution_deadline`
- ❌ Pas de calcul automatique des deadlines
- ❌ Pas de compteur temps restant
- ❌ Pas d'indicateur vert/rouge

**Action requise** :
```python
# Ajouter dans models/incident.py (pour type='support')
sla_prise_en_charge_deadline = db.Column(db.DateTime, nullable=True)
sla_resolution_deadline = db.Column(db.DateTime, nullable=True)
sla_prise_en_charge_status = db.Column(db.String(20), default='vert')  # 'vert', 'rouge'
sla_resolution_status = db.Column(db.String(20), default='vert')  # 'vert', 'rouge'

# Calculer automatiquement lors de la création
def calculate_sla_deadlines(priority, created_at):
    sla_config = {
        'P1': {'prise_en_charge_minutes': 30, 'resolution_hours': 4},
        'P2': {'prise_en_charge_hours': 1, 'resolution_hours': 24},
        'P3': {'prise_en_charge_hours': 4, 'resolution_hours': 72},
        'P4': {'prise_en_charge_hours': 24, 'resolution_hours': 120}
    }
    # Calculer les deadlines...
```

---

### 🚨 **6. SUPPORT - KPI (Indicateurs de Performance)** ❌

**Cahier des charges** :
- Taux de tickets résolus dans les SLA (%)
- Délai moyen de résolution par priorité
- Taux de satisfaction client (post-ticket)

**État actuel** :
- ❌ Pas de calcul de taux de respect SLA
- ❌ Pas de calcul de délai moyen
- ❌ Pas de système de satisfaction client

**Action requise** :
```python
# Ajouter dans models/incident.py (pour type='support')
satisfaction_rating = db.Column(db.Integer, nullable=True)  # 1-5 étoiles
satisfaction_comment = db.Column(db.Text, nullable=True)

# Créer un service KPI
class SupportKPIService:
    def get_sla_compliance_rate(self, date_range):
        # Calculer % de tickets résolus dans les SLA
        pass
    
    def get_average_resolution_time(self, priority):
        # Calculer délai moyen par priorité
        pass
    
    def get_satisfaction_rate(self, date_range):
        # Calculer taux de satisfaction moyen
        pass
```

---

### 🚨 **7. SÉCURITÉ - Authentification Multi-Facteur (MFA)** ❌

**Cahier des charges** :
> "L'authentification Multi facteur devra être mise en place en envoyant un code par mail à l'utilisateur pour chaque connexion."

**État actuel** :
- ✅ JWT Authentication
- ✅ Email de réinitialisation de mot de passe
- ❌ **Pas de MFA (code par email à chaque connexion)**

**Action requise** :
```python
# 1. Ajouter dans models/user.py
mfa_enabled = db.Column(db.Boolean, default=False)
mfa_code = db.Column(db.String(10), nullable=True)
mfa_code_expiry = db.Column(db.DateTime, nullable=True)

# 2. Modifier auth_service.py
def login(self, email, password):
    # ... vérification mot de passe ...
    
    # Générer code MFA
    mfa_code = generate_numeric_code(6)  # 123456
    user.mfa_code = mfa_code
    user.mfa_code_expiry = datetime.utcnow() + timedelta(minutes=5)
    db.session.commit()
    
    # Envoyer email avec code
    send_mfa_code_email(user.email, mfa_code)
    
    return {
        'requires_mfa': True,
        'user_id': user.id,
        'message': 'Code MFA envoyé par email'
    }

# 3. Créer route /auth/verify-mfa
@bp.route('/auth/verify-mfa', methods=['POST'])
def verify_mfa():
    # Vérifier le code MFA
    # Si OK, générer le token JWT
    pass
```

---

### ✅ **8. COMPTES UTILISATEURS - Code Client Unique** ✅

**Cahier des charges** :
> "La génération d'un code client comme login unique. En effet compte tenu de la contrainte qu'il peut avoir sur la mobilité coté client, l'utilisation d'un email coté client peut s'avérer problématique à un certain moment. La génération d'un code client unique pour chaque client permet de s'affranchir d'un changement de mail ou d'une mobilité éventuelle."

**État actuel** :
- ✅ Login par email
- ✅ **Code client unique** (ex: `DATALYS-2025-001`)
- ✅ Génération automatique lors de la création
- ✅ Login avec email OU code client
- ✅ Migration SQL pour utilisateurs existants

**Implémentation** :
```python
# ✅ Ajouté dans models/user.py
client_code = db.Column(db.String(50), unique=True, nullable=True, index=True)

# ✅ Méthode de génération automatique
@classmethod
def generate_client_code(cls):
    year = datetime.now().year
    last_user = cls.query.filter(
        cls.client_code.like(f'DATALYS-{year}-%')
    ).order_by(cls.id.desc()).with_for_update().first()
    
    if last_user and last_user.client_code:
        last_num = int(last_user.client_code.split('-')[-1])
        new_num = last_num + 1
    else:
        new_num = 1
    
    return f'DATALYS-{year}-{new_num:03d}'

# ✅ Modifié auth_service.py pour accepter email OU client_code
def login(self, identifier: str, password: str):
    from sqlalchemy import or_
    user = User.query.filter(
        or_(
            User.email == identifier,
            User.client_code == identifier
        ),
        User.is_deleted == False
    ).first()
    # ...
```

**Documentation** : `/docs/CLIENT_CODE_UNIQUE.md`  
**Migration SQL** : `/src/migrations/add_client_code_to_users.sql`  
**Date d'implémentation** : 9 Octobre 2025

---

### 🚨 **9. COMPTES UTILISATEURS - Comptes Multiples par Partenaire** ❌

**Cahier des charges** :
> "Le client peut avoir un contrat de support en plus des projets. Pour cela il peut dédier la gestion de l'interface à un autre compte. Autrement il peut avoir des clients avec deux comptes de connexion. Un pour l'espace projets et Incidents et l'autre pour l'espace Support. L'application devrait pouvoir créer ses identifiants. Le compte support ne doit pas avoir accès aux informations de projets et vice versa."

**État actuel** :
- ✅ Rôles : Admin, Manager, User
- ❌ **Pas de rôle "Support"**
- ❌ **Pas de séparation Projets/Incidents vs Support**
- ❌ Pas de permissions granulaires par module

**Action requise** :
```python
# 1. Ajouter des rôles spécifiques
# - "Partner_Projects" : Accès projets/incidents uniquement
# - "Partner_Support" : Accès support uniquement
# - "Partner_Full" : Accès complet

# 2. Ajouter dans models/user.py
access_modules = db.Column(db.JSON, nullable=True)
# Exemple : ['projects', 'incidents'] ou ['support']

# 3. Créer middleware de vérification
@require_module_access('projects')
def get_projects():
    # Vérifier que l'utilisateur a accès au module 'projects'
    pass
```

---

### 🚨 **10. NOTIFICATIONS - Email automatique création incident** ❌

**Cahier des charges** :
> "Une fois l'incident créé par le client, un mail de notification devra être envoyé à tous les Experts pour leur notifier la création d'un nouvel incident avec son numéro contenu dans le mail."

**État actuel** :
- ✅ Notifications push (Firebase FCM)
- ❌ **Pas d'email automatique aux experts**

**Action requise** :
```python
# Dans services/incident_service.py
def create(self, data, user_id):
    # ... créer incident ...
    
    # Envoyer email à tous les experts (rôle Admin/Manager)
    experts = User.query.join(Role).filter(
        Role.name.in_(['Admin', 'Manager']),
        User.is_active == True
    ).all()
    
    for expert in experts:
        send_incident_notification_email(
            expert.email,
            incident.incident_number,
            incident.title,
            incident.priority
        )
```

---

### 🚨 **11. INCIDENTS - Refus de solution et réouverture** ❌

**Cahier des charges** :
> "Il pourra en revanche refuser une solution de résolution en rouvrant l'incident et en indiquant que le problème de base n'est pas résolu."

**État actuel** :
- ✅ Changement de statut possible
- ❌ **Pas de workflow de refus de solution**
- ❌ Pas de champ `refusal_reason`

**Action requise** :
```python
# Ajouter dans models/incident.py
refusal_count = db.Column(db.Integer, default=0)
refusal_reason = db.Column(db.Text, nullable=True)
last_refusal_at = db.Column(db.DateTime, nullable=True)

# Créer route /incidents/refuse-solution
@bp.route('/incidents/<int:incident_id>/refuse-solution', methods=['POST'])
def refuse_solution(incident_id):
    # Rouvrir l'incident
    # Incrémenter refusal_count
    # Enregistrer refusal_reason
    # Notifier l'expert
    pass
```

---

### 🚨 **12. DASHBOARD - Statistiques avancées** ❌

**Cahier des charges** :
- Nombre d'incidents par projet pour un client donné
- Nombre de projets pour un client donné
- Liste de projets ou d'incidents sélectionnés
- Voir directement la liste des nouveaux objets ajoutés récemment

**État actuel** :
- ✅ Dashboard de base existe
- ❌ **Statistiques avancées limitées**
- ❌ Pas de filtre "nouveaux objets récents"

**Action requise** :
```python
# Améliorer routes/dashboard.py
@bp.route('/dashboard/statistics', methods=['POST'])
def get_advanced_statistics():
    # Incidents par projet
    # Projets par client
    # Objets récents (dernières 24h)
    pass
```

---

### 🚨 **13. FICHIERS - Upload dans incidents/supports** ❌

**Cahier des charges** :
> "Elle doit permettre également d'ajouter des fichiers (PDF, Word, png, jpeg, Excel, CSV, fichiers textes) dans le suivi de l'incident."

**État actuel** :
- ✅ Upload de fichiers dans projets
- ❌ **Pas de relation Incident ↔ Fichiers**

**Action requise** :
```python
# Modifier models/file.py
incident_id = db.Column(db.Integer, db.ForeignKey('incidents.id'), nullable=True)

# Créer route /incidents/<id>/upload-file
@bp.route('/incidents/<int:incident_id>/upload-file', methods=['POST'])
def upload_incident_file(incident_id):
    # Upload fichier et associer à l'incident
    pass
```

---

## 📊 **RÉSUMÉ DES PRIORITÉS**

### 🔴 **CRITIQUE (À faire immédiatement)**

1. ✅ **Système de criticité P0-P4** (au lieu de basse/moyenne/haute/critique) - **FAIT**
2. ✅ **Numéro d'incident auto-généré** (INC-2025-00001) - **FAIT**
3. ✅ **Champs obligatoires incidents** : déclarant, domaine, impact - **FAIT**
4. ✅ **Authentification Multi-Facteur (MFA)** par email - **FAIT**
5. ✅ **Code client unique** pour login - **FAIT**

### 🟠 **IMPORTANT (À faire rapidement)**

6. ❌ **SLA avec compteurs** (délais, deadlines, vert/rouge)
7. ✅ **Statuts spécifiques** : nouveau, en_attente, en_arbitrage - **FAIT**
8. ✅ **Email automatique aux experts** lors création incident - **FAIT**
9. ❌ **Refus de solution** et réouverture incident
10. ❌ **Upload fichiers dans incidents**

### 🟡 **SOUHAITABLE (Amélioration)**

11. ❌ **KPI Support** (taux SLA, délai moyen, satisfaction)
12. ❌ **Comptes multiples par partenaire** (Projets vs Support)
13. ❌ **Statistiques avancées** dashboard

---

## 📝 **PLAN D'ACTION RECOMMANDÉ**

### **Phase 1 : Incidents & Support (2-3 jours)**
1. Ajouter criticité P0-P4 + impact
2. Générer numéro incident automatique
3. Ajouter champs : déclarant, domaine
4. Modifier statuts : nouveau, en_attente, en_arbitrage
5. Email automatique aux experts

### **Phase 2 : Sécurité (1-2 jours)**
6. Implémenter MFA par email
7. Générer code client unique
8. Modifier login pour accepter email OU code client

### **Phase 3 : SLA & Support (2-3 jours)**
9. Calculer deadlines SLA automatiquement
10. Compteur temps restant (vert/rouge)
11. Refus de solution et réouverture

### **Phase 4 : Améliorations (1-2 jours)**
12. Upload fichiers dans incidents
13. KPI Support
14. Statistiques avancées dashboard

---

## 🎯 **TEMPS ESTIMÉ TOTAL : 6-10 jours**

---

**Note** : Ce document sera mis à jour au fur et à mesure de l'implémentation des fonctionnalités manquantes.

