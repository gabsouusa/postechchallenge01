from flask import jsonify
from flask_jwt_extended import JWTManager

def configure_jwt_handlers(app, jwt: JWTManager):
    # Token ausente ou sem autorização
    @jwt.unauthorized_loader
    def custom_missing_token_callback(reason):
        return jsonify(error="Token de acesso ausente ou inválido", detalhe=reason), 401

    # Token inválido
    @jwt.invalid_token_loader
    def custom_invalid_token_callback(reason):
        return jsonify(error="Token inválido", detalhe=reason), 401

    # Token expirado
    @jwt.expired_token_loader
    def custom_expired_token_callback(jwt_header, jwt_payload):
        return jsonify(error="Token expirado", detalhe="Faça login novamente"), 401

    # Token revogado
    @jwt.revoked_token_loader
    def custom_revoked_token_callback(jwt_header, jwt_payload):
        return jsonify(error="Token revogado", detalhe="Esse token não pode mais ser usado"), 401
