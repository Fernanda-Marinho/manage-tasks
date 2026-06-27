from flask import request, jsonify
from routes import api_bp
from models import db, Task
from datetime import datetime


@api_bp.route('/tasks', methods=['POST'])
def create_task(): 
    data = request.get_json() or {}

    if 'title' not in data: 
        return jsonify({'error': 'Título é obrigatório'}), 400
    
    status = data.get('status', 'PENDING').upper()  
    if status not in ['PENDING', 'IN_PROGRESS', 'COMPLETED']:
        return jsonify({'error': 'Status inválido'}), 400
    
    new_task = Task(
        title=data['title'].strip(),
        description=data.get('description', ''),
        status=status,
        category_id=data.get('category_id')  #should be an select in frontend
    )

    db.session.add(new_task)
    db.session.commit()

    return jsonify(new_task.to_dict()), 201


@api_bp.route('/tasks', methods=['GET'])
def get_tasks():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    pagination = Task.query.filter_by(deleted_at=None).order_by(Task.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)

    task_array = [tasks.to_dict() for tasks in pagination.items]

    return jsonify({
        "tasks": task_array,
        "data": {
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total_items": pagination.total,
            "total_pages": pagination.pages,
            "has_next": pagination.has_next,
            "has_prev": pagination.has_prev
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
            return jsonify({"error": "O campo 'title' não pode ser vazio."}), 400
        task.title = data['title']

    status = data.get('status', 'PENDING').upper()

    if status in data:
        if data['status'] not in ['PENDING', 'IN_PROGRESS', 'DONE']:
            return jsonify({"error": "Status inválido. Use PENDING, IN_PROGRESS ou DONE."}), 400
        task.status = data['status']
        
    if 'description' in data:
        task.description = data.get('description', '')
        
    if 'category_id' in data:
        task.category_id = data.get('category_id')

    db.session.commit()
    return jsonify(task.to_dict()), 200


@api_bp.route('/tasks/<uuid:id>', methods=['DELETE'])
def delete_task(id):
    task = Task.query.filter_by(id=id, deleted_at=None).first_or_404(description="Tarefa não encontrada ou já deletada.")
    task.deleted_at = datetime.utcnow()
    #db.session.delete(task) #in case of hard delete 
    db.session.commit()
    return jsonify({"message": "Tarefa removida com sucesso."}), 200

