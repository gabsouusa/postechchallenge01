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

swagger = Swagger(app)

def fetch_or_scrape_data(year, opt, db, opcao_model_map, sub=None, sub_value=None):
    try:
        dados = execute_query(year, opt, sub, sub_value, opcao_model_map)

        if dados is None:
            logging.info("Dado não encontrado no banco de dados. Iniciando scraping...")
            dados = capturar_dados(opt, year, sub)

            if not dados:
                return json.dumps({"mensagem": "Nenhum dado encontrado para esta opção."}, ensure_ascii=False), 404

            logging.info("Escrevendo dado no banco de dados...")
            register_data(db, dados, opt, opcao_model_map)
            logging.info("Banco de dados atualizado com sucesso.")

        if not dados:
            return json.dumps({"mensagem": "Nenhum dado encontrado para esta opção."}, ensure_ascii=False), 404

        return json.dumps(dados, ensure_ascii=False, indent=2), 200

    except Exception as e:
        logging.error(f"Erro ao processar a requisição: {e}")
        return json.dumps({"erro": "Erro interno do servidor."}, ensure_ascii=False), 500


@app.route('/')
def home():
    return '🍇 API Vitibrasil Online'
    #return render_template('index.html')

@app.route('/register', methods=['POST'])
def register_user():
    """
    Registra um novo usuario
    ---
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
            description: Usuario criado com sucesso
        400:
            description: Usuario ja existe
    """
    data = request.get_json()
    if Usuario.query.filter_by(username=data['username']).first():
        return json.dumps({"error": "Usuario já existe"}), 400
    new_user = Usuario(username=data['username'], password=data['password'])
    db.session.add(new_user)
    db.session.commit()
    return json.dumps({"msg": "Usuario criado"}), 201

@app.route('/login', methods=['POST'])
def login():
    """
    Faz login do usuario e retorna um JWT
    ---
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
            description: Credenciais invalidas
    """
    data = request.get_json()
    user = Usuario.query.filter_by(username=data['username']).first()
    if user and user.password == data['password']:
        token = create_access_token(identity=str(user.id))
        return json.dumps({"acess_token": token}), 200
    return json.dumps({"error": "Credenciais invalidas"}), 201


@app.route('/producao', methods=['GET'])
@jwt_required()
def get_dados_opt2():
    """
    Lista os dados da pagina opt_02
    ---
    security:
        - BaererAuth: []
    parameters:
        - in: query
          name: opcao
          type: int
          required: true
          description: Filtra a opcao da pagina
        - in: query
          name: ano
          type: integer
          required: false
          description: Filtra o ano dos dados da pagina, se nao for passado retorna o ano mais recente disponivel
        - in: query
          name: subopcao
          type: int
          required: false
          description: Filtra a sub opcao da pagina caso tenha disponivel
    responses:
        200:
            description: Lista os dados da pagina
            schema:
                type: array
                items:
                    type: object
                    properties:
                        id:
                            type: integer
                        ano:
                            type: integer
                        produto:
                            type: string
                        subproduto:
                            type: string
                        quantidade_lt:
                            type: integer
    """
    opt = 2
    year = validate_year(opt)

    return fetch_or_scrape_data(year, opt, db, opcao_model_map)
    
@app.route('/processamento', methods=['GET'])
@jwt_required()
def get_dados_opt3():
    opt = 3
    year = validate_year(opt)
    sub, sub_value = validate_suboption(opt)

    return fetch_or_scrape_data(year, opt, db, opcao_model_map, sub, sub_value)

@app.route('/comercializacao', methods=['GET'])
@jwt_required()
def get_dados_opt4():
    opt = 4
    year = validate_year(opt)

    return fetch_or_scrape_data(year, opt, db, opcao_model_map)

@app.route('/importacao', methods=['GET'])
@jwt_required()
def get_dados_opt5():
    opt = 5
    year = validate_year(opt)
    sub, sub_value = validate_suboption(opt)

    return fetch_or_scrape_data(year, opt, db, opcao_model_map, sub, sub_value)

@app.route('/exportacao', methods=['GET'])
@jwt_required()
def get_dados_opt6():
    opt = 6
    year = validate_year(opt)
    sub, sub_value = validate_suboption(opt)

    return fetch_or_scrape_data(year, opt, db, opcao_model_map, sub, sub_value)


if __name__ == '__main__':
    app.run(debug=True)
