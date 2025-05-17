SQLALCHEMY_DATABASE_URI = 'sqlite:///postechchallenge01.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False
JSON_AS_ASCII = False
SWAGGER = {
    'title': 'API Tech Challenge',
    'uiversion': 3
}
SECRET_KEY = 'chave-secreta'
CACHE_TYPE = 'simple'
JWT_SECRET_KEY = 'jwt-chave-secreta'
JWT_ACCESS_TOKEN_EXPIRES = 1800