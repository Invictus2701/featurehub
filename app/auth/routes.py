# app/auth/routes.py - Blueprint qui gère l'authentification.
#
# Note TP3 (Exo 3) : on a séparé l'authentification dans un blueprint dédié pour
# bien isoler cette partie sensible. Ca permet aussi de réutiliser facilement ce
# module dans d'autres projets.
#
# Routes contenues :
# - /register : créer un compte
# - /login : se connecter
# - /logout : se déconnecter

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user

from ..models import db, User

# Note TP3 (Exo 3) : nom du blueprint = 'auth'.
# url_for('auth.login') -> /login
auth = Blueprint('auth', __name__)


# ============================================================
# INSCRIPTION (Register)
# ============================================================
@auth.route('/register', methods=['GET', 'POST'])
def register():
    # Note TP3 : si l'user est deja connecté, ca n'a pas de sens de le laisser
    # créer un nouveau compte. On le redirige vers l'accueil.
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        # Note TP3 (Exo 3) : récupération + validation cote serveur
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm', '')

        # Le username ne doit pas etre vide
        if not username:
            flash("Le nom d'utilisateur est obligatoire.", "danger")
            return render_template('auth/register.html', active_page='register')

        # Le mot de passe doit faire au moins 4 caracteres (consigne du TP)
        if len(password) < 4:
            flash("Le mot de passe doit faire au moins 4 caractères.", "danger")
            return render_template('auth/register.html', active_page='register')

        # Verifier que les 2 saisies du mot de passe sont identiques
        if password != confirm:
            flash("Les deux mots de passe ne correspondent pas.", "danger")
            return render_template('auth/register.html', active_page='register')

        # Note TP3 (Exo 3) : verifier que ce username n'est pas deja pris.
        # filter_by(username=...).first() retourne le 1er User trouvé ou None.
        if User.query.filter_by(username=username).first() is not None:
            flash("Ce nom d'utilisateur est déjà pris.", "danger")
            return render_template('auth/register.html', active_page='register')

        # Note TP3 (Exo 3) : création de l'user. set_password() s'occupe de hasher
        # le mot de passe AVANT de le stocker. JAMAIS de mot de passe en clair en DB.
        user = User(username=username)
        user.set_password(password)

        try:
            db.session.add(user)
            db.session.commit()
            flash("Compte créé ! Vous pouvez maintenant vous connecter.", "success")
            return redirect(url_for('auth.login'))
        except Exception:
            db.session.rollback()
            flash("Erreur lors de la création du compte.", "danger")

    # GET : on affiche le formulaire d'inscription vide
    return render_template('auth/register.html', active_page='register')


# ============================================================
# CONNEXION (Login)
# ============================================================
@auth.route('/login', methods=['GET', 'POST'])
def login():
    # Si deja connecté, on n'affiche pas le formulaire de connexion
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        # On cherche l'user dans la base
        user = User.query.filter_by(username=username).first()

        # Note TP3 (Exo 3) : on vérifie que :
        #  1) l'user existe (user is not None)
        #  2) ET le mot de passe correspond (check_password)
        # Important : on ne dit PAS lequel des 2 est faux, pour limiter
        # les fuites d'information aux attaquants.
        if user is None or not user.check_password(password):
            flash("Identifiants invalides.", "danger")
            return render_template('auth/login.html', active_page='login')

        # Note TP3 (Exo 3) : login_user() est LA fonction magique de Flask-Login.
        # Elle place l'id de l'utilisateur dans la session (cookie signé) et
        # rend current_user disponible partout dans l'app.
        login_user(user)
        flash(f"Bienvenue, {user.username} !", "success")
        return redirect(url_for('main.index'))

    return render_template('auth/login.html', active_page='login')


# ============================================================
# DECONNEXION (Logout)
# ============================================================
@auth.route('/logout')
@login_required  # On ne peut se déconnecter que si on est connecté
def logout():
    # Note TP3 (Exo 3) : logout_user() supprime l'identifiant stocké dans la session.
    # current_user redevient anonyme apres cet appel.
    logout_user()
    flash("Vous êtes déconnecté.", "info")
    return redirect(url_for('main.index'))
