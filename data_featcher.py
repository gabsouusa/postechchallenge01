import json
import logging
from modules.database.functions import execute_query, register_data
from modules.webscraping.webscraping import capturar_dados

def fetch_or_scrape_data(year, opt, db, opcao_model_map, sub=None, sub_value=None):
    """
    Busca dados no banco de dados ou realiza scraping caso os dados não estejam disponíveis.

    Esta função tenta recuperar dados do banco de dados com base nos parâmetros fornecidos.
    Caso os dados não estejam presentes, inicia o processo de web scraping para capturá-los
    da fonte externa. Se obtidos com sucesso, os dados são registrados no banco e retornados.

    Parâmetros:
    - year (int): Ano dos dados a serem buscados.
    - opt (int): Código da opção (2 a 6), utilizado para identificar o modelo da tabela correspondente.
    - db (SQLAlchemy): Instância do banco de dados para realizar queries e registrar dados.
    - opcao_model_map (dict): Mapeamento de opções para modelos de banco de dados.
    - sub (str, opcional): Código da subopção, caso aplicável.
    - sub_value (int, opcional): Nome da subopção, caso aplicável.

    Retorno:
    - tuple: Uma tupla contendo os dados em formato JSON e o código de status HTTP correspondente.
             Pode ser (dados_json, 200), (mensagem_erro, 404), ou (mensagem_erro, 500).
    """
    try:
        dados = execute_query(year, opt, sub, sub_value, opcao_model_map)

        if not dados:
            logging.info("Dado não encontrado no banco de dados. Iniciando scraping...")
            dados = capturar_dados(opt, year, sub)

            if isinstance(dados, tuple) and isinstance(dados[0], dict) and "erro" in dados[0]:
                return json.dumps(dados[0], ensure_ascii=False), dados[1]

            if not dados:
                return json.dumps({
                    "mensagem": "Nenhum dado encontrado para esta opção."
                }, ensure_ascii=False), 404

            logging.info("Escrevendo dado no banco de dados...")
            register_data(db, dados, opt, opcao_model_map)
            logging.info("Banco de dados atualizado com sucesso.")

        return json.dumps(dados, ensure_ascii=False, indent=2), 200

    except Exception as e:
        logging.exception("Erro ao processar a requisição:")
        return json.dumps({
            "erro": "Erro interno do servidor."
        }, ensure_ascii=False), 500
