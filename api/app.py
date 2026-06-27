import os
from flask import Flask
from flask_migrate import Migrate
from models import db
from routes import api_bp

migrate = Migrate()

def create_app(config_name=None):
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://user:pass@db:5432/tasks_db')

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(api_bp)

    return app

app = create_app()