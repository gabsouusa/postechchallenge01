# PosTechChallenge
Pos Tech - Machine Learning Engineering

Challenge 01 - API pública de consulta nos dados

## API

Link: https://postechchallenge01-badpbzdsbmdaazg2.eastus2-01.azurewebsites.net/

## Instalar Python

Instalando a versão 3.13.3

```
https://www.python.org/ftp/python/3.13.3/python-3.13.3-amd64.exe
```

## Activate venv ans install libs

```cmd
python -m venv venv
venv/Scripts/activate
pip install -r requirements.txt
```

## Run

```cmd
python app.py
```

## Rotas

Documentação Swagger - https://postechchallenge01-badpbzdsbmdaazg2.eastus2-01.azurewebsites.net/apidocs

```
salvar usuario no banco
    post/register

retornar jwt token
    post/login

get - pegar dados do site/banco com parametros de busca

    get/producao
    get/processamento
    get/comercializacao
    get/importacao
    get/exportacao
```
## Arquitetura API
![alt text](docs/architecture.png)