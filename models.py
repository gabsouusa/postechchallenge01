from db_config import db

class Wine(db.Model):
    __tablename__ = 'vitibrasil'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    opcao = db.Column(db.String(10), nullable=False)
    subopcao = db.Column(db.String(10), nullable=True)
    ano = db.Column(db.Integer, nullable=False)
    produto = db.Column(db.String(120), nullable=True)
    subproduto = db.Column(db.String(120), nullable=True)
    tipo = db.Column(db.String(120), nullable=True)
    quantidade_lt = db.Column(db.Integer, nullable=True)
    quantidade_kg = db.Column(db.Integer, nullable=True)
    cultivar = db.Column(db.String(120), nullable=True)
    pais = db.Column(db.String(120), nullable=True)
    valor_usd = db.Column(db.Float, nullable=True)
