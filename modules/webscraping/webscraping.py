import re
import time
import logging
import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)

base_url = 'http://vitibrasil.cnpuv.embrapa.br/index.php'
default_year = 2023

def capturar_anos(opcao, ano):
        if opcao == 2 or opcao == 3 or opcao == 4:
            min_ano, max_ano = 1970, 2023
        elif opcao == 5 or opcao == 6:
            min_ano, max_ano = 1970, 2024
        else:
            logging.error(f"Opção {opcao} não é suportada.")
            return None, None
        
        if ano < min_ano or ano > max_ano:
            url = f'{base_url}?ano={ano}&opcao=opt_0{opcao}'
            try:
                response = requests.get(url)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser', from_encoding=response.encoding)

                label_ano = soup.find('label', class_='lbl_pesq')
                if label_ano:
                    texto = label_ano.get_text(strip=True)
                    anos = re.findall(r'\[(\d{4})-(\d{4})\]', texto)
                    if anos:
                        return map(int, anos[0])
                return None, None
            except requests.exceptions.RequestException as e:
                logging.error(f"Erro ao acessar {url}: {e}")
                return None, None
            
        return min_ano, max_ano

def capturar_subopcoes(opcao, sub):
    if opcao == 3:
        subopcoes = {
            1: 'Vinífetas',
            2: 'Americanas E Híbridas',
            3: 'Uvas De Mesa',
            4: 'Sem Classificação'
        } 
    elif opcao == 5:
        subopcoes = {
            1: 'Vinhos De Mesa',
            2: 'Espumantes',
            3: 'Uvas Frescas',
            4: 'Uvas Passas',
            5: 'Suco De Uva'
        }
    elif opcao == 6: 
        subopcoes = {
            1: 'Vinhos De Mesa',
            2: 'Espumantes',
            3: 'Uvas Frescas',
            4: 'Suco De Uva'
        }
    else:
        logging.error(f"Subopção {sub} não é suportada para a Opção {opcao}.")
        return None
    
    valid_keys = subopcoes.keys()

    if sub not in valid_keys:
        url = f'{base_url}?ano={default_year}&opcao=opt_0{opcao}'
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser', from_encoding=response.encoding)
            botoes = soup.find_all('button', {'name': 'subopcao'})
            for botao in botoes:
                valor = botao.get('value')
                nome = botao.get_text(strip=True)
                if valor and nome:
                    subopcoes[valor] = nome
        except requests.exceptions.RequestException as e:
            logging.error(f"Erro ao acessar subopções de {opcao}: {e}")
        return subopcoes
    return subopcoes


def capturar_dados_opt_02_04(url, ano):
    dados = []
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser', from_encoding=response.encoding)
        tabela = soup.find('table', class_='tb_base tb_dados')
        
        produto_atual = None
        for row in tabela.find_all('tr'):
            cols = row.find_all('td')
            if not cols or len(cols) < 2:
                continue
            primeira_coluna = cols[0].get_text(strip=True)
            segunda_coluna = cols[1].get_text(strip=True)
            if not primeira_coluna or 'total' in primeira_coluna.lower():
                continue
            valor = None
            try:
                valor = float(segunda_coluna.replace('.', '').replace(',', '.')) if segunda_coluna not in ('', '-') else None
            except ValueError:
                pass
            if 'tb_item' in cols[0].get('class', []):
                produto_atual = primeira_coluna
                dados.append({
                    'ano': ano,
                    'produto': produto_atual.title(),
                    'subproduto': '*',
                    'quantidade_lt': valor
                })
            elif 'tb_subitem' in cols[0].get('class', []) and produto_atual:
                subproduto = primeira_coluna.lower()
                dados.append({
                    'ano': ano,
                    'produto': produto_atual.title(),
                    'subproduto': subproduto.title(),
                    'quantidade_lt': valor
                })
    except requests.exceptions.RequestException as e:
        logging.error(f"Erro ao acessar {url}: {e}")
    time.sleep(1)
    return dados

def capturar_dados_opt_03(url, ano, sub):
    dados = []
    if sub == 1:
        tipo_nome = 'Vinífetas'
    elif sub == 2:
        tipo_nome = 'Americanas E Híbridas'
    elif sub == 3:
        tipo_nome = 'Uvas De Mesa'
    elif sub == 4:
        tipo_nome = 'Sem Classificação'
    else:
        logging.error(f"Subopção inválida: {sub} para opção 3")
        valid_subs = capturar_subopcoes(3, sub)
        numeros_validos = [str(k) for k in valid_subs.keys() if isinstance(k, int)]
        subopcoes_list = ', '.join(numeros_validos) if numeros_validos else "nenhuma subopção encontrada"
        return {
            "erro": f"Subopção inválida. Escolha uma das seguintes subopções para essa opção: {subopcoes_list}."
        }, 400
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser', from_encoding=response.encoding)
        tabela = soup.find('table', class_='tb_base tb_dados')
        
        cultivar_atual = None
        for row in tabela.find_all('tr'):
            cols = row.find_all('td')
            if not cols or len(cols) < 2:
                continue
            primeira_coluna = cols[0].get_text(strip=True)
            segunda_coluna = cols[1].get_text(strip=True)
            if not primeira_coluna or 'total' in primeira_coluna.lower():
                continue
            valor = None
            try:
                valor = float(segunda_coluna.replace('.', '').replace(',', '.')) if segunda_coluna not in ('', '-') else None
            except ValueError:
                pass
            if 'tb_item' in cols[0].get('class', []):
                cultivar_atual = primeira_coluna
                dados.append({
                    'ano': ano,
                    'tipo': tipo_nome.title(),
                    'cultivar': cultivar_atual.title(),
                    'subproduto': '*',
                    'quantidade_kg': valor
                })
            elif 'tb_subitem' in cols[0].get('class', []) and cultivar_atual:
                subproduto = primeira_coluna.lower()
                dados.append({
                    'ano': ano,
                    'tipo': tipo_nome.title(),
                    'cultivar': cultivar_atual.title(),
                    'subproduto': subproduto.title(),
                    'quantidade_kg': valor
                })
    except requests.exceptions.RequestException as e:
        logging.error(f"Erro ao acessar {url}: {e}")
    time.sleep(1)
    return dados

def capturar_dados_opt_05_06(url, opcao, ano, sub):
    dados = []
    if sub == 1:
        tipo_nome = 'Vinhos De Mesa'
    elif sub == 2:
        tipo_nome = 'Espumantes'
    elif sub == 3:
        tipo_nome = 'Uvas Frescas'
    elif (opcao == 5 and sub == 4):
        tipo_nome = 'Uvas Passas'
    elif (opcao == 5 and sub == 5) or (opcao == 6 and sub == 4):
        tipo_nome = 'Suco De Uva'
    else:
        logging.error(f"Subopção inválida: {sub} para opção {opcao}")
        valid_subs = capturar_subopcoes(opcao, sub)
        numeros_validos = [str(k) for k in valid_subs.keys() if isinstance(k, int)]
        subopcoes_list = ', '.join(numeros_validos) if numeros_validos else "nenhuma subopção encontrada"
        return {
            "erro": f"Subopção inválida. Escolha uma das seguintes subopções para essa opção: {subopcoes_list}."
        }, 400
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser', from_encoding=response.encoding)
        tabela = soup.find('table', class_='tb_base tb_dados')

        for row in tabela.find_all('tr'):
            cols = row.find_all('td')
            if len(cols) != 3:
                continue
            pais = cols[0].get_text(strip=True)
            quantidade_raw = cols[1].get_text(strip=True)
            valor_raw = cols[2].get_text(strip=True)
            try:
                quantidade = float(quantidade_raw.replace('.', '').replace(',', '.')) if quantidade_raw not in ('', '-') else None
            except ValueError:
                quantidade = None
            try:
                valor = float(valor_raw.replace('.', '').replace(',', '.')) if valor_raw not in ('', '-') else None
            except ValueError:
                valor = None
            dados.append({
                'ano': ano,
                'tipo': tipo_nome.title(),
                'pais': pais.title(),
                'quantidade_kg': quantidade,
                'valor_usd': valor
            })
    except requests.exceptions.RequestException as e:
        logging.error(f"Erro ao acessar {url}: {e}")
    time.sleep(1)
    return dados

def capturar_dados(opcao, ano, sub):
    if opcao == 2 or opcao == 4:
        url = f'{base_url}?ano={ano}&opcao=opt_0{opcao}'
        return capturar_dados_opt_02_04(url, ano)
    elif opcao == 3:
        url = f'{base_url}?ano={ano}&opcao=opt_0{opcao}&subopcao=subopt_0{sub}'
        return capturar_dados_opt_03(url, ano, sub)
    elif opcao in [5, 6]:
        url = f'{base_url}?ano={ano}&opcao=opt_0{opcao}&subopcao=subopt_0{sub}'
        return capturar_dados_opt_05_06(url, opcao, ano, sub)
    else:
        logging.warning(f"⚠️ Opção {opcao} não é suportada.")
        return []

if __name__ == "__main__":
    #main()
    logging.info("🛠️ Script de coleta de dados iniciado.")