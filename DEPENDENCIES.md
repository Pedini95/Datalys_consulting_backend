# Gestion des Dépendances Python

## Problème récurrent avec `click`

### Symptômes
```
ModuleNotFoundError: No module named 'click.core'
```

### Pourquoi ce problème arrive ?

1. **Dépendance transitive non fixée**
   - `click` n'est pas utilisé directement dans notre code
   - C'est Flask qui en a besoin pour ses commandes CLI
   - Flask ne fixe pas la version exacte de `click`

2. **Corruption lors des builds Docker**
   - Les couches Docker cachées peuvent contenir des installations incomplètes
   - Les builds incrémentaux peuvent réutiliser des packages corrompus
   - Le flag `--no-cache` n'efface pas toujours tout

3. **Installations multiples conflictuelles**
   - Si `pip install` est exécuté plusieurs fois, les fichiers peuvent être partiellement écrasés
   - Les fichiers `.pyc` (bytecode Python) peuvent devenir obsolètes

## Solutions implémentées

### 1. ✅ Versions fixées dans `requirements.txt`

```txt
click==8.3.1
Flask==3.1.2
```

**Pourquoi ?** Garantit que la même version est toujours installée.

### 2. ✅ Fichier `requirements-lock.txt` avec TOUTES les versions

Ce fichier contient TOUTES les dépendances avec versions exactes (générées via `pip freeze`).

**Quand l'utiliser ?**
- Pour les déploiements en production
- Pour garantir une reproductibilité à 100%
- Pour débugger des problèmes de compatibilité

**Comment mettre à jour ?**
```bash
# Sur le serveur, depuis un conteneur qui fonctionne
docker exec datalys-api pip freeze > src/requirements-lock.txt
```

### 3. ✅ Dockerfile optimisé

```dockerfile
# Installation en une seule passe pour éviter les corruptions
RUN python -m pip install --no-cache-dir --timeout 600 --upgrade -r requirements.txt && \
    python -c "import click; print('✅ click version:', click.__version__)" && \
    python -c "import flask; print('✅ Flask version:', flask.__version__)"
```

**Avantages :**
- Une seule couche Docker
- Vérification immédiate après installation
- Échec rapide si quelque chose ne va pas

## Bonnes pratiques pour éviter ce problème

### ✅ À FAIRE

1. **Toujours fixer les versions des dépendances principales**
   ```txt
   Flask==3.1.2  # ✅ BON
   Flask          # ❌ MAUVAIS
   ```

2. **Rebuild complet si problème**
   ```bash
   docker stop datalys-api
   docker rm datalys-api
   docker rmi datalys_consulting_backend-datalys-api:latest
   docker-compose build --pull datalys-api
   docker-compose up -d datalys-api
   ```

3. **Vérifier les logs après déploiement**
   ```bash
   docker logs --tail 50 datalys-api | grep -i "error\|fail"
   ```

4. **Tester l'import après build**
   ```bash
   docker exec datalys-api python -c "import click; import flask; print('OK')"
   ```

### ❌ À ÉVITER

1. ❌ Installer des packages manuellement dans le conteneur
   ```bash
   docker exec datalys-api pip install click  # ❌ NE FAIT PAS ÇA
   ```
   **Pourquoi ?** Les changements seront perdus au prochain redémarrage.

2. ❌ Utiliser `--force-reinstall --no-deps`
   ```dockerfile
   RUN pip install --force-reinstall --no-deps click  # ❌ DANGEREUX
   ```
   **Pourquoi ?** `--no-deps` peut créer des incompatibilités.

3. ❌ Mélanger pip et pip3
   ```dockerfile
   RUN pip install flask && pip3 install click  # ❌ INCONSISTANT
   ```

## Checklist de déploiement

Avant chaque déploiement :

- [ ] Les versions sont-elles fixées dans `requirements.txt` ?
- [ ] Le Dockerfile installe-t-il en une seule passe ?
- [ ] Les tests d'import sont-ils présents ?
- [ ] Le build est-il complet (pas de cache corrompu) ?
- [ ] Les logs montrent-ils une initialisation réussie ?

## Commandes utiles

```bash
# Générer requirements-lock.txt depuis un conteneur qui fonctionne
docker exec datalys-api pip freeze > src/requirements-lock.txt

# Vérifier les versions installées
docker exec datalys-api pip list | grep -i "click\|flask"

# Rebuild complet et propre
docker-compose build --pull --no-cache datalys-api

# Tester l'application sans démarrer les workers
docker exec datalys-api python -c "from app import app; print('✅ App OK')"
```

## Historique des incidents

| Date | Problème | Solution | Commit |
|------|----------|----------|--------|
| 2026-01-12 | `ModuleNotFoundError: click.core` | Ajout `click==8.3.1` + Dockerfile optimisé | 35fd52b |

---

**Note :** Ce document doit être mis à jour à chaque incident similaire.
