# app/main/routes.py - Le Blueprint principal de l'application.
#
# Note TP3 (Exo 1) : c'est le "C" (Controller) du pattern MVC. Les routes
# reçoivent les requetes HTTP, parlent au Modele (db) et retournent une Vue
# (un template render_template) ou une redirection.
#
# Note TP3 : un Blueprint est un "mini-serveur" autonome qui regroupe des
# routes liées. Ici, le blueprint "main" contient toute la gestion des
# demandes (CRUD). L'authentification est dans un autre blueprint (auth/).

import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from ..models import db, FeatureRequest

# Note TP3 (Exo 1) : on crée le Blueprint avec un nom ('main'). Ce nom servira
# pour les url_for : url_for('main.index') au lieu de url_for('index').
main = Blueprint('main', __name__)


# ============================================================
# CONFIG UPLOAD (héritée du TP2)
# ============================================================
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}


def allowed_file(filename):
    """Vérifie qu'un fichier a une extension autorisée."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ============================================================
# ROUTES - LECTURE
# ============================================================
@main.route("/")
def index():
    # On récupère toutes les demandes triées de la plus récente a la plus ancienne
    features = FeatureRequest.query.order_by(FeatureRequest.created_at.desc()).all()
    total = len(features)
    en_attente = sum(1 for f in features if f.status == "En attente")
    return render_template(
        "main/index.html",
        features=features,
        total=total,
        en_attente=en_attente,
        active_page="index",
    )


@main.route("/about")
def about():
    return render_template("main/about.html", active_page="about")


@main.route("/feature/<int:feature_id>")
def view_feature(feature_id):
    # get_or_404 : retourne la demande si elle existe, sinon une 404 automatique
    feature = FeatureRequest.query.get_or_404(feature_id)
    return render_template("main/view_feature.html", feature=feature, active_page=None)


# ============================================================
# ROUTES - CREATION (Create)
# ============================================================
@main.route("/feature/add", methods=['GET', 'POST'])
@login_required  # Note TP3 (Exo 5) : seuls les users connectés peuvent ajouter
def add_feature():
    if request.method == 'POST':
        # Récupération des données du formulaire
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        nature = request.form.get('nature', 'Feature')
        priority = request.form.get('priority', 'Moyenne')

        # Validation cote serveur (toujours obligatoire, meme si on a "required" en HTML)
        if not title:
            flash("Le titre est obligatoire.", "danger")
            return render_template("main/add_feature.html", active_page=None)
        if len(title) > 100:
            flash("Le titre ne peut pas dépasser 100 caractères.", "danger")
            return render_template("main/add_feature.html", active_page=None)

        # Gestion de la pièce jointe (optionelle)
        filename = None
        file = request.files.get('file')
        if file and file.filename:
            if not allowed_file(file.filename):
                flash("Type de fichier non autorisé (png, jpg, jpeg, gif, pdf).", "danger")
                return render_template("main/add_feature.html", active_page=None)
            filename = secure_filename(file.filename)
            os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))

        # Note TP3 (Exo 5) : on enregistre l'auteur grace a current_user.id.
        # current_user est l'utilisateur connecté, fourni par Flask-Login.
        feature = FeatureRequest(
            title=title,
            description=description,
            nature=nature,
            priority=priority,
            filename=filename,
            author_id=current_user.id,
        )
        try:
            db.session.add(feature)
            db.session.commit()
            flash("Demande ajoutée !", "success")
        except Exception:
            db.session.rollback()
            flash("Erreur lors de l'enregistrement.", "danger")

        # Pattern Post-Redirect-Get : on redirige apres un POST réussi
        return redirect(url_for('main.index'))

    # GET : on affiche le formulaire vide
    return render_template("main/add_feature.html", active_page=None)


# ============================================================
# ROUTES - MODIFICATION (Update)
# ============================================================
@main.route("/feature/<int:feature_id>/edit", methods=['GET', 'POST'])
@login_required  # Note TP3 (Exo 6) : il faut etre connecté
def edit_feature(feature_id):
    feature = FeatureRequest.query.get_or_404(feature_id)

    # Note TP3 (Exo 6) : VERIFICATION D'AUTORISATION.
    # @login_required vérifie l'AUTHENTIFICATION (qui est-ce ?).
    # Mais il faut aussi vérifier l'AUTORISATION (a-t-il le droit ?).
    # Ici, on s'assure que l'user connecté est bien l'auteur de la demande.
    if feature.author_id != current_user.id:
        flash("Vous n'avez pas la permission de modifier cette demande.", "danger")
        return redirect(url_for('main.view_feature', feature_id=feature.id))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()

        # Meme validation qu'a la création
        if not title:
            flash("Le titre est obligatoire.", "danger")
            return render_template("main/edit_feature.html", feature=feature, active_page=None)
        if len(title) > 100:
            flash("Le titre ne peut pas dépasser 100 caractères.", "danger")
            return render_template("main/edit_feature.html", feature=feature, active_page=None)

        # On modifie l'objet directement, SQLAlchemy détecte les changements
        feature.title = title
        feature.description = request.form.get('description', '').strip()
        feature.nature = request.form.get('nature', feature.nature)
        feature.priority = request.form.get('priority', feature.priority)
        feature.status = request.form.get('status', feature.status)

        try:
            db.session.commit()
            flash("Demande modifiée !", "success")
            return redirect(url_for('main.view_feature', feature_id=feature.id))
        except Exception:
            db.session.rollback()
            flash("Erreur lors de la modification.", "danger")
            return render_template("main/edit_feature.html", feature=feature, active_page=None)

    # GET : on affiche le formulaire pre-rempli avec les valeurs actuelles
    return render_template("main/edit_feature.html", feature=feature, active_page=None)


# ============================================================
# ROUTES - SUPPRESSION (Delete)
# ============================================================
@main.route("/feature/<int:feature_id>/delete", methods=['POST'])
@login_required  # Note TP3 (Exo 6)
def delete_feature(feature_id):
    """Note TP3 (Exo 6) : protection double :
    - @login_required : doit etre connecté
    - vérification author_id : doit etre l'auteur de la demande
    """
    feature = FeatureRequest.query.get_or_404(feature_id)

    if feature.author_id != current_user.id:
        flash("Vous n'avez pas la permission de supprimer cette demande.", "danger")
        return redirect(url_for('main.view_feature', feature_id=feature.id))

    title = feature.title  # On le garde pour le message flash
    try:
        db.session.delete(feature)
        db.session.commit()
        flash(f'Demande "{title}" supprimée.', "success")
    except Exception:
        db.session.rollback()
        flash("Erreur lors de la suppression.", "danger")
    return redirect(url_for('main.index'))
