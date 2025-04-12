from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # Configuração do banco de dados
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventario.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'chave-secreta-da-aplicacao'
    
    # Inicializar extensões
    db.init_app(app)
    
    # Registrar blueprints
    from app.controllers.routes import main_bp
    app.register_blueprint(main_bp)
    
    # Garantir que o diretório instance exista
    os.makedirs(app.instance_path, exist_ok=True)
    
    # Criar as tabelas do banco de dados
    with app.app_context():
        db.create_all()
        # Para forçar a atualização das tabelas existentes com os novos campos
        # Isto só é necessário em ambiente de desenvolvimento
        # Num ambiente de produção, usaríamos migrações
        try:
            from app.models.models import ItemInventario
            # Verificar se os novos campos já existem
            if not hasattr(ItemInventario, 'valor_estoque_direto'):
                # Se não existir, recria as tabelas
                db.drop_all()
                db.create_all()
        except Exception as e:
            print(f"Erro ao atualizar esquema: {str(e)}")
    
    return app 