# routers/auth.py
from flask import Blueprint, request
from flask_jwt_extended import create_access_token
from modules.database.models import Usuario
from modules.database.db_config import db
import json

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register_user():
    """
    Registra um novo usuário
    ---
    tags:
      - Autenticação
    parameters:
        - in: body
          name: body
          required: true
          schema:
            type: object
            properties:
                username:
                    type: string
                password:
                    type: string
    responses:
        201:
            description: Usuário criado com sucesso
        400:
            description: Usuário já existe
    """
    data = request.get_json()
    if Usuario.query.filter_by(username=data['username']).first():
        return json.dumps({"error": "Usuário já existe"}), 400
    new_user = Usuario(username=data['username'], password=data['password'])
    db.session.add(new_user)
    db.session.commit()
    return json.dumps({"msg": "Usuário criado"}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Faz login do usuário e retorna um JWT
    ---
    tags:
      - Autenticação
    parameters:
        - in: body
          name: body
          required: true
          schema:
            type: object
            properties:
                username:
                    type: string
                password:
                    type: string
    responses:
        201:
            description: Login bem sucedido, retorna JWT
        400:
            description: Credenciais inválidas
    """
    data = request.get_json()
    user = Usuario.query.filter_by(username=data['username']).first()
    if user and user.password == data['password']:
        token = create_access_token(identity=str(user.id))
        return json.dumps({"acess_token": token}), 200
    return json.dumps({"error": "Credenciais inválidas"}), 400
