import json
import logging
from flask import Flask, request#, render_template
from validators import validate_year, validate_suboption
from modules.database.db_config import db
from modules.database.functions import create_tables, register_data, execute_query, drop_tables
from modules.database.models import Producao, Processamento, Comercializacao, Importacao, Exportacao, Usuario
from modules.webscraping.webscraping import capturar_dados
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required
)
from auth.jwt_handlers import configure_jwt_handlers  # importando os handlers de jwt personalizados
from flasgger import Swagger
from config import SWAGGER_TEMPLATE

from data_service import fetch_or_scrape_data

from routers.producao import producao_bp
from routers.processamento import processamento_bp
from routers.comercializacao import comercializacao_bp
from routers.importacao import importacao_bp
from routers.exportacao import exportacao_bp
from routers.auth import auth_bp

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
app.config.from_object('config')

opcao_model_map = {
    2: Producao,
    3: Processamento,
    4: Comercializacao,
    5: Importacao,
    6: Exportacao,
}
db.init_app(app)
create_tables(app, db)
# Caso queira apagar a tabela e criar novamente, descomente a linha abaixo
# drop_tables(app, db)

jwt = JWTManager(app)
configure_jwt_handlers(app, jwt)

swagger = Swagger(app, template=SWAGGER_TEMPLATE)

app.register_blueprint(producao_bp)
app.register_blueprint(processamento_bp)
app.register_blueprint(comercializacao_bp)
app.register_blueprint(importacao_bp)
app.register_blueprint(exportacao_bp)
app.register_blueprint(auth_bp)

@app.route('/')
def home():
    return '🍇 API Vitibrasil Online'
    #return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
