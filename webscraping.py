import requests
from bs4 import BeautifulSoup
import re
import json
import logging
import time

logging.basicConfig(level=logging.INFO)

def capturar_anos(opcao):
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

def capturar_subopcoes(opcao):
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

# def extrair_tipo_limpo(texto_botao):
#     return texto_botao.strip()

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
                        'quantidade_l': valor
                    })
                elif 'tb_subitem' in cols[0].get('class', []) and produto_atual:
                    subproduto = primeira_coluna.lower()
                    dados.append({
                        'ano': ano,
                        'produto': produto_atual,
                        'subproduto': subproduto,
                        'quantidade_l': valor
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

# def main():
#     opcoes = ['opt_02', 'opt_03', 'opt_04', 'opt_05', 'opt_06']
#     dados_finais = {}
#     for opcao in opcoes:
#         logging.info(f"\n🚀 Iniciando coleta da opção {opcao}")
#         ano_inicio, ano_fim = capturar_anos(opcao)
#         if not (ano_inicio and ano_fim):
#             logging.warning(f"❌ Intervalo de anos não encontrado para {opcao}.")
#             continue

#         if opcao == 'opt_02' or opcao == 'opt_04':
#             dados = capturar_dados_opt_02_04(ano_inicio, ano_fim, opcao)
#         elif opcao == 'opt_03':
#             dados = capturar_dados_opt_03(ano_inicio, ano_fim)
#         elif opcao in ['opt_05', 'opt_06']:
#             dados = capturar_dados_opt_05_06(opcao, ano_inicio, ano_fim)
#         else:
#             dados = []

#         if dados:
#             dados_finais[opcao] = dados
#             logging.info(f"✅ Coleta finalizada para {opcao} com {len(dados)} registros.")
#         else:
#             logging.warning(f"⚠️ Nenhum dado coletado para {opcao}.")

#     # Exporta para JSON
#     for opcao, registros in dados_finais.items():
#         with open(f'dados_{opcao}.json', 'w', encoding='utf-8') as f:
#             json.dump(registros, f, ensure_ascii=False, indent=2)
#         logging.info(f"💾 Arquivo JSON salvo: dados_{opcao}.json")

if __name__ == "__main__":
    #main()
    logging.info("🛠️ Script de coleta de dados iniciado.")
