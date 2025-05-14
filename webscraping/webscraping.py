import re
import time
import logging
import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)

def capturar_anos(opcao, ano):
        if opcao == 'opt_02':
            min_ano, max_ano = 1970, 2023
        elif opcao == 'opt_03':
            min_ano, max_ano = 1970, 2023
        elif opcao == 'opt_04':
            min_ano, max_ano = 1970, 2023
        elif opcao == 'opt_05':
            min_ano, max_ano = 1970, 2024
        elif opcao == 'opt_06':
            min_ano, max_ano = 1970, 2024
        else:
            logging.error(f"Opção {opcao} não é suportada.")
            return None, None
        
        if ano < min_ano or ano > max_ano:
            url = f'http://vitibrasil.cnpuv.embrapa.br/index.php?ano=2023&opcao={opcao}'
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
    if opcao == 'opt_03':
        subopcoes = {
            'subopt_01': 'Viníferas',
            'subopt_02': 'Americanas e híbridas',
            'subopt_03': 'Uvas de mesa',
            'subopt_04': 'Sem classificação'
        } 
    elif opcao == 'opt_05':
        subopcoes = {
            'subopt_01': 'Vinhos de mesa',
            'subopt_02': 'Espumantes',
            'subopt_03': 'Uvas frescas',
            'subopt_04': 'Uvas passas',
            'subopt_05': 'Suco de uva'
        }
    elif opcao == 'opt_06': 
        subopcoes = {
            'subopt_01': 'Vinhos de mesa',
            'subopt_02': 'Espumantes',
            'subopt_03': 'Uvas frescas',
            'subopt_06': 'Suco de uva'
        }
    else:
        logging.error(f"Subopção {sub} não é suportada para a Opção {opcao}.")
        return None
    
    valid_keys = subopcoes.keys()

    if sub not in valid_keys:
        url = f'http://vitibrasil.cnpuv.embrapa.br/index.php?ano=2023&opcao={opcao}'
        subopcoes = {}
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


def capturar_dados_opt_02_04(ano, opcao):
    dados = []
    url = f'http://vitibrasil.cnpuv.embrapa.br/index.php?ano={ano}&opcao={opcao}'
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
                        'produto': produto_atual,
                        'subproduto': 'valor total produto',
                        'quantidade_lt': valor
                    })
                elif 'tb_subitem' in cols[0].get('class', []) and produto_atual:
                    subproduto = primeira_coluna.lower()
                    dados.append({
                        'ano': ano,
                        'produto': produto_atual,
                        'subproduto': subproduto,
                        'quantidade_lt': valor
                    })
    except requests.exceptions.RequestException as e:
        logging.error(f"Erro ao acessar {url}: {e}")
    time.sleep(1)
    return dados

def capturar_dados_opt_03(ano, sub):
    dados = []
    url = f'http://vitibrasil.cnpuv.embrapa.br/index.php?ano={ano}&opcao=opt_03&subopcao={sub}'
    if sub == 'subopt_01':
        tipo_nome = 'Vinífetas'
    if sub == 'subopt_02':
        tipo_nome = 'Americanas e Híbridas'
    if sub == 'subopt_03':
        tipo_nome = 'Uvas de mesa'
    if sub == 'subopt_04':
        tipo_nome = 'Sem classificação'
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
                            'tipo': tipo_nome,
                            'cultivar': cultivar_atual,
                            'subproduto': 'valor total cultivar',
                            'quantidade_kg': valor
                        })
                    elif 'tb_subitem' in cols[0].get('class', []) and cultivar_atual:
                        subproduto = primeira_coluna.lower()
                        dados.append({
                            'ano': ano,
                            'tipo': tipo_nome,
                            'cultivar': cultivar_atual,
                            'subproduto': subproduto,
                            'quantidade_kg': valor
                        })
    except requests.exceptions.RequestException as e:
        logging.error(f"Erro ao acessar {url}: {e}")
    time.sleep(1)
    return dados

def capturar_dados_opt_05_06(opcao, ano, sub):
    dados = []
    url = f'http://vitibrasil.cnpuv.embrapa.br/index.php?ano={ano}&opcao={opcao}&subopcao={sub}'
    if sub == 'subopt_01':
        tipo_nome = 'Vinhos de mesa'
    if sub == 'subopt_02':
        tipo_nome = 'Espumantes'
    if sub == 'subopt_03':
        tipo_nome = 'Uvas frescas'
    if (opcao == 'opt_05') & (sub == 'subopt_04'):
        tipo_nome = 'Uvas passas'
    if ((opcao == 'opt_05') & (sub == 'subopt_05')) | ((opcao == 'opt_04') & (sub == 'subopt_04')):
        tipo_nome = 'Suco de uva'
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
                        'tipo': tipo_nome,
                        'pais': pais,
                        'quantidade_kg': quantidade,
                        'valor_usd': valor
                    })
    except requests.exceptions.RequestException as e:
        logging.error(f"Erro ao acessar {url}: {e}")
    time.sleep(1)
    return dados

def capturar_dados(opcao, ano, sub):
    if opcao == 'opt_02' or opcao == 'opt_04':
        return capturar_dados_opt_02_04(ano, opcao)
    elif opcao == 'opt_03':
        return capturar_dados_opt_03(ano, sub)
    elif opcao in ['opt_05', 'opt_06']:
        return capturar_dados_opt_05_06(opcao, ano, sub)
    else:
        logging.warning(f"⚠️ Opção {opcao} não é suportada.")
        return []

if __name__ == "__main__":
    #main()
    logging.info("🛠️ Script de coleta de dados iniciado.")