import json
import logging
from flask import Flask, request#, render_template
from modules.database.db_config import db
from modules.database.functions import create_tables, register_data, execute_query, drop_tables
from modules.database.models import Producao, Processamento, Comercializacao, Importacao, Exportacao, Usuario
from modules.webscraping.webscraping import capturar_dados, capturar_anos, capturar_subopcoes
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required
)
from auth.jwt_handlers import configure_jwt_handlers  # importando os handlers de jwt personalizados

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

@app.route('/')
def home():
    return '🍇 API Vitibrasil Online'
    #return render_template('index.html')

@app.route('/register', methods=['POST'])
def register_user():
    data = request.get_json()
    if Usuario.query.filter_by(username=data['username']).first():
        return json.dumps({"error": "Usuario já existe"}), 400
    new_user = Usuario(username=data['username'], password=data['password'])
    db.session.add(new_user)
    db.session.commit()
    return json.dumps({"msg": "Usuario criado"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = Usuario.query.filter_by(username=data['username']).first()
    if user and user.password == data['password']:
        token = create_access_token(identity=str(user.id))
        return json.dumps({"acess_token": token}), 200
    return json.dumps({"error": "Credenciais invalidas"}), 201

@app.route('/dados', methods=['GET'])
@jwt_required()
def get_dados():
    opt = int(request.args.get("opcao"))
    logging.info(f"Requisição recebida para a opção: {opt}")
    valid_options = {2, 3, 4, 5, 6}
    if opt not in valid_options:
        return json.dumps({"erro": f"Opção inválida. Escolha uma das seguintes: 2, 3, 4, 5, 6."}, ensure_ascii=False), 400
    
    year = request.args.get("ano", type=int, default=2023)
    valid_year_start, valid_year_end = capturar_anos(opt, year)
    if (valid_year_start is None) | (valid_year_end is None):
        return json.dumps({"erro": "Ocorreu um erro ao tentar acessar o servidor. Por favor, tente novamente mais tarde."}, ensure_ascii=False), 400
    if (year < valid_year_start) | (year > valid_year_end):
        return json.dumps({"erro": f"Ano inválido. Escolha uma dos seguintes anos para essa opção: {str(valid_year_start)} - {str(valid_year_end)}."}, ensure_ascii=False), 400

    sub = None
    sub_value = None
    if opt in (3, 5, 6):
        try:
            sub = int(request.args.get("subopcao", default=1))
        except:
            return json.dumps({"erro": "Subopção inválida. Escolha um número inteiro."}, ensure_ascii=False), 400
        valid_suboptions = capturar_subopcoes(opt, sub)
        if valid_suboptions is None:
            return json.dumps({"erro": "Ocorreu um erro ao tentar acessar o servidor. Por favor, tente novamente mais tarde."}, ensure_ascii=False), 400
        if sub:
            valid_suboptions_keys = list(valid_suboptions.keys())
            sub_value = valid_suboptions.get(sub)
            if sub not in valid_suboptions_keys:
                return json.dumps({"erro": f"Subopção inválida. Escolha uma das seguintes subopções para essa opção: {', '.join(map(str, valid_suboptions))}."}, ensure_ascii=False), 400
            
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
        #return render_template("index.html", resultado=dados)
    
    except Exception as e:
        logging.error(f"Erro ao processar a requisição: {e}")
        return json.dumps({"erro": "Erro interno do servidor."}, ensure_ascii=False), 500


if __name__ == '__main__':
    app.run(debug=True)
