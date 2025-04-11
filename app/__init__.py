from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'chave_secreta_para_desenvolvimento'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventario.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
    
    db.init_app(app)
    
    from app.controllers.routes import main_bp
    app.register_blueprint(main_bp)
    
    with app.app_context():
        db.create_all()
    
    return app 