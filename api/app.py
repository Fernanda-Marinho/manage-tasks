from flask import Flask
from flask_migrate import Migrate
from models import db, Task, Category 

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:pass@db:5432/tasks_db'

db.init_app(app)
migrate = Migrate(app, db)

@app.route('/')
def index():
    return {"status": "OK"}