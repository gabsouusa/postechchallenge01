from modules.database.models import Producao, Processamento, Comercializacao, Importacao, Exportacao


def create_tables(app, db):
    with app.app_context():
        db.create_all()


def drop_tables(app, db):
    with app.app_context():
        Producao.__table__.drop(db.engine)
        Processamento.__table__.drop(db.engine)
        Comercializacao.__table__.drop(db.engine)
        Importacao.__table__.drop(db.engine)
        Exportacao.__table__.drop(db.engine)


def register_data(db, data, opt, opcao_model_map):
    Model = opcao_model_map.get(opt)
    registros = []
    for item in data:
        campos_validos = {col.name for col in Model.__table__.columns}
        dados_filtrados = {
            key: value
            for key, value in item.items()
            if key in campos_validos
        }
        registro = Model(**dados_filtrados)
        registros.append(registro)

    db.session.add_all(registros)
    db.session.commit()


def fetch_data(query, Model):
    data = []
    for row in query.all():
        row_data = {}
        for column in Model.__table__.columns:  
            row_data[column.name] = getattr(row, column.name)  
        data.append(row_data)
    return data


def execute_query(year, opt, sub, sub_value, opcao_model_map):
    Model = opcao_model_map.get(opt)
    filters = [Model.ano == (int(year) if year is not None else 2023)]
    if sub is not None:
        filters.append(Model.tipo == sub_value)
    query = Model.query.filter(*filters)
    if query.count() == 0:
        return None
    return fetch_data(query, Model)
