from flask import request, jsonify
from routes import api_bp
from models import db, Category 
from sqlalchemy.exc import IntegrityError

@api_bp.route('/categories', methods=['POST'])
def create_category():
    data = request.get_json() or {}
    
    if 'name' not in data or not data['name'].strip():
        return jsonify({'error': 'Nome da categoria é obrigatório'}), 400

    new_category = Category(
        name=data['name'].strip()
    )

    try:
        db.session.add(new_category)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Categoria com este nome já existe ou dados inválidos'}), 400

    return jsonify({
        'id': new_category.id,
        'name': new_category.name
    }), 201


@api_bp.route('/categories', methods=['GET'])
def get_categories():
    categories = Category.query.order_by(Category.name.asc()).all()
    categories_array = [{
        'id': cat.id,
        'name': cat.name
    } for cat in categories]

    return jsonify(categories_array), 200
