# app.py - Fichier principal de l'application FeatureHub
# C'est le point d'entrée du serveur Flask, c'est ici qu'on defini toutes les routes,
# le modele de donnée, et la configuration generale.

import os
from datetime import datetime

from flask import Flask, render_template, abort, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename


# ============================================================
# CREATION DE L'APP + CONFIGURATION
# ============================================================
# __name__ permet a Flask de savoir ou trouver les templates et fichiers statiques
app = Flask(__name__)

# Note TP2 : la SECRET_KEY est OBLIGATOIRE pour utiliser flash() et la session.
# Flask l'utilise pour signer les cookies (empeche un utilisateur de modifier sa session
# pour se faire passer pour un admin par ex). En vrai projet on la mettrait dans une
# variable d'environement, jamais en dur dans le code.
app.config['SECRET_KEY'] = 'dev-secret-key-a-changer-en-production'

# Note TP2 (Exo 2) : on indique a SQLAlchemy ou stocker les données.
# 'sqlite:///featurehub.db' = fichier featurehub.db dans le dossier "instance/" de Flask
# (qui est créé automatiquement). C'est super pratique en dev : pas de serveur de DB
# a installer, juste un fichier sur le disque.
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///featurehub.db'
# Désactive un warning verbeux qu'on n'utilise pas
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Note TP2 (Exo 7) : configuration pour les uploads de fichiers
app.config['UPLOAD_FOLDER'] = 'static/uploads'   # ou les fichiers seront sauvés
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2 Mo max (2*1024*1024 octets)

# Liste des extensions qu'on accepte. Tout le reste sera refusé pour la sécurité.
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}


def allowed_file(filename):
    """Note TP2 (Exo 7) : verifie qu'un fichier a une extension autorisée.

    On découpe le nom autour du dernier point ('.') et on regarde l'extension
    en minuscule. Si l'extension n'est pas dans ALLOWED_EXTENSIONS -> refus.
    Ca evite que quelqu'un upload un .exe ou un .php malveilant."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Instance de SQLAlchemy liée a notre app Flask. db.session sera notre point d'entrée
# pour parler a la base.
db = SQLAlchemy(app)


# ============================================================
# MODELE
# ============================================================
class FeatureRequest(db.Model):
    """Note TP2 (Exo 2) : représentation Python d'UNE demande dans la base.

    Chaque attribut de classe est une colonne de la table. SQLAlchemy s'occupe
    de la conversion Python <-> SQL. Quand on instancie cette classe (ex.
    FeatureRequest(title="...")) on crée un objet en mémoire ; il faut ensuite
    db.session.add() puis db.session.commit() pour vraiment l'enregistrer en base.
    """
    # Sans ca, la table aurait pour nom "feature_request" (auto-généré par SQLAlchemy).
    # On préfere le pluriel et un nom explicite.
    __tablename__ = 'feature_requests'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='En attente')
    nature = db.Column(db.String(20), default='Feature')
    priority = db.Column(db.String(20), default='Moyenne')
    # Note TP2 : datetime.utcnow (sans parenthese!) passe la FONCTION,
    # pas son resultat. SQLAlchemy l'appelle a chaque insertion -> chaque ligne aura
    # sa propre date. Si on mettait datetime.utcnow() avec () toutes les lignes auraient
    # la meme date (celle du démarage du serveur).
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Note TP2 (Exo 7) : nom du fichier joint, optionel (peut etre None)
    filename = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        # Sert au debugage : quand on fait print(une_feature) dans la console,
        # ca affiche un truc lisible au lieu de <FeatureRequest object at 0x7fa...>
        return f'<FeatureRequest {self.id}: {self.title}>'


# Note TP2 (Exo 2) : on crée les tables au démarage si elles n'existent pas encore.
# app.app_context() est nécessaire car db.create_all() a besoin de savoir a quelle app
# il parle (utile quand on a plusieurs app dans le meme projet).
with app.app_context():
    db.create_all()


# ============================================================
# CONTEXT PROCESSOR (variables disponibles dans TOUS les templates)
# ============================================================
@app.context_processor
def inject_current_year():
    # Permet d'utiliser {{ current_year }} dans n'importe quel template
    # sans avoir a le passer manuellement a chaque render_template().
    return {"current_year": datetime.now().year}


# ============================================================
# ROUTES - LECTURE
# ============================================================
@app.route("/")
def index():
    # Note TP2 (Exo 3) : on récupere TOUTES les demandes, triées par date décroissante
    # (.desc() = "descending" = du plus récent au plus ancien).
    # .all() exécute la requete et retourne une liste Python.
    features = FeatureRequest.query.order_by(FeatureRequest.created_at.desc()).all()

    # Stats pour le tableau de bord
    total = len(features)
    en_attente = sum(1 for f in features if f.status == "En attente")

    return render_template(
        "index.html",
        features=features,
        total=total,
        en_attente=en_attente,
        active_page="index",
    )


@app.route("/about")
def about():
    return render_template("about.html", active_page="about")


@app.route("/feature/<int:feature_id>")
def view_feature(feature_id):
    # Note TP2 (Exo 4) : get_or_404 cherche par primary key (ici l'id) et
    # retourne automatiquement une 404 si rien n'est trouvé. Ca remplace
    # le pattern verbeux "obj = query.get(id) ; if obj is None: abort(404)".
    feature = FeatureRequest.query.get_or_404(feature_id)
    return render_template("view_feature.html", feature=feature, active_page=None)


# ============================================================
# ROUTES - CREATION (CREATE)
# ============================================================
@app.route("/feature/add", methods=['GET', 'POST'])
def add_feature():
    # Note TP2 (Exo 1) : meme route, deux comportements differents selon la méthode HTTP :
    # - GET  : on AFFICHE le formulaire vide
    # - POST : on TRAITE les données soumises par le formulaire
    if request.method == 'POST':
        # request.form.get('xxx', valeur_par_defaut) : on extrait les champs du formulaire.
        # .strip() enleve les espaces au debut et a la fin.
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        nature = request.form.get('nature', 'Feature')
        priority = request.form.get('priority', 'Moyenne')

        # Note TP2 (Exo 1) : VALIDATION cote serveur.
        # Important : meme si on met "required" en HTML, il faut TOUJOURS revalider
        # cote serveur car le HTML peut etre contourné (curl, Postman, navigateur modifié...).
        if not title:
            flash("Le titre est obligatoire.", "danger")
            return render_template("add_feature.html", active_page=None)
        if len(title) > 100:
            flash("Le titre ne peut pas dépasser 100 caractères.", "danger")
            return render_template("add_feature.html", active_page=None)

        # Note TP2 (Exo 7) : gestion du fichier joint (optionel).
        filename = None
        file = request.files.get('file')
        if file and file.filename:
            # On verifie que l'extension est autorisée
            if not allowed_file(file.filename):
                flash("Type de fichier non autorisé (png, jpg, jpeg, gif, pdf).", "danger")
                return render_template("add_feature.html", active_page=None)
            # secure_filename nettoie le nom : enleve les caracteres dangereux comme "../"
            # qui permetteraient a un attaquant d'ecrire ailleurs sur le disque.
            filename = secure_filename(file.filename)
            # On s'assure que le dossier de destination existe (sinon on le crée)
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        # Note TP2 (Exo 3) : on crée l'objet Python et on l'enregistre en base.
        feature = FeatureRequest(
            title=title,
            description=description,
            nature=nature,
            priority=priority,
            filename=filename,
        )
        try:
            db.session.add(feature)      # ajoute l'objet a la "session" (= zone de travail)
            db.session.commit()          # envoie tout en base
            flash("Demande ajoutée !", "success")
        except Exception:
            # Si quelque chose plante, on annule la transaction (rollback) pour ne pas
            # laisser la base dans un etat incohérent.
            db.session.rollback()
            flash("Erreur lors de l'enregistrement.", "danger")

        # Note TP2 : pattern Post-Redirect-Get.
        # Apres un POST réussi, on REDIRIGE vers une autre page au lieu de re-rendre
        # un template. Pourquoi ? Parce que si l'utilisateur fait F5 (rafraichir) sur
        # une page rendue apres POST, le navigateur renvoie le formulaire et la demande
        # est créée 2x ! Le redirect change la page courante en GET => F5 ne re-soumet plus.
        return redirect(url_for('index'))

    # Méthode GET : on affiche le formulaire vide
    return render_template("add_feature.html", active_page=None)


# ============================================================
# ROUTES - MODIFICATION (UPDATE)
# ============================================================
@app.route("/feature/<int:feature_id>/edit", methods=['GET', 'POST'])
def edit_feature(feature_id):
    # On commence par récuperer la demande a modifier (ou 404 si elle n'existe pas)
    feature = FeatureRequest.query.get_or_404(feature_id)

    if request.method == 'POST':
        title = request.form.get('title', '').strip()

        # Meme validation qu'a la création
        if not title:
            flash("Le titre est obligatoire.", "danger")
            return render_template("edit_feature.html", feature=feature, active_page=None)
        if len(title) > 100:
            flash("Le titre ne peut pas dépasser 100 caractères.", "danger")
            return render_template("edit_feature.html", feature=feature, active_page=None)

        # Note TP2 (Exo 5) : on met a jour les attributs DIRECTEMENT sur l'objet.
        # Pas besoin de db.session.add() ici : l'objet vient de get_or_404, il est deja
        # dans la session SQLAlchemy. Tout changement sur ses attributs est detecté
        # automatiquement et sera envoyé en base au prochain commit().
        feature.title = title
        feature.description = request.form.get('description', '').strip()
        feature.nature = request.form.get('nature', feature.nature)
        feature.priority = request.form.get('priority', feature.priority)
        feature.status = request.form.get('status', feature.status)

        try:
            db.session.commit()
            flash("Demande modifiée !", "success")
            # Note TP2 : on redirige vers la page de detail (Post-Redirect-Get encore)
            return redirect(url_for('view_feature', feature_id=feature.id))
        except Exception:
            db.session.rollback()
            flash("Erreur lors de la modification.", "danger")
            return render_template("edit_feature.html", feature=feature, active_page=None)

    # GET : on affiche le formulaire pré-rempli avec les valeurs actuelles
    return render_template("edit_feature.html", feature=feature, active_page=None)


# ============================================================
# ROUTES - SUPPRESSION (DELETE)
# ============================================================
@app.route("/feature/<int:feature_id>/delete", methods=['POST'])
def delete_feature(feature_id):
    """Note TP2 (Exo 6) : route accessible UNIQUEMENT en POST (pas en GET).

    Pourquoi ? Parce qu'un GET ne devrait JAMAIS modifier des données. Si on autorisait
    le GET, un simple <a href="/feature/1/delete">Supprimer</a> pourrait etre suivi
    par un robot d'indexation Google ou par le pré-chargement du navigateur, ce qui
    supprimerait des demandes sans que personne ait cliqué !
    """
    feature = FeatureRequest.query.get_or_404(feature_id)
    # On garde le titre AVANT la suppression pour pouvoir l'afficher dans le message flash
    title = feature.title

    try:
        db.session.delete(feature)
        db.session.commit()
        flash(f'Demande "{title}" supprimée.', "success")
    except Exception:
        db.session.rollback()
        flash("Erreur lors de la suppression.", "danger")

    return redirect(url_for('index'))


# ============================================================
# GESTIONAIRES D'ERREURS
# ============================================================
@app.errorhandler(404)
def page_not_found(e):
    # Le parametre 'e' contient les infos de l'erreur (on l'utilise pas ici)
    # Important : il faut retourner le code 404 en deuxieme valeur sinon Flask
    # renverais un code 200 (OK) par defaut.
    return render_template("404.html", active_page=None), 404


@app.errorhandler(413)
def file_too_large(e):
    """Note TP2 (Exo 7) : Flask declenche 413 (Request Entity Too Large) quand un
    fichier dépasse MAX_CONTENT_LENGTH. On affiche un message clair et on renvoie
    l'utilisateur sur le formulaire d'ajout."""
    flash("Le fichier est trop volumineux (max 2 Mo).", "danger")
    return redirect(url_for('add_feature'))


# ============================================================
# LANCEMENT
# ============================================================
# Ce bloc permet de lancer le serveur directement avec "python app.py"
# debug=True active le rechargement automatique quand on modifie le code
# (super pratique pendant le developpement)
if __name__ == "__main__":
    app.run(debug=True)
