# app.py - Fichier principal de l'application FeatureHub
# C'est le point d'entrée du serveur Flask, c'est ici qu'on defini toutes les routes

from datetime import datetime

from flask import Flask, render_template, abort

# On crée l'instance de l'application Flask
# __name__ permet a Flask de savoir ou trouver les templates et fichiers statiques
app = Flask(__name__)


# Context processor : ca permet d'injecter des variables dans TOUS les templates
# automatiquement sans devoir les passer a chaque render_template()
# Ici on injecte l'année en cours pour l'afficher dans le footer
@app.context_processor
def inject_current_year():
    return {"current_year": datetime.now().year}


# --- Données simulées (en attendant la base de donnée) ---
# C'est une liste de dictionnaires, chaque dico represente une demande
# On a volontairement mis des combinaisons differentes de status/nature/priorité
# pour tester les badges de couleur dans les templates
features = [
    {
        "id": 1,
        "title": "Mode Sombre",
        "description": "Permettre aux utilisateurs de basculer l'interface en thème sombre pour réduire la fatigue visuelle.",
        "status": "En attente",
        "nature": "Feature",
        "priority": "Haute",
    },
    {
        "id": 2,
        "title": "Crash au chargement des pièces jointes",
        "description": "L'application plante lorsqu'on tente d'ouvrir un fichier PDF joint à une demande existante.",
        "status": "Validé",
        "nature": "Bug",
        "priority": "Haute",
    },
    {
        "id": 3,
        "title": "Refonte du tableau de bord",
        "description": "",  # description vide exprès pour tester le cas "pas de description"
        "status": "En attente",
        "nature": "Amélioration",
        "priority": "Moyenne",
    },
    {
        "id": 4,
        "title": "Export CSV des demandes",
        "description": "Ajouter un bouton permettant d'exporter la liste filtrée des demandes au format CSV.",
        "status": "Rejeté",
        "nature": "Feature",
        "priority": "Basse",
    },
    {
        "id": 5,
        "title": "Notification par e-mail",
        "description": "Envoyer un e-mail à l'auteur lorsque le statut de sa demande change.",
        "status": "En attente",
        "nature": "Feature",
        "priority": "Moyenne",
    },
]


# ============================================================
# ROUTES
# ============================================================

# Route pour la page d'accueil (/)
# On calcule les stats (total et nb en attente) avant de les envoyer au template
@app.route("/")
def index():
    total = len(features)
    # sum() avec un generateur pour compter combien ont le statut "En attente"
    en_attente = sum(1 for f in features if f["status"] == "En attente")

    # render_template() va chercher le fichier index.html dans le dossier templates/
    # et on lui passe les variables dont le template a besoin
    return render_template(
        "index.html",
        features=features,
        total=total,
        en_attente=en_attente,
        active_page="index",  # sert a mettre le lien "Accueil" en surbrillance dans la navbar
    )


# Route pour la page "a propos"
@app.route("/about")
def about():
    return render_template("about.html", active_page="about")


# Route dynamique pour afficher le detail d'une feature
# <int:feature_id> veut dire que Flask attend un entier dans l'URL
# par exemple /feature/3 affichera la feature avec l'id 3
@app.route("/feature/<int:feature_id>")
def view_feature(feature_id):
    # next() parcours la liste et retourne le premier element qui match
    # si aucun element ne correspond, il retourne None (le 2eme argument)
    feature = next((f for f in features if f["id"] == feature_id), None)

    if feature is None:
        # abort(404) déclenche une erreur HTTP 404, Flask va appeler
        # notre gestionaire d'erreur personnalisé defini plus bas
        abort(404)

    return render_template("view_feature.html", feature=feature, active_page=None)


# Gestionaire d'erreur personaliser pour les pages 404
# Le parametre 'e' contient les infos de l'erreur (on l'utilise pas ici)
@app.errorhandler(404)
def page_not_found(e):
    # Important : il faut retourner le code 404 en deuxieme valeur
    # sinon Flask renverais un code 200 (OK) par defaut
    return render_template("404.html", active_page=None), 404


# Ce bloc permet de lancer le serveur directement avec "python app.py"
# debug=True active le rechargement automatique quand on modifie le code
# (super pratique pendant le developpement)
if __name__ == "__main__":
    app.run(debug=True)
