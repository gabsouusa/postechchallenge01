SQLALCHEMY_DATABASE_URI = 'sqlite:///postechchallenge01.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False
JSON_AS_ASCII = False
SWAGGER = {
    'title': '🍇 API Vitibrasil',
    'uiversion': 3
}
SWAGGER_TEMPLATE = {
    "swagger": "2.0",
    "info": {
        "title": "🍇 API Vitibrasil",
        "description": "API com autenticação JWT usando Bearer token.",
        "version": "1.0.0"
    },
    "securityDefinitions": {
        "BearerAuth": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT Authorization header using the Bearer scheme. Example: 'Bearer {token}'"
        }
    }
}
SECRET_KEY = 'chave-secreta'
CACHE_TYPE = 'simple'
JWT_SECRET_KEY = 'jwt-chave-secreta'
JWT_ACCESS_TOKEN_EXPIRES = 1800