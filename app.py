#!/usr/bin/env python3
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from config import Config
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(os.getcwd(), Config.DATABASE)}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    Config.init_app(app)
    db.init_app(app)
    
    with app.app_context():
        from models import RuleHistory, RuleTemplate, SystemConfig
        db.create_all()
    
    @app.route('/')
    def index():
        return render_template('index.html')
    
    from routes.rules import rules_bp
    from routes.history import history_bp
    from routes.templates import templates_bp
    from routes.system import system_bp
    from routes.import_export import import_export_bp
    
    app.register_blueprint(rules_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(templates_bp)
    app.register_blueprint(system_bp)
    app.register_blueprint(import_export_bp)
    
    return app

def init_default_data(app):
    with app.app_context():
        from routes.templates import init_templates
        init_templates()

if __name__ == '__main__':
    app = create_app()
    init_default_data(app)
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)