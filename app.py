from flask import Flask, request
from webscraping.webscraping import capturar_dados, capturar_anos, capturar_subopcoes
import logging
import json

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Simulação de base de dados em memória
dados_memoria = []

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
    
    valid_year_start, valid_year_end = capturar_anos(opt)
    year = request.args.get("ano", type=int, default=valid_year_end)
    if (valid_year_start is None) | (valid_year_end is None):
        return json.dumps({"erro": "Ocorreu um erro ao tentar acessar o servidor. Por favor, tente novamente mais tarde."}, ensure_ascii=False), 400
    if (year < valid_year_start) | (year > valid_year_end):
        return json.dumps({"erro": f"Ano inválido. Escolha uma dos seguintes anos para essa opção: {str(valid_year_start)} - {str(valid_year_end)}."}, ensure_ascii=False), 400

    sub = None
    if opt in ('opt_03', 'opt_05', 'opt_06'):
        valid_suboptions = capturar_subopcoes(opt)
        sub = request.args.get("subopcao", default='subopt_01')
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
        dados = capturar_dados(opt, year, sub)
        if not dados:
            return json.dumps({"mensagem": "Nenhum dado encontrado para esta opção."}, ensure_ascii=False), 404

        return json.dumps(dados, ensure_ascii=False, indent=2), 200
    except Exception as e:
        logging.error(f"Erro ao processar a requisição: {e}")
        return json.dumps({"erro": "Erro interno do servidor."}, ensure_ascii=False), 500

# # POST - Adiciona novo dado manualmente
# @app.route('/dados', methods=['POST'])
# def adicionar_dado():
#     novo_dado = request.get_json()
#     if not novo_dado:
#         return json.dumps({"erro": "Dados ausentes no corpo da requisição."}, ensure_ascii=False), 400

#     dados_memoria.append(novo_dado)
#     return json.dumps({"mensagem": "Dado adicionado com sucesso.", "dado": novo_dado}, ensure_ascii=False), 201

# # PUT - Atualiza dado existente baseado no índice
# @app.route('/dados/<int:indice>', methods=['PUT'])
# def atualizar_dado(indice):
#     if indice >= len(dados_memoria):
#         return json.dumps({"erro": "Índice não encontrado."}, ensure_ascii=False), 404

#     dado_atualizado = request.get_json()
#     dados_memoria[indice] = dado_atualizado
#     return json.dumps({"mensagem": "Dado atualizado com sucesso.", "dado": dado_atualizado}, ensure_ascii=False), 200

# # DELETE - Remove dado baseado no índice
# @app.route('/dados/<int:indice>', methods=['DELETE'])
# def deletar_dado(indice):
#     if indice >= len(dados_memoria):
#         return json.dumps({"erro": "Índice não encontrado."}, ensure_ascii=False), 404

#     removido = dados_memoria.pop(indice)
#     return json.dumps({"mensagem": "Dado removido com sucesso.", "dado": removido}, ensure_ascii=False), 200

if __name__ == '__main__':
    app.run(debug=True)
