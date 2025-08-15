#!/usr/bin/env python3
"""
Initialise directement la base MySQL et crée les tables à partir des modèles SQLAlchemy.
- Lit les variables via --env-file et/ou options CLI
- Crée la base si manquante puis crée les tables

Exemples:
  python3 scripts/init_db_direct.py --env-file .env.production
  python3 scripts/init_db_direct.py \
    --db-host 127.0.0.1 --db-port 3306 \
    --db-name datalys_consulting --db-user datalys_user --db-password 'secret'
"""

import argparse
import os
import sys
from typing import Optional


def load_env_file(env_file: str) -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        print("⚠️ python-dotenv non installé; le chargement --env-file sera ignoré")
        return
    if os.path.exists(env_file):
        load_dotenv(env_file, override=True)
        print(f"✅ Variables chargées depuis: {env_file}")
    else:
        print(f"⚠️ Fichier .env introuvable: {env_file}")


def set_env_if_provided(name: str, value: Optional[str]) -> None:
    if value is not None:
        os.environ[name] = str(value)


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialisation de la base et création des tables")
    parser.add_argument("--env-file", help="Chemin du fichier .env à charger", default=None)
    parser.add_argument("--db-host", help="Hôte MySQL", default=None)
    parser.add_argument("--db-port", help="Port MySQL", default=None)
    parser.add_argument("--db-name", help="Nom de la base", default=None)
    parser.add_argument("--db-user", help="Utilisateur MySQL", default=None)
    parser.add_argument("--db-password", help="Mot de passe MySQL", default=None)

    args = parser.parse_args()

    if args.env_file:
        load_env_file(args.env_file)

    set_env_if_provided("DB_HOST", args.db_host)
    set_env_if_provided("DB_PORT", args.db_port)
    set_env_if_provided("DB_NAME", args.db_name)
    set_env_if_provided("DB_USER", args.db_user)
    set_env_if_provided("DB_PASSWORD", args.db_password)

    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    src_path = os.path.join(repo_root, "src")
    if src_path not in sys.path:
        sys.path.insert(0, src_path)

    try:
        import init_db as init_db_module
        success = init_db_module.init_database()
        return 0 if success else 1
    except Exception as exc:
        print(f"❌ Erreur: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main()) 