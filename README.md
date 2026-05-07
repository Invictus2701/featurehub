# FeatureHub

Application web de gestion de demandes de fonctionnalités, bugs et améliorations.
Développée avec **Flask**, **SQLAlchemy**, **Flask-Login**, **Flask-JWT-Extended**,
**Jinja2** et **Bootstrap 5**.

Cette version (`featureHub_v4`) couvre l'intégralité des **TP1, TP2, TP3 et TP4**
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

> **Note** : si vous arrivez d'une version antérieure (v1, v2 ou v3), supprimez
> le fichier `instance/featurehub.db` avant le premier lancement. Le schéma de la
> base évolue à chaque TP, et `db.create_all()` ne modifie pas une table existante.

## Premiers pas — interface web

1. Lancez l'application avec `python run.py`.
2. Cliquez sur **Inscription** dans la navbar et créez un compte (mot de passe ≥ 4 caractères).
3. Connectez-vous avec ce compte.
4. Cliquez sur **Ajouter une demande** et créez votre première demande.
5. Sur l'accueil, utilisez le formulaire de filtres pour trier par nature/statut/priorité.
6. Vous pouvez modifier ou supprimer vos propres demandes via la page de détail.

## Premiers pas — API REST

1. Récupérer un token JWT :

   ```bash
   curl -X POST http://127.0.0.1:5000/api/v1/auth/token \
     -H "Content-Type: application/json" \
     -d "{\"username\":\"alice\",\"password\":\"alicepass\"}"
   ```

2. Utiliser le token pour créer une demande :

   ```bash
   curl -X POST http://127.0.0.1:5000/api/v1/features \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer VOTRE_TOKEN_ICI" \
     -d "{\"title\":\"Demande via API\",\"priority\":\"Haute\"}"
   ```

3. Lister les demandes (sans token, ouvert au public) :

   ```bash
   curl http://127.0.0.1:5000/api/v1/features
   ```

## Structure du projet

```
featureHub_v4/
├── run.py                          # Point d'entrée (lance l'application)
├── requirements.txt                # Dépendances Python
├── README.md
├── .gitignore                      # Fichiers exclus de git
├── diagramme_classes.html          # Diagramme UML des classes
├── diagramme_packages.html         # Diagramme UML des packages
├── diagramme_bdd.html              # Diagramme de la base de données
├── instance/
│   └── featurehub.db               # Base SQLite (générée au démarrage)
└── app/                            # Package principal (architecture MVC)
    ├── __init__.py                 # Application Factory create_app()
    ├── models.py                   # Modèles SQLAlchemy (User + FeatureRequest)
    ├── main/                       # Blueprint principal (CRUD HTML)
    │   ├── __init__.py
    │   └── routes.py
    ├── auth/                       # Blueprint d'authentification web
    │   ├── __init__.py
    │   └── routes.py
    ├── api/                        # Blueprint API REST (versionné /api/v1)
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
        └── uploads/                # Pièces jointes des demandes (.gitkeep)
```

## Routes disponibles

### Interface web (HTML)

| URL                          | Méthode    | Auth requise              | Description                              |
|------------------------------|------------|---------------------------|------------------------------------------|
| `/`                          | GET        | Non                       | Tableau de bord avec filtres et tri      |
| `/about`                     | GET        | Non                       | Page de présentation                     |
| `/feature/<int:id>`          | GET        | Non                       | Détail d'une demande                     |
| `/feature/add`               | GET / POST | Oui (Flask-Login)         | Création d'une demande                   |
| `/feature/<int:id>/edit`     | GET / POST | Oui (auteur uniquement)   | Modification d'une demande               |
| `/feature/<int:id>/delete`   | POST       | Oui (auteur uniquement)   | Suppression d'une demande                |
| `/register`                  | GET / POST | Non                       | Inscription                              |
| `/login`                     | GET / POST | Non                       | Connexion                                |
| `/logout`                    | GET        | Oui                       | Déconnexion                              |

### API REST (JSON)

| Verbe   | URI                              | Description                            | Auth | Code  |
|---------|----------------------------------|----------------------------------------|------|-------|
| POST    | `/api/v1/auth/token`             | Obtenir un token JWT                   | —    | 200   |
| GET     | `/api/v1/features`               | Lister (filtres + tri + pagination)    | —    | 200   |
| POST    | `/api/v1/features`               | Créer une demande                      | JWT  | 201   |
| GET     | `/api/v1/features/<int:id>`      | Détail d'une demande                   | —    | 200   |
| PUT     | `/api/v1/features/<int:id>`      | Remplacer entièrement (champs absents = défauts) | JWT  | 200   |
| PATCH   | `/api/v1/features/<int:id>`      | Modifier partiellement (autres champs préservés) | JWT  | 200   |
| DELETE  | `/api/v1/features/<int:id>`      | Supprimer (corps de réponse vide)      | JWT  | 204   |

#### Paramètres GET pour `/api/v1/features`

| Paramètre   | Type   | Description                              | Exemple                |
|-------------|--------|------------------------------------------|------------------------|
| `nature`    | string | Filtre par nature                        | `?nature=Bug`          |
| `status`    | string | Filtre par statut                        | `?status=En attente`   |
| `priority`  | string | Filtre par priorité                      | `?priority=Haute`      |
| `sort`      | string | Colonne de tri (created_at, title, ...)  | `?sort=title`          |
| `order`     | string | Sens du tri (`asc` ou `desc`)            | `?order=asc`           |
| `page`      | int    | Numéro de page (défaut 1)                | `?page=2`              |
| `per_page`  | int    | Items par page (défaut 10)               | `?per_page=5`          |

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

### TP4 — API REST & JWT

- **Filtres et tri dynamiques** sur la page d'accueil :
  - Formulaire `method="GET"` avec listes déroulantes (Nature, Statut, Priorité, Tri).
  - Construction de la requête SQLAlchemy en chaîne via `request.args`.
  - Tri par priorité avec `db.case()` (sinon ordre alphabétique = Basse, Haute, Moyenne).
  - Persistance des choix dans le formulaire après soumission.
  - Bouton "Réinitialiser" pour repartir à zéro.
- **Blueprint API versionné** (`/api/v1/`) :
  - Méthode `to_dict()` sur le modèle pour la sérialisation JSON.
  - Helper `make_error()` pour des réponses d'erreur cohérentes.
  - Toutes les routes retournent du JSON (jamais du HTML, même en cas d'erreur).
- **CRUD complet via REST** :
  - `GET /features` avec filtres, tri et pagination.
  - `GET /features/<id>` pour le détail.
  - `POST /features` pour la création (code 201 Created).
  - `PUT /features/<id>` pour le remplacement total.
  - `PATCH /features/<id>` pour la modification partielle.
  - `DELETE /features/<id>` retourne 204 No Content.
- **Authentification JWT** avec Flask-JWT-Extended :
  - `POST /auth/token` retourne un token (Bearer) en échange d'identifiants.
  - Décorateur `@jwt_required()` sur les opérations d'écriture.
  - `get_jwt_identity()` pour récupérer l'utilisateur du token.
  - Les routes de lecture restent publiques (pas de token nécessaire).

## Correspondance avec les exercices du TP4

| Exercice TP4                                | Fichier(s) concerné(s)                                              |
|---------------------------------------------|---------------------------------------------------------------------|
| 1. Filtres et tri dynamiques                | `app/main/routes.py` (route `index`), `app/templates/main/index.html` |
| 2. Blueprint API + endpoints GET            | `app/api/routes.py`, `app/__init__.py` (enregistrement avec `url_prefix='/api/v1'`), `app/models.py` (`to_dict()`) |
| 3. Création via l'API (POST)                | `app/api/routes.py` (route `create_feature`)                       |
| 4. Mise à jour (PUT et PATCH)               | `app/api/routes.py` (routes `update_feature_put` et `update_feature_patch`) |
| 5. Suppression et JWT                       | `app/api/routes.py` (routes `delete_feature` et `get_token`), `app/__init__.py` (config `JWT_SECRET_KEY`) |

## Tester l'API rapidement

Une fois l'application lancée, créez un compte via `/register` (par exemple `alice` / `alicepass`), puis testez l'API :

```bash
# 1. Obtenir un token
curl -X POST http://127.0.0.1:5000/api/v1/auth/token \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"alice\",\"password\":\"alicepass\"}"
# → {"access_token": "eyJ..."}

# 2. Créer une demande (avec le token)
curl -X POST http://127.0.0.1:5000/api/v1/features \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJ..." \
  -d "{\"title\":\"Test API\",\"priority\":\"Haute\"}"
# → 201 Created + JSON de la demande

# 3. Lister avec filtres et pagination (sans token)
curl "http://127.0.0.1:5000/api/v1/features?nature=Feature&page=1&per_page=5"

# 4. Modifier partiellement (PATCH)
curl -X PATCH http://127.0.0.1:5000/api/v1/features/1 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJ..." \
  -d "{\"status\":\"Validé\"}"

# 5. Supprimer
curl -X DELETE http://127.0.0.1:5000/api/v1/features/1 \
  -H "Authorization: Bearer eyJ..."
# → 204 No Content (réponse vide)
```

## Documentation complémentaire

Le projet est livré avec trois diagrammes UML rendus en HTML :

- `diagramme_classes.html` — diagramme de classes (modèle de domaine User + FeatureRequest)
- `diagramme_packages.html` — diagramme de packages (organisation du code source)
- `diagramme_bdd.html` — diagramme de base de données relationnelle (MCD + MLD + SQL)

Ouvrez ces fichiers dans un navigateur pour les consulter.

## Codes HTTP utilisés

| Code | Signification              | Cas d'usage                                       |
|------|----------------------------|---------------------------------------------------|
| 200  | OK                         | Lecture ou modification réussie                   |
| 201  | Created                    | Ressource créée (POST)                            |
| 204  | No Content                 | Suppression réussie (corps vide)                  |
| 302  | Found                      | Redirection (Post-Redirect-Get)                   |
| 400  | Bad Request                | Données invalides (champ manquant, format...)     |
| 401  | Unauthorized               | Auth manquante ou token invalide                  |
| 404  | Not Found                  | Ressource inexistante                             |
| 413  | Payload Too Large          | Upload dépassant 2 Mo                             |
