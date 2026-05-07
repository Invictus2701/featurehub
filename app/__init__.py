# app/__init__.py - Le coeur de l'organisation MVC : "Application Factory".
#
# Note TP3 (Exo 1) : ce fichier est exécuté quand on fait "from app import create_app".
# Le fait qu'il s'appelle __init__.py transforme le dossier "app/" en "package" Python.
#
# Note TP3 (Exo 1) : au lieu de créer une instance globale "app = Flask(__name__)" en haut
# du fichier (comme dans les TPs precedents), on définit une FONCTION create_app()
# qui crée et configure l'application. Avantages :
# - Permet de creer plusieurs instances (utile pour les tests automatiques).
# - Casse les imports circulaires entre les fichiers.
# - Permet de switcher facilement la config (dev / production / test).

from datetime import datetime
from flask import Flask, render_template
from flask_login import LoginManager

from .models import db, User


# Note TP3 (Exo 2) : on instancie le LoginManager SANS app, comme pour db.
# Il sera "branché" plus tard dans create_app() avec login_manager.init_app(app).
login_manager = LoginManager()


def create_app():
    """Note TP3 (Exo 1) : la fonction-fabrique qui assemble notre application.

    A chaque appel, elle :
    1) Crée une nouvelle instance Flask
    2) La configure
    3) Branche les extensions (db, login_manager)
    4) Enregistre les blueprints (les "modules" de routes)
    5) Crée les tables de la base si necessaire
    6) Retourne l'app prête a etre lancée
    """
    app = Flask(__name__)

    # ---------- Configuration ----------
    # SECRET_KEY : clé secrète utilisée pour signer les cookies de session.
    # Sans elle, ni flash() ni Flask-Login ne fonctionnent.
    app.config['SECRET_KEY'] = 'dev-secret-key-a-changer-en-production'

    # Note TP3 : la base SQLite sera créée dans le dossier "instance/" automatiquement.
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///featurehub.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Config pour les uploads (héritée du TP2). Le chemin pointe vers le dossier
    # static a l'INTERIEUR du package app/.
    app.config['UPLOAD_FOLDER'] = 'app/static/uploads'
    app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2 Mo max

    # ---------- Branchement des extensions ----------
    # Note TP3 (Exo 1) : maintenant qu'on a une instance "app", on peut lier
    # l'objet "db" a cette app. C'est ce qui permet a db.session de savoir
    # vers quelle base envoyer les requetes.
    db.init_app(app)

    # Note TP3 (Exo 2) : pareil pour Flask-Login. On lui dit aussi vers quelle
    # page rediriger les utilisateurs non connectés qui essayent d'acceder a
    # une route protégée par @login_required.
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  # 'nom_du_blueprint.nom_de_la_fonction'
    login_manager.login_message = "Veuillez vous connecter pour accéder à cette page."
    login_manager.login_message_category = 'warning'

    # Note TP3 (Exo 2) : le user_loader est UNE FONCTION que Flask-Login appelle
    # a chaque requete pour reconstruire l'objet User a partir de l'id stocké dans
    # le cookie de session. Sans ca, current_user resterais toujours anonyme.
    @login_manager.user_loader
    def load_user(user_id):
        # user_id arrive en string (depuis le cookie), on le convertit en int.
        return User.query.get(int(user_id))

    # ---------- Variables disponibles dans tous les templates ----------
    @app.context_processor
    def inject_current_year():
        # current_year est utilisable dans n'importe quel template (dans le footer)
        return {"current_year": datetime.now().year}

    # ---------- Enregistrement des Blueprints ----------
    # Note TP3 (Exo 1 + Exo 3) : un Blueprint = un "mini-serveur" Flask autonome
    # avec ses propres routes. On les enregistre ici pour les "brancher" sur l'app.
    #
    # Note TP3 : les imports sont LOCAUX (a l'interieur de la fonction) volontairement.
    # Cela évite les imports circulaires : si on importait main/routes.py au sommet
    # du fichier, et que main/routes.py importait db, on aurait une boucle infinie.
    from .main.routes import main as main_bp
    app.register_blueprint(main_bp)

    from .auth.routes import auth as auth_bp
    app.register_blueprint(auth_bp)

    # ---------- Création des tables au démarage ----------
    # Note TP3 (Exo 1) : db.create_all() a besoin de savoir a quelle app il
    # s'addresse. C'est pour ça qu'on l'entoure de "with app.app_context()".
    with app.app_context():
        db.create_all()

    # ---------- Gestionaire d'erreurs 404 ----------
    @app.errorhandler(404)
    def page_not_found(e):
        # On retourne le template + le code 404 (sinon Flask renverait 200 par defaut)
        return render_template("404.html"), 404

    @app.errorhandler(413)
    def file_too_large(e):
        # Note TP2 (Exo 7) : déclenché quand un upload dépasse MAX_CONTENT_LENGTH
        from flask import flash, redirect, url_for
        flash("Le fichier est trop volumineux (max 2 Mo).", "danger")
        return redirect(url_for('main.add_feature'))

    return app
