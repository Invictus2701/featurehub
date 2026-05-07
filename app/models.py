# app/models.py - Tous les modèles de données de l'application.
#
# Note TP3 (Exo 1) : dans le pattern MVC, c'est le "M" (Model). Ce fichier
# contient les classes Python qui représentent les tables de la base de données.
# Chaque classe = une table, chaque instance = une ligne.
#
# Note TP3 (Exo 1) : on crée db = SQLAlchemy() SANS lui passer "app" en argument.
# C'est crucial : ca permet d'éviter les imports circulaires entre __init__.py
# et models.py. La liaison avec l'app sera faite plus tard via db.init_app(app).

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# Instance "vide" de SQLAlchemy. Elle sera "branchée" sur l'app dans __init__.py.
db = SQLAlchemy()


# ============================================================
# MODELE USER (Exo 2)
# ============================================================
class User(UserMixin, db.Model):
    """Note TP3 (Exo 2) : représente un utilisateur du site.

    On hérite de DEUX classes :
    - UserMixin : fournit GRATUITEMENT les 4 méthodes/propriétés que Flask-Login
      attend sur un user (is_authenticated, is_active, is_anonymous, get_id).
      Sans elle on devrait les écrire a la main.
    - db.Model : permet a SQLAlchemy de transformer cette classe en table SQL.
    """
    # Pas de __tablename__ explicite : SQLAlchemy va deduire "user" tout seul.
    # On garde ce nom car la ForeignKey de FeatureRequest pointe vers 'user.id'.

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    # Note TP3 : on stoque uniquement le HASH du mot de passe, JAMAIS le mot de passe en clair.
    # 256 caracteres : large car les hashs modernes (pbkdf2:sha256:...) sont longs.
    password_hash = db.Column(db.String(256))

    # Note TP3 (Exo 5) : relation One-to-Many (1:N) avec FeatureRequest.
    # - 'FeatureRequest' : nom de la classe liée (en string car elle est definie plus bas)
    # - backref='author' : ajoute AUTOMATIQUEMENT un attribut .author sur chaque
    #   FeatureRequest, qui pointera vers le User propriétaire. Tres pratique !
    # - lazy=True : SQLAlchemy charge la liste des features uniquement quand on y accède
    #   (evite de charger des données inutilement).
    features = db.relationship('FeatureRequest', backref='author', lazy=True)

    # ---------- Méthodes utilitaires pour le mot de passe ----------

    def set_password(self, password):
        """Note TP3 (Exo 2) : prend un mot de passe en clair et le transforme
        en hash sécurisé avant de le stocker. generate_password_hash ajoute
        automatiquement un "sel" aléatoire pour rendre le hash unique.
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Note TP3 (Exo 2) : verifie qu'un mot de passe donné correspond au hash stocké.
        Retourne True si OK, False sinon. On ne dechiffre jamais le hash : on hash a
        nouveau le mot de passe fourni avec le meme sel et on compare les deux hashs.
        """
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        # Sert au debogage quand on print() un User dans la console
        return f'<User {self.id}: {self.username}>'


# ============================================================
# MODELE FEATUREREQUEST (mis à jour pour TP3 Exo 5)
# ============================================================
class FeatureRequest(db.Model):
    """Représente une demande de fonctionalité, un bug ou une amélioration."""

    __tablename__ = 'feature_requests'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='En attente')
    nature = db.Column(db.String(20), default='Feature')
    priority = db.Column(db.String(20), default='Moyenne')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    filename = db.Column(db.String(255), nullable=True)

    # Note TP3 (Exo 5) : clé étrangère vers la table user.
    # - 'user.id' : nom_de_table.nom_de_colonne (en SQL).
    # - nullable=True : on tolere des demandes sans auteur (ex. demandes
    #   importées avant la mise en place de l'authentification).
    # Cette ligne crée AUSSI virtuellement un attribut .author sur cet objet
    # grace au backref défini dans la classe User ci-dessus.
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    def __repr__(self):
        return f'<FeatureRequest {self.id}: {self.title}>'
