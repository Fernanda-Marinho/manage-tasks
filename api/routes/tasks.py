from flask import request, jsonify
from routes import api_bp
from models import db, Task
from datetime import datetime
from sqlalchemy.exc import IntegrityError

VALID_STATUSES = ['PENDING', 'IN_PROGRESS', 'DONE']

@api_bp.route('/tasks', methods=['POST'])
def create_task(): 
    data = request.get_json() or {}

    if 'title' not in data or not data['title'].strip():
        return jsonify({'error': 'Título é obrigatório'}), 400
    
    status = data.get('status', 'PENDING')
    if status not in VALID_STATUSES:
        return jsonify({'error': f'Status inválido. Use: {", ".join(VALID_STATUSES)}'}), 400
    
    new_task = Task(
        title=data['title'].strip(),
        description=data.get('description', '').strip(),
        status=status,
        category_id=data.get('category_id')  #should be an select in frontend
    )

    try:
        db.session.add(new_task)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Erro ao criar tarefa'}), 400

    return jsonify(new_task.to_dict()), 201


@api_bp.route('/tasks', methods=['GET'])
def get_tasks():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    status_filter = request.args.get('status', None)

    if status_filter and status_filter not in VALID_STATUSES:
        return jsonify({'error': f'Status inválido. Use: {", ".join(VALID_STATUSES)}'}), 400

    query = Task.query.filter_by(deleted_at=None)
    
    if status_filter:
        query = query.filter_by(status=status_filter)

    pagination = query.order_by(Task.created_at.desc()).paginate(
        page=page, 
        per_page=per_page, 
        error_out=False
    )

    task_array = [task.to_dict() for task in pagination.items]

    return jsonify({
        "tasks": task_array,
        "meta": {
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total_items": pagination.total,
            "total_pages": pagination.pages,
        }
    }), 200


@api_bp.route('/tasks/<uuid:id>', methods=['GET'])
def get_task_by_id(id):
    task = Task.query.filter_by(id=id, deleted_at=None).first_or_404(description="Tarefa não encontrada.")
    return jsonify(task.to_dict()), 200


@api_bp.route('/tasks/<uuid:id>', methods=['PUT'])
def update_task(id):
    task = Task.query.filter_by(id=id, deleted_at=None).first_or_404(description="Tarefa não encontrada para atualização.")
    
    data = request.get_json() or {}
    
    if 'title' in data:
        if not data['title'].strip():
            return jsonify({"error": "Título não pode ser vazio."}), 400
        task.title = data['title'].strip()

    if 'status' in data:
        status = data['status']
        if status not in VALID_STATUSES:
            return jsonify({
                "error": f"Status inválido. Use: {', '.join(VALID_STATUSES)}"
            }), 400
        task.status = status
        
    if 'description' in data:
        task.description = data['description'].strip()
        
    if 'category_id' in data:
        task.category_id = data['category_id']

    task.updated_at = datetime.utcnow()

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Erro ao atualizar tarefa'}), 400

    return jsonify(task.to_dict()), 200


@api_bp.route('/tasks/<uuid:id>', methods=['DELETE'])
def delete_task(id):
    task = Task.query.filter_by(id=id, deleted_at=None).first_or_404(description="Tarefa não encontrada.")
    task.deleted_at = datetime.utcnow()
    #db.session.delete(task) #in case of hard delete 
    db.session.commit()
    return jsonify({"message": "Tarefa removida com sucesso."}), 200