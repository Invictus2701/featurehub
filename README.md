# FeatureHub

Application web de gestion de demandes de fonctionnalités, bugs et améliorations.
Développée avec **Flask**, **Jinja2** et **Bootstrap 5**.

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
featureHub_app/
├── app.py                  # Point d'entrée Flask
├── requirements.txt        # Dépendances Python
├── README.md
├── static/
│   └── css/
│       └── style.css       # Feuille de styles personnalisée
└── templates/
    ├── base.html           # Layout de base (Navbar + Footer)
    ├── index.html          # Page d'accueil (tableau de bord)
    ├── about.html          # Page À propos
    ├── view_feature.html   # Détail d'une demande
    ├── 404.html            # Page d'erreur 404
    └── _card.html          # Partial — carte d'une demande
```
