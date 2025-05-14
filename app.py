import json
import logging
from flask import Flask, request
from db_config import db
from models import Wine
from webscraping.webscraping import capturar_dados, capturar_anos, capturar_subopcoes

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config.from_object('config')
db.init_app(app)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def create_tables():
    with app.app_context():
        # Caso queira apagar a tabela e criar novamente, descomente a linha abaixo
        # Wine.__table__.drop(db.engine)
        db.create_all()
create_tables()


def register_data(data, opt, sub):
    """
    Cria uma nova receita
    """
    registros = [
        Wine(
            ano=item.get('ano'),
            produto=item.get('produto', opt),
            subproduto=item.get('subproduto', sub),
            tipo=item.get('tipo'),
            quantidade_lt=item.get('quantidade_lt'),
            quantidade_kg=item.get('quantidade_kg'),
            cultivar=item.get('cultivar'),
            pais=item.get('pais'),
            valor_usd=item.get('valor_usd')
        )
        for item in data
    ]
    db.session.add_all(registros)
    db.session.commit()


@app.route('/')
def home():
    return '🍇 API Vitibrasil Online'


@app.route('/dados', methods=['GET'])
def get_dados():
    opt = request.args.get("opcao")
    logging.info(f"Requisição recebida para a opção: {opt}")
    valid_options = {'opt_02', 'opt_03', 'opt_04', 'opt_05', 'opt_06'}
    if opt not in valid_options:
        return json.dumps({"erro": f"Opção inválida. Escolha uma das seguintes: {', '.join(valid_options)}."}, ensure_ascii=False), 400
    
    year = request.args.get("ano", type=int, default=2023)
    valid_year_start, valid_year_end = capturar_anos(opt, year)
    if (valid_year_start is None) | (valid_year_end is None):
        return json.dumps({"erro": "Ocorreu um erro ao tentar acessar o servidor. Por favor, tente novamente mais tarde."}, ensure_ascii=False), 400
    if (year < valid_year_start) | (year > valid_year_end):
        return json.dumps({"erro": f"Ano inválido. Escolha uma dos seguintes anos para essa opção: {str(valid_year_start)} - {str(valid_year_end)}."}, ensure_ascii=False), 400

    sub = None
    if opt in ('opt_03', 'opt_05', 'opt_06'):
        sub = request.args.get("subopcao", default='subopt_01')
        valid_suboptions = capturar_subopcoes(opt, sub)
        if valid_suboptions is None:
            return json.dumps({"erro": "Ocorreu um erro ao tentar acessar o servidor. Por favor, tente novamente mais tarde."}, ensure_ascii=False), 400
        if sub:
            valid_suboptions_keys = list(valid_suboptions.keys())
            valid_suboptions_values = list(valid_suboptions.values())

            sub_normalized = sub.lower()
            valid_options_normalized = [v.lower() for v in valid_suboptions_keys + valid_suboptions_values]

            if sub_normalized not in valid_options_normalized:
                return json.dumps({"erro": f"Subopção inválida. Escolha uma das seguintes subopções para essa opção: {', '.join(valid_suboptions)}."}, ensure_ascii=False), 400
            
    try:
        filters = [Wine.produto == opt]
        filters.append(Wine.ano == (year if year is not None else 2023))
        if sub:
            filters.append(Wine.subproduto == sub)
        logging.info(f"Filtros aplicados: {filters}")
        query = Wine.query.filter(*filters)
        if query.count() == 0:
            logging.info("Dado não encontrado no banco de dados. Iniciando scraping...")
            dados = capturar_dados(opt, year, sub)
            if not dados:
                return json.dumps({"mensagem": "Nenhum dado encontrado para esta opção."}, ensure_ascii=False), 404
            logging.info("Escrevendo dado no banco de dados...")
            register_data(dados, opt, sub)
            logging.info("Banco de dados atualizado com sucesso.")
        else:
            dados = []
            for row in query.all():
                row_data = {}
                for column in Wine.__table__.columns:  
                    row_data[column.name] = getattr(row, column.name)  
                dados.append(row_data)
            logging.info("Retornando dado do banco.")
        if not dados:
            return json.dumps({"mensagem": "Nenhum dado encontrado para esta opção."}, ensure_ascii=False), 404
        
        return json.dumps(dados, ensure_ascii=False, indent=2), 200
    
    except Exception as e:
        logging.error(f"Erro ao processar a requisição: {e}")
        return json.dumps({"erro": "Erro interno do servidor."}, ensure_ascii=False), 500


if __name__ == '__main__':
    app.run(debug=True)
