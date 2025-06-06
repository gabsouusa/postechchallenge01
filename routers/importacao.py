from flask import Blueprint
from flask_jwt_extended import jwt_required
from services.validators import validate_year, validate_suboption

from modules.database.db_config import db
from modules.database.models import Producao, Processamento, Comercializacao, Importacao, Exportacao, Usuario

from services.data_featcher import fetch_or_scrape_data

opcao_model_map = {
    2: Producao,
    3: Processamento,
    4: Comercializacao,
    5: Importacao,
    6: Exportacao,
}

importacao_bp = Blueprint('importacao', __name__)

@importacao_bp.route('/importacao', methods=['GET'])
@jwt_required()
def get_dados_opt5():
    """
    Lista os dados da página de Importação (opt_05)
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
      - in: query
        name: subopcao
        schema:
          type: integer
        required: false
        description: Filtra a subopção dos dados da página, se não for passada retorna a primeira subopção
        minimum: 1
        maximum: 5
        enum: [1, 2, 3, 4, 5]
    responses:
      200:
        description: Lista os dados da página de Importação (opt_05)
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
                  tipo:
                    type: string
                  pais:
                    type: string
                  quantidade_kg:
                    type: integer
                  valor_usd:
                    type: integer
                required:
                  - ano
                  - tipo
                  - pais
                  - quantidade_kg
                  - valor_usd
    """
    opt = 5
    year, error = validate_year(opt)
    if error:
        return error 
    sub, sub_value = validate_suboption(opt)

    return fetch_or_scrape_data(year, opt, db, opcao_model_map, sub, sub_value)