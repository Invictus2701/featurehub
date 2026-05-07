# app/api/routes.py - Le Blueprint qui expose notre API REST.
#
# Note TP4 (Exo 2) : une API REST permet a des programmes externes (apps mobiles,
# autres serveurs, scripts...) de communiquer avec FeatureHub. Au lieu de retourner
# des pages HTML, l'API retourne du JSON, un format de données universel.
#
# Note TP4 : ce blueprint est enregistré avec le préfixe /api/v1 dans __init__.py.
# Donc une route définie ici comme @api.route('/features') sera en réalité
# accessible a /api/v1/features. Le "/v1/" permet de versionner l'API.

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity

from ..models import db, FeatureRequest, User

api = Blueprint('api', __name__)


# ============================================================
# UTILITAIRE : RÉPONSES D'ERREUR EN JSON
# ============================================================
def make_error(status_code, message, field=None):
    """Note TP4 (Exo 2) : helper pour retourner des erreurs cohérentes en JSON.

    Pourquoi ? Parce qu'un client d'API a besoin de réponses TOUJOURS en JSON,
    meme quand il y a une erreur. Sans cette fonction, Flask renverait une page
    HTML par défaut quand quelque chose plante - ce qui ferait crasher le client.
    """
    response = {'error': message, 'code': status_code}
    if field:
        response['field'] = field  # Optionel : nom du champ qui pose problème
    return jsonify(response), status_code


# ============================================================
# AUTHENTIFICATION : OBTENIR UN TOKEN JWT (Exo 5)
# ============================================================
@api.route('/auth/token', methods=['POST'])
def get_token():
    """Note TP4 (Exo 5) : route d'authentification pour les clients de l'API.

    Le client envoie son username/password en JSON, on verifie, et si tout est OK
    on lui retourne un TOKEN JWT. Il devra ensuite l'inclure dans l'entete
    "Authorization: Bearer <token>" de toutes ses futures requetes.

    Note TP4 : pourquoi JWT et pas Flask-Login (cookies) ?
    - REST est "stateless" : le serveur ne devrait rien retenir entre 2 requetes.
    - Les cookies HTTP sont liés a un domaine et a un navigateur, ce qui limite
      l'usage cross-platform (apps mobiles, scripts...).
    - Le token JWT est totalement portable : un script Python ou une app Android
      peut s'en servir aussi facilement qu'un navigateur.
    """
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return make_error(400, "Username et password requis")

    # Note TP4 : on cherche l'user et on vérifie le password (comme dans auth/routes.py).
    # On utilise check_password() (méthode du modèle) pour rester cohérent avec le TP3.
    user = User.query.filter_by(username=username).first()
    if user is None or not user.check_password(password):
        # Note TP4 : 401 Unauthorized = "qui es-tu ?" (auth manquante ou invalide)
        return make_error(401, "Identifiants invalides")

    # Note TP4 : on crée le token. "identity" sera le contenu du token, ici le username.
    # Plus tard, get_jwt_identity() permettra de retrouver ce username dans les routes
    # protégées. On évite de stoquer l'id (qui pourrait changer) au profit du username.
    token = create_access_token(identity=username)
    return jsonify(access_token=token), 200


# ============================================================
# LECTURE : LISTE DES DEMANDES (Exo 2)
# ============================================================
@api.route('/features', methods=['GET'])
def get_features():
    """Note TP4 (Exo 2) : GET /api/v1/features
    Retourne la liste des demandes en JSON, avec filtrage, tri et pagination.

    Exemples d'URLs :
    - /api/v1/features                            (toutes les demandes)
    - /api/v1/features?nature=Bug                 (uniquement les bugs)
    - /api/v1/features?status=Validé&page=2       (les validées, page 2)
    - /api/v1/features?sort=title&order=asc       (triées par titre A-Z)
    """
    # ---------- Filtrage ----------
    nature = request.args.get('nature')
    status = request.args.get('status')
    priority = request.args.get('priority')

    # ---------- Tri ----------
    sort = request.args.get('sort', 'created_at')   # colonne par défaut
    order = request.args.get('order', 'desc')       # sens par défaut (descendant)

    # ---------- Pagination ----------
    # type=int convertit automatiquement le paramètre en entier (avec défaut)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    # On part d'une requete vide et on rajoute les filtres "en chaine"
    query = FeatureRequest.query
    if nature:
        query = query.filter_by(nature=nature)
    if status:
        query = query.filter_by(status=status)
    if priority:
        query = query.filter_by(priority=priority)

    # Note TP4 : tri dynamique. getattr(...) récupère la colonne par son nom.
    # Si le client demande un nom de colonne qui n'existe pas, on retombe sur
    # la valeur par défaut (created_at).
    column = getattr(FeatureRequest, sort, FeatureRequest.created_at)
    query = query.order_by(column.desc() if order == 'desc' else column.asc())

    # Note TP4 : .paginate() est fourni par Flask-SQLAlchemy. Il découpe les résultats
    # en pages, ce qui evite de renvoyer 10 000 demandes d'un coup au client.
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    # On construit la réponse JSON avec les meta-données utiles au client
    return jsonify({
        'total': pagination.total,        # nb total de demandes
        'page': pagination.page,          # page actuelle
        'pages': pagination.pages,        # nb total de pages
        'per_page': pagination.per_page,  # nb d'items par page
        'data': [f.to_dict() for f in pagination.items],  # les demandes elles-memes
    })


# ============================================================
# LECTURE : DETAIL D'UNE DEMANDE (Exo 2)
# ============================================================
@api.route('/features/<int:id>', methods=['GET'])
def get_feature(id):
    """Note TP4 (Exo 2) : GET /api/v1/features/<id>
    Retourne une seule demande, ou 404 si elle n'existe pas.
    """
    feature = FeatureRequest.query.get(id)
    if feature is None:
        return make_error(404, "Demande introuvable")
    return jsonify(feature.to_dict())


# ============================================================
# CREATION (Exo 3 + JWT en Exo 5)
# ============================================================
@api.route('/features', methods=['POST'])
@jwt_required()  # Note TP4 (Exo 5) : seuls les clients avec un token JWT valide peuvent créer
def create_feature():
    """Note TP4 (Exo 3) : POST /api/v1/features
    Crée une nouvelle demande a partir des données JSON envoyées par le client.

    Réponse : 201 Created (le code standard pour "ressource créée avec succès").
    """
    # Note TP4 : get_jwt_identity() récupère ce qu'on a mis dans le token (le username).
    # On retrouve ensuite l'user en base pour avoir son id (et le mettre comme author).
    current_username = get_jwt_identity()
    user = User.query.filter_by(username=current_username).first()
    if user is None:
        # Cas tres improbable : token valide mais user supprimé. On refuse quand meme.
        return make_error(401, "Utilisateur du token introuvable")

    # Note TP4 : request.get_json() lit le corps de la requete et le parse en dict Python.
    # Le "or {}" permet d'avoir un dict vide si le client envoie rien (au lieu de None).
    data = request.get_json() or {}

    if not data.get('title'):
        # Note TP4 : 400 Bad Request = "ta requete est mal formée"
        return make_error(400, "Le titre est requis", field='title')

    feature = FeatureRequest(
        title=data['title'],
        description=data.get('description', ''),
        nature=data.get('nature', 'Feature'),
        priority=data.get('priority', 'Moyenne'),
        status='En attente',  # toujours "En attente" a la création
        author_id=user.id,    # Note TP4 (Exo 5) : auteur déduit du token JWT
    )
    db.session.add(feature)
    db.session.commit()

    # Note TP4 : 201 = "Created", code spécifique pour signaler une création réussie
    return jsonify(feature.to_dict()), 201


# ============================================================
# MODIFICATION TOTALE (PUT) - Exo 4
# ============================================================
@api.route('/features/<int:id>', methods=['PUT'])
@jwt_required()
def update_feature_put(id):
    """Note TP4 (Exo 4) : PUT /api/v1/features/<id>
    REMPLACE ENTIEREMENT la ressource. Tout champ non fourni revient a sa
    valeur par défaut. C'est comme si on supprimait l'ancienne et qu'on créait
    une nouvelle demande avec le meme id.
    """
    feature = FeatureRequest.query.get(id)
    if feature is None:
        return make_error(404, "Demande introuvable")

    data = request.get_json() or {}
    if not data.get('title'):
        return make_error(400, "Le titre est requis pour un remplacement complet", field='title')

    # Note TP4 : on assigne MEME les champs absents → ils prennent leur valeur par défaut.
    # C'est ce qui differencie PUT de PATCH.
    feature.title = data['title']
    feature.description = data.get('description', '')
    feature.nature = data.get('nature', 'Feature')
    feature.priority = data.get('priority', 'Moyenne')
    feature.status = data.get('status', 'En attente')

    db.session.commit()
    return jsonify(feature.to_dict())


# ============================================================
# MODIFICATION PARTIELLE (PATCH) - Exo 4
# ============================================================
@api.route('/features/<int:id>', methods=['PATCH'])
@jwt_required()
def update_feature_patch(id):
    """Note TP4 (Exo 4) : PATCH /api/v1/features/<id>
    Modifie UNIQUEMENT les champs fournis. Les autres restent inchangés.

    Exemple : si le client envoie juste {"status": "Validé"}, on change que ça,
    le titre et la description sont gardés intactes.

    C'est tres pratique car le client n'a pas besoin de renvoyer toute la ressource.
    """
    feature = FeatureRequest.query.get(id)
    if feature is None:
        return make_error(404, "Demande introuvable")

    data = request.get_json() or {}

    # Note TP4 : "if 'xxx' in data" verifie si la clé EXISTE dans le JSON envoyé.
    # Tres different de "if data.get('xxx')" : le get retourne None si absent
    # OU si la valeur est vide. Avec PATCH on veut pouvoir "vider" un champ
    # (description = "") en l'envoyant explicitement.
    if 'title' in data:
        feature.title = data['title']
    if 'description' in data:
        feature.description = data['description']
    if 'nature' in data:
        feature.nature = data['nature']
    if 'priority' in data:
        feature.priority = data['priority']
    if 'status' in data:
        feature.status = data['status']

    db.session.commit()
    return jsonify(feature.to_dict())


# ============================================================
# SUPPRESSION (DELETE) - Exo 5
# ============================================================
@api.route('/features/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_feature(id):
    """Note TP4 (Exo 5) : DELETE /api/v1/features/<id>

    Supprime la ressource. On retourne 204 No Content (succes sans body).

    Note TP4 : pourquoi 204 et pas 200 ?
    Le code 200 implique qu'il y a un corps de réponse. Apres une suppression,
    il n'y a plus rien a retourner — donc 204 ("succes, mais pas de contenu")
    est le code semantiquement correct.
    """
    feature = FeatureRequest.query.get(id)
    if feature is None:
        return make_error(404, "Demande introuvable")

    db.session.delete(feature)
    db.session.commit()

    # Note TP4 : on retourne une chaine vide + le code 204 (pas de body)
    return '', 204
