from .db_config import db


class Producao(db.Model):
    __tablename__ = 'producao'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ano = db.Column(db.Integer, nullable=False)
    produto = db.Column(db.String(120), nullable=False)
    subproduto = db.Column(db.String(120), nullable=False)
    quantidade_lt = db.Column(db.Integer, nullable=True)


class Processamento(db.Model):
    __tablename__ = 'processamento'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ano = db.Column(db.Integer, nullable=False)
    cultivar = db.Column(db.String(120), nullable=True)
    tipo = db.Column(db.String(120), nullable=True)
    subproduto = db.Column(db.String(120), nullable=False)
    quantidade_kg = db.Column(db.Integer, nullable=True)


class Comercializacao(db.Model):
    __tablename__ = 'comercializacao'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ano = db.Column(db.Integer, nullable=False)
    produto = db.Column(db.String(120), nullable=False)
    subproduto = db.Column(db.String(120), nullable=False)
    quantidade_lt = db.Column(db.Integer, nullable=True)


class Importacao(db.Model):
    __tablename__ = 'importacao'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ano = db.Column(db.Integer, nullable=False)
    tipo = db.Column(db.String(120), nullable=False)
    pais = db.Column(db.String(120), nullable=False)
    quantidade_kg = db.Column(db.Integer, nullable=True)
    valor_usd = db.Column(db.Float, nullable=True)


class Exportacao(db.Model):
    __tablename__ = 'exportacao'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ano = db.Column(db.Integer, nullable=False)
    tipo = db.Column(db.String(120), nullable=False)
    pais = db.Column(db.String(120), nullable=False)
    quantidade_kg = db.Column(db.Integer, nullable=True)
    valor_usd = db.Column(db.Float, nullable=True)
