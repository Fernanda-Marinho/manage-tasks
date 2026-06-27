from flask import Blueprint

api_bp = Blueprint('api', __name__)

@api_bp.route('/', methods=['GET'])
def index():
    return {"status": "HOME OK"}

from routes.tasks import *
from routes.categories import *