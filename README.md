# FeatureHub

Application web de gestion de demandes de fonctionnalités, bugs et améliorations.
Développée avec **Flask**, **Jinja2** et **Bootstrap 5**.

Cette version (`featureHub_v1`) couvre l'intégralité du **TP1 — Initialisation**
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
python app.py
```

L'application est accessible sur [http://127.0.0.1:5000](http://127.0.0.1:5000).

## Structure du projet

```
featureHub_v1/
├── app.py                  # Point d'entrée Flask (routes + données simulées)
├── requirements.txt        # Dépendances Python (Flask)
├── README.md
├── static/
│   └── css/
│       └── style.css       # Feuille de styles personnalisée (fond + effet hover)
└── templates/
    ├── base.html           # Layout de base (Navbar + Footer + bloc content)
    ├── index.html          # Page d'accueil (tableau de bord)
    ├── about.html          # Page À propos
    ├── view_feature.html   # Détail d'une demande
    ├── 404.html            # Page d'erreur 404 personnalisée
    └── _card.html          # Partial réutilisable — carte d'une demande
```

## Routes disponibles

| URL                 | Méthode | Description                                       |
|---------------------|---------|---------------------------------------------------|
| `/`                 | GET     | Tableau de bord (stats + grille de demandes)     |
| `/about`            | GET     | Page de présentation du projet                   |
| `/feature/<int:id>` | GET     | Détail d'une demande spécifique                  |
| (toute URL inconnue)| GET     | Page 404 personnalisée                           |

## Fonctionnalités implémentées (TP1)

### Côté Python (`app.py`)

- **Application Flask minimale** avec route racine `/`, mode debug actif et bloc `if __name__ == "__main__"`.
- **Données simulées** : liste `features` de 5 dictionnaires couvrant toutes les combinaisons de statut (`En attente`, `Validé`, `Rejeté`), nature (`Bug`, `Feature`, `Amélioration`) et priorité (`Haute`, `Moyenne`, `Basse`). L'une des entrées a volontairement une description vide pour tester le rendu.
- **Calcul des statistiques** (`total`, `en_attente`) côté Python avant rendu du template.
- **Route dynamique** `/feature/<int:feature_id>` avec recherche de la demande via `next()` et levée de `abort(404)` si l'identifiant n'existe pas.
- **Gestionnaire 404 personnalisé** (`@app.errorhandler(404)`) qui affiche une page conviviale au lieu du message brut de Flask.
- **Context processor** qui injecte automatiquement l'année courante (`current_year`) dans tous les templates pour le footer.

### Côté templates (Jinja2 + Bootstrap)

- **Héritage de templates** : `base.html` définit le squelette commun (navbar, footer, bloc `content`), toutes les autres pages l'étendent via `{% extends "base.html" %}`. Principe **DRY** respecté.
- **Partial réutilisable** : `_card.html` contient le HTML d'une seule carte ; il est inclus dans la boucle de `index.html` via `{% include '_card.html' %}`.
- **Navbar dynamique** : la classe Bootstrap `active` est appliquée conditionnellement sur le lien correspondant à la page courante grâce à la variable `active_page` envoyée par chaque route.
- **Badges colorés dynamiques** dans `_card.html` et `view_feature.html` :
  - Nature : rouge (Bug), bleu (Feature), bleu clair (Amélioration).
  - Priorité : rouge (Haute), jaune (Moyenne), gris (Basse).
  - Statut : bleu clair (En attente), vert (Validé), rouge (Rejeté).
- **Gestion de la description vide** : si `feature.description` est vide, affichage du message *"Pas de description fournie."* en italique grisé.
- **Grille responsive** Bootstrap : 3 cartes par ligne sur grand écran, 2 sur tablette, 1 sur mobile.
- **Génération d'URLs via `url_for()`** partout (liens navbar, bouton « Détails », fichier CSS) — aucune URL écrite en dur.
- **Auto-escaping Jinja2** laissé actif partout (aucun usage du filtre `| safe`).

### Côté style (`static/css/style.css`)

- Fond de page gris clair, plus reposant que le blanc pur.
- Effet *hover* sur les cartes : légère élévation et ombre plus marquée au survol.

## Correspondance avec les exercices du TP1

| Exercice TP1                                  | Fichier(s) concerné(s)                                |
|-----------------------------------------------|--------------------------------------------------------|
| 1. Environnement & installation               | `requirements.txt`, `.venv/`                          |
| 2. Serveur minimal                            | `app.py`                                              |
| 3. Templating Jinja2 + Bootstrap (base.html, index.html) | `templates/base.html`, `templates/index.html`         |
| 4. Fichiers statiques                         | `static/css/style.css` + `url_for('static', ...)` dans `base.html` |
| 5. Injection de données + logique Jinja       | `app.py` (liste + stats), `templates/index.html`, `_card.html` |
| 6. Template partials (DRY)                    | `templates/_card.html` + `{% include %}` dans `index.html` |
| 7. Navigation multi-pages + lien actif        | `templates/about.html`, navbar dans `base.html`, `active_page` dans `app.py` |
| 8. Détail d'une feature + 404                 | `templates/view_feature.html`, `templates/404.html`, `abort(404)` + `errorhandler` dans `app.py` |
