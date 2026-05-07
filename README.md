# FeatureHub

Application web de gestion de demandes de fonctionnalités, bugs et améliorations.
Développée avec **Flask**, **SQLAlchemy**, **Jinja2** et **Bootstrap 5**.

Cette version (`featureHub_v2`) couvre l'intégralité des **TP1 et TP2** du cours
d'Architecture Web (ECAM).

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
python app.py
```

L'application est accessible sur [http://127.0.0.1:5000](http://127.0.0.1:5000).

> **Note** : la base de données SQLite est créée automatiquement au premier
> lancement dans `instance/featurehub.db`. Pas besoin de l'initialiser manuellement.

## Premiers pas

1. Lancez l'application avec `python app.py`.
2. Sur la page d'accueil, cliquez sur **Ajouter une demande**.
3. Remplissez le formulaire (titre obligatoire, ≤ 100 caractères) et joignez
   éventuellement un fichier (PNG/JPG/PDF, max 2 Mo).
4. Validez : vous êtes redirigé vers l'accueil avec un message flash de confirmation.
5. Sur la page de détail, vous pouvez **Modifier** ou **Supprimer** la demande.

## Structure du projet

```
featureHub_v2/
├── app.py                          # Point d'entrée Flask + modèle + routes
├── requirements.txt                # Dépendances Python (Flask + Flask-SQLAlchemy)
├── README.md
├── instance/
│   └── featurehub.db               # Base SQLite (générée au démarrage)
├── static/
│   ├── css/
│   │   └── style.css               # Feuille de styles personnalisée
│   └── uploads/                    # Pièces jointes des demandes
└── templates/
    ├── base.html                   # Layout commun (Navbar + Footer + flash)
    ├── 404.html                    # Page d'erreur 404 personnalisée
    ├── index.html                  # Tableau de bord (grille de demandes + stats)
    ├── about.html                  # Page de présentation
    ├── view_feature.html           # Détail d'une demande + boutons Modifier/Supprimer
    ├── add_feature.html            # Formulaire de création
    ├── edit_feature.html           # Formulaire de modification
    ├── _card.html                  # Partial : carte d'une demande (DRY)
    └── _form.html                  # Partial : formulaire factorisé add + edit
```

## Routes disponibles

| URL                          | Méthode    | Description                                        |
|------------------------------|------------|----------------------------------------------------|
| `/`                          | GET        | Tableau de bord (liste des demandes + stats)       |
| `/about`                     | GET        | Page de présentation                               |
| `/feature/<int:id>`          | GET        | Détail d'une demande                               |
| `/feature/add`               | GET / POST | Création d'une demande (avec upload optionnel)     |
| `/feature/<int:id>/edit`     | GET / POST | Modification d'une demande                         |
| `/feature/<int:id>/delete`   | POST       | Suppression d'une demande (POST uniquement)        |

> **Note de sécurité** : la route de suppression accepte uniquement la méthode
> `POST` (jamais `GET`). Cela évite qu'un robot d'indexation ou un préchargement
> de navigateur déclenche une suppression accidentelle en suivant un lien.

## Modèle de données

Une seule table : `feature_requests`.

| Colonne        | Type           | Contraintes                | Description                              |
|----------------|----------------|----------------------------|------------------------------------------|
| `id`           | Integer        | PRIMARY KEY                | Identifiant auto-incrémenté              |
| `title`        | String(100)    | NOT NULL                   | Titre, max 100 caractères                |
| `description`  | Text           | —                          | Description longue, optionnelle          |
| `status`       | String(20)     | DEFAULT 'En attente'       | "En attente", "Validé", "Rejeté"         |
| `nature`       | String(20)     | DEFAULT 'Feature'          | "Feature", "Bug", "Amélioration"         |
| `priority`     | String(20)     | DEFAULT 'Moyenne'          | "Haute", "Moyenne", "Basse"              |
| `created_at`   | DateTime       | DEFAULT now()              | Horodatage automatique                   |
| `filename`     | String(255)    | nullable                   | Nom de la pièce jointe, optionnel        |

## Fonctionnalités implémentées

### TP1 — Initialisation (slides 1 à 3)

- Architecture Flask minimale, mode debug, gestionnaire 404 personnalisé.
- Templates Jinja2 avec héritage (`base.html` + blocs `content`/`footer`).
- Partial `_card.html` réutilisable pour la grille de cartes (principe DRY).
- Navigation multi-pages avec lien actif conditionnel via `active_page`.
- Génération d'URLs avec `url_for()` partout (jamais d'URL en dur).
- Style personnalisé Bootstrap 5 + petit effet de survol sur les cartes.

### TP2 — Formulaires & Base de données (slides 4 à 6)

- **Formulaire d'ajout** avec validation côté serveur (titre obligatoire, ≤ 100 caractères).
- **Messages flash Bootstrap** (catégories `success` / `danger` / `warning` / `info`)
  affichés automatiquement par `base.html` via `get_flashed_messages()`.
- **Pattern Post-Redirect-Get** systématique après chaque POST réussi (évite la
  duplication des données si l'utilisateur fait F5).
- **Base SQLite** via Flask-SQLAlchemy (`SQLALCHEMY_DATABASE_URI`).
- **Modèle `FeatureRequest`** avec horodatage automatique (`created_at = datetime.utcnow`).
- **Cycle CRUD complet** :
  - Create : route `/feature/add`
  - Read : routes `/` (liste) et `/feature/<id>` (détail)
  - Update : route `/feature/<id>/edit` avec formulaire pré-rempli
  - Delete : route `/feature/<id>/delete` (POST uniquement)
- **Modale Bootstrap de confirmation** pour la suppression (sécurité UX).
- **Upload de pièces jointes** sécurisé :
  - `enctype="multipart/form-data"` côté HTML
  - `secure_filename()` pour nettoyer le nom (empêche `../../config.py`)
  - Vérification de l'extension (png, jpg, jpeg, gif, pdf uniquement)
  - Limite de 2 Mo via `MAX_CONTENT_LENGTH`
  - Gestionnaire d'erreur 413 (Request Entity Too Large)
- **Partial `_form.html`** factorisé entre les pages add et edit (principe DRY).
- **Affichage différencié de la pièce jointe** sur la page de détail :
  - Si c'est une image → balise `<img>` directe
  - Sinon → bouton de téléchargement

## Correspondance avec les exercices du TP2

| Exercice TP2                            | Fichier(s) concerné(s)                                    |
|-----------------------------------------|-----------------------------------------------------------|
| 1. Formulaire d'ajout + flash messages  | `app.py` (route `add_feature`), `templates/add_feature.html`, `base.html` (zone flash) |
| 2. Configuration DB + modèle            | `app.py` (config SQLAlchemy + classe `FeatureRequest`)    |
| 3. Persistance Create + Read            | `app.py` (`db.session.add/commit` + `query.all()`), `templates/index.html` |
| 4. Page de détail                       | `app.py` (route `view_feature` avec `get_or_404`), `templates/view_feature.html` |
| 5. Modification (Update)                | `app.py` (route `edit_feature`), `templates/edit_feature.html`, `templates/_form.html` |
| 6. Suppression (Delete) + modale        | `app.py` (route `delete_feature`), `templates/view_feature.html` (modale) |
| 7. Upload de pièces jointes             | `app.py` (config `UPLOAD_FOLDER`, `secure_filename`, gestion 413), `templates/add_feature.html` |

## Codes HTTP utilisés

| Code | Signification              | Cas d'usage                                       |
|------|----------------------------|---------------------------------------------------|
| 200  | OK                         | Lecture ou affichage de page réussi               |
| 302  | Found                      | Redirection (Post-Redirect-Get)                   |
| 404  | Not Found                  | Demande inexistante (`get_or_404`)                |
| 413  | Payload Too Large          | Upload dépassant 2 Mo                             |
