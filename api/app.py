from flask import Flask
from flask_migrate import Migrate
from models import db, Task, Category 
from routes import api_bp

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:pass@db:5432/tasks_db'

db.init_app(app)
migrate = Migrate(app, db)

app.register_blueprint(api_bp)

@app.route('/')
def index():
    return {"status": "OK"}