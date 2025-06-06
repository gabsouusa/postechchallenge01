import json
from modules.webscraping.webscraping import capturar_anos, capturar_subopcoes
from flask import request

def validate_year(opt):
    """
    Valida o parâmetro de ano fornecido na query da requisição.

    Retorna:
    - (int, None): ano validado com sucesso.
    - (None, tuple): erro no formato (mensagem_json, status_http)
    """
    ano_str = request.args.get("ano")

    if ano_str is not None:
        try:
            year = int(ano_str)
        except ValueError:
            return None, (json.dumps({
                "erro": "O valor do parâmetro 'ano' deve ser um número inteiro."
            }, ensure_ascii=False), 400)
    else:
        year = 2023 if opt in {2, 3, 4} else 2024

    valid_year_start, valid_year_end = capturar_anos(opt, year)
    if valid_year_start is None or valid_year_end is None:
        return None, (json.dumps({
            "erro": "Ocorreu um erro ao tentar acessar o servidor. Por favor, tente novamente mais tarde."
        }, ensure_ascii=False), 400)

    if year < valid_year_start or year > valid_year_end:
        return None, (json.dumps({
            "erro": f"Ano inválido. Escolha um dos seguintes anos para essa opção: {valid_year_start} - {valid_year_end}."
        }, ensure_ascii=False), 400)

    return year, None

def validate_suboption(opt):
    """
    Valida a subopção fornecida na query string com base na opção selecionada.

    Parâmetros:
    - opt (int): Código da opção principal (por exemplo, 3, 5 ou 6), que define se a subopção é necessária.

    Retorno:
    - tuple:
        - sub (int or None): Número da subopção validada, ou None se não aplicável.
        - sub_value (str or None): Valor associado à subopção, ou None se não aplicável.

    Retorno em caso de erro:
    - tuple: Em caso de erro, retorna uma tupla contendo uma mensagem JSON de erro e
             o código de status HTTP 400. Os erros possíveis incluem:
        - subopção não numérica
        - erro ao acessar o servidor para obter subopções
        - subopção fora do intervalo permitido
    """
    sub = None
    sub_value = None
    if opt in (3, 5, 6):
        try:
            sub = int(request.args.get("subopcao", default=1))
        except:
            return json.dumps({
                "erro": "Subopção inválida. Escolha um número inteiro."
            }, ensure_ascii=False), 400

        valid_suboptions = capturar_subopcoes(opt, sub)
        if valid_suboptions is None:
            return json.dumps({
                "erro": "Ocorreu um erro ao tentar acessar o servidor. Por favor, tente novamente mais tarde."
            }, ensure_ascii=False), 400

        valid_suboptions_keys = list(valid_suboptions.keys())
        sub_value = valid_suboptions.get(sub)

        if sub not in valid_suboptions_keys:
            return json.dumps({
                "erro": f"Subopção inválida. Escolha uma das seguintes subopções para essa opção: {', '.join(map(str, valid_suboptions))}."
            }, ensure_ascii=False), 400
            
    return sub, sub_value
