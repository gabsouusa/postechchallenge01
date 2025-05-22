from flask import Blueprint
from flask_jwt_extended import jwt_required
from validators import validate_year

from modules.database.db_config import db
from modules.database.models import Producao, Processamento, Comercializacao, Importacao, Exportacao, Usuario

from data_service import fetch_or_scrape_data

opcao_model_map = {
    2: Producao,
    3: Processamento,
    4: Comercializacao,
    5: Importacao,
    6: Exportacao,
}

producao_bp = Blueprint('producao', __name__)

@producao_bp.route('/producao', methods=['GET'])
@jwt_required()
def get_dados_opt2():
    """
    Lista os dados da página de Produção (opt_02)
    ---
    tags:
      - Dados
    security:
      - BearerAuth: []
    parameters:
      - in: query
        name: ano
        schema:
          type: integer
        required: false
        description: Filtra o ano dos dados da página, se não for passado retorna o ano mais recente disponível
    responses:
      200:
        description: Lista os dados da página de Produção (opt_02)
        content:
          application/json:
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
                required:
                  - ano
                  - produto
                  - subproduto
                  - quantidade_lt
    """
    opt = 2
    year, error = validate_year(opt)
    if error:
        return error 
    return fetch_or_scrape_data(year, opt, db, opcao_model_map)