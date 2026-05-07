# run.py - Le NOUVEAU point d'entrée de l'application.
# Note TP3 (Exo 1) : avec le pattern "Application Factory", on ne crée plus l'app
# directement ici. On appelle simplement la fonction create_app() définie dans
# le package "app/" qui s'occupe de tout le setup (config, base de données, blueprints).
#
# Pour lancer le serveur : python run.py

from app import create_app

# create_app() construit et configure l'application Flask, puis nous la rend.
app = create_app()

if __name__ == "__main__":
    # debug=True : auto-reload du serveur quand on modifie le code (pratique en dev).
    app.run(debug=True)
