# FeatureHub

Application web de gestion de demandes de fonctionnalités, bugs et améliorations.
Développée avec **Flask**, **SQLAlchemy**, **Flask-Login**, **Jinja2** et **Bootstrap 5**.

Cette version (`featureHub_v3`) couvre l'intégralité des **TP1, TP2 et TP3**
du cours d'Architecture Web (ECAM).

## Prérequis

- Python 3.10 ou supérieur

## Installation

```bash
# Créer l'environnement virtuel
python -m venv venv

# Activer l'environnement
# Windows :
venv\Scripts\activate
# macOS / Linux :
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

## Lancement

```bash
python run.py
```

L'application est accessible sur [http://127.0.0.1:5000](http://127.0.0.1:5000).

> **Note** : si vous arrivez d'une version antérieure (v1 ou v2), supprimez
> le fichier `instance/featurehub.db` avant le premier lancement. Le schéma
> de la base a évolué (ajout de la table `user` et de la clé étrangère
> `author_id`), `db.create_all()` recréera tout proprement.

## Premiers pas

1. Lancez l'application avec `python run.py`.
2. Cliquez sur **Inscription** dans la navbar et créez un compte (mot de passe ≥ 4 caractères).
3. Connectez-vous avec ce compte.
4. Cliquez sur **Ajouter une demande** et créez votre première demande.
5. Vous pouvez modifier ou supprimer vos propres demandes via la page de détail.

## Structure du projet

```
featureHub_v3/
├── run.py                          # Point d'entrée (lance l'application)
├── requirements.txt                # Dépendances Python
├── README.md
├── instance/
│   └── featurehub.db               # Base SQLite (générée au démarrage)
└── app/                            # Package principal (architecture MVC)
    ├── __init__.py                 # Application Factory create_app()
    ├── models.py                   # Modèles SQLAlchemy (User + FeatureRequest)
    ├── main/                       # Blueprint principal (CRUD des demandes)
    │   ├── __init__.py
    │   └── routes.py
    ├── auth/                       # Blueprint d'authentification
    │   ├── __init__.py
    │   └── routes.py
    ├── templates/
    │   ├── base.html               # Layout commun (navbar dynamique + footer)
    │   ├── 404.html
    │   ├── main/                   # Templates du blueprint main
    │   │   ├── index.html, about.html
    │   │   ├── view_feature.html, add_feature.html, edit_feature.html
    │   │   ├── _card.html, _form.html
    │   └── auth/                   # Templates du blueprint auth
    │       ├── login.html
    │       └── register.html
    └── static/
        ├── css/style.css
        └── uploads/                # Pièces jointes des demandes
```

## Routes disponibles

| URL                          | Méthode    | Auth requise              | Description                              |
|------------------------------|------------|---------------------------|------------------------------------------|
| `/`                          | GET        | Non                       | Tableau de bord (liste des demandes)     |
| `/about`                     | GET        | Non                       | Page de présentation                     |
| `/feature/<int:id>`          | GET        | Non                       | Détail d'une demande                     |
| `/feature/add`               | GET / POST | Oui                       | Création d'une demande                   |
| `/feature/<int:id>/edit`     | GET / POST | Oui (auteur uniquement)   | Modification d'une demande               |
| `/feature/<int:id>/delete`   | POST       | Oui (auteur uniquement)   | Suppression d'une demande                |
| `/register`                  | GET / POST | Non                       | Inscription                              |
| `/login`                     | GET / POST | Non                       | Connexion                                |
| `/logout`                    | GET        | Oui                       | Déconnexion                              |

## Fonctionnalités implémentées

### TP1 — Initialisation (slides 1 à 3)

- Architecture Flask minimale, mode debug, gestionnaire 404 personnalisé.
- Templates Jinja2 avec héritage (`base.html` + blocs `content`/`footer`).
- Partial `_card.html` réutilisable pour la grille de cartes (principe DRY).
- Navigation multi-pages avec lien actif conditionnel via `active_page`.
- Génération d'URLs avec `url_for()` partout (jamais d'URL en dur).
- Style personnalisé Bootstrap 5 + petit effet de survol sur les cartes.

### TP2 — Formulaires & Base de données (slides 4 à 6)

- Formulaire d'ajout avec validation côté serveur (titre obligatoire, ≤ 100 caractères).
- Messages flash Bootstrap (catégories `success` / `danger` / `warning` / `info`).
- Pattern **Post-Redirect-Get** systématique après chaque POST réussi.
- Modèle SQLAlchemy `FeatureRequest` avec horodatage automatique (`created_at`).
- Cycle CRUD complet : créer / lire / modifier / supprimer.
- Suppression via POST + modale Bootstrap de confirmation (jamais via GET).
- Upload de pièces jointes sécurisé : `secure_filename`, extensions autorisées
  (png/jpg/jpeg/gif/pdf), taille max 2 Mo, gestionnaire 413.

### TP3 — Architecture & Sécurité (slides 7 et 8)

- **Refactorisation MVC complète** : passage d'un fichier monolithique à une
  architecture en packages avec :
  - Application Factory (`create_app()` dans `app/__init__.py`).
  - Modèles isolés dans `app/models.py`.
  - Routes regroupées dans des Blueprints (`main` et `auth`).
  - Imports locaux pour casser les dépendances circulaires.
- **Authentification complète** avec Flask-Login :
  - Modèle `User` héritant de `UserMixin`.
  - Hachage des mots de passe via `werkzeug.security` (jamais de mot de passe en clair).
  - Routes `/register`, `/login`, `/logout`.
  - `current_user` accessible dans tous les templates.
- **Navbar dynamique** selon l'état de connexion (`current_user.is_authenticated`).
- **Relation One-to-Many** entre `User` et `FeatureRequest` via `author_id` +
  `db.relationship('FeatureRequest', backref='author')`.
- **Permissions** : décorateur `@login_required` sur les routes sensibles +
  vérification `feature.author_id == current_user.id` pour modifier ou supprimer.
  Les boutons Modifier/Supprimer ne s'affichent que pour l'auteur.

## Correspondance avec les exercices du TP3

| Exercice TP3                                | Fichier(s) concerné(s)                                |
|---------------------------------------------|--------------------------------------------------------|
| 1. Refactorisation MVC (Factory + Blueprints) | `run.py`, `app/__init__.py`, `app/main/routes.py`     |
| 2. Modèle User (UserMixin + hachage)        | `app/models.py` (classe `User`)                        |
| 3. Inscription / Connexion / Déconnexion    | `app/auth/routes.py`, `templates/auth/`               |
| 4. Navbar dynamique                         | `app/templates/base.html` (`current_user.is_authenticated`) |
| 5. Relation auteur-demande                  | `app/models.py` (`db.relationship` + `db.ForeignKey`), `routes.py` (`author_id=current_user.id`) |
| 6. Permissions (auteur uniquement)          | `app/main/routes.py` (vérification `author_id == current_user.id`), `view_feature.html` (affichage conditionnel des boutons) |
