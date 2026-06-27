import pytest
from uuid import uuid4


@pytest.fixture
def app():
    """Cria app em modo teste"""
    from app import create_app, db
    
    app = create_app(config_name='testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Cliente de teste do Flask"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """CLI runner para testes"""
    return app.test_cli_runner()


@pytest.fixture
def sample_category(client):
    """Cria uma categoria de teste"""
    response = client.post('/categories', 
        json={'name': 'Desenvolvimento'},
        content_type='application/json'
    )
    return response.get_json()


@pytest.fixture
def sample_task(client, sample_category):
    """Cria uma tarefa de teste"""
    response = client.post('/tasks',
        json={
            'title': 'Implementar API',
            'description': 'Criar endpoints REST',
            'status': 'PENDING',
            'category_id': sample_category['id']
        },
        content_type='application/json'
    )
    return response.get_json()


class TestTasksCreate:
    """Testes para POST /tasks"""
    
    def test_create_task_with_valid_data(self, client, sample_category):
        """Deve criar tarefa com dados válidos"""
        response = client.post('/tasks',
            json={
                'title': 'Nova tarefa',
                'description': 'Descrição da tarefa',
                'status': 'PENDING',
                'category_id': sample_category['id']
            },
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['title'] == 'Nova tarefa'
        assert data['description'] == 'Descrição da tarefa'
        assert data['status'] == 'PENDING'
        assert data['category_id'] == sample_category['id']
        assert 'id' in data
        assert 'created_at' in data

    def test_create_task_with_minimum_data(self, client):
        """Deve criar tarefa com apenas título"""
        response = client.post('/tasks',
            json={'title': 'Tarefa mínima'},
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['title'] == 'Tarefa mínima'
        assert data['status'] == 'PENDING' 
        assert data['description'] == ''
        assert data['category_id'] is None

    def test_create_task_without_title(self, client):
        """Deve falhar sem título"""
        response = client.post('/tasks',
            json={'description': 'Sem título'},
            content_type='application/json'
        )
        
        assert response.status_code == 400
        assert 'Título é obrigatório' in response.get_json()['error']

    def test_create_task_with_empty_title(self, client):
        """Deve falhar com título vazio"""
        response = client.post('/tasks',
            json={'title': ''},
            content_type='application/json'
        )
        
        assert response.status_code == 400
        assert 'Título é obrigatório' in response.get_json()['error']

    def test_create_task_with_whitespace_title(self, client):
        """Deve falhar com título só de espaços"""
        response = client.post('/tasks',
            json={'title': '   '},
            content_type='application/json'
        )
        
        assert response.status_code == 400
        assert 'Título é obrigatório' in response.get_json()['error']

    def test_create_task_with_invalid_status(self, client):
        """Deve falhar com status inválido"""
        response = client.post('/tasks',
            json={
                'title': 'Tarefa',
                'status': 'INVALID_STATUS'
            },
            content_type='application/json'
        )
        
        assert response.status_code == 400
        assert 'Status inválido' in response.get_json()['error']

    @pytest.mark.parametrize('status', ['PENDING', 'IN_PROGRESS', 'DONE'])
    def test_create_task_with_all_valid_statuses(self, client, status):
        """Deve aceitar todos os status válidos"""
        response = client.post('/tasks',
            json={'title': f'Tarefa com {status}', 'status': status},
            content_type='application/json'
        )
        
        assert response.status_code == 201
        assert response.get_json()['status'] == status

    def test_create_task_strips_whitespace(self, client):
        """Deve remover espaços em branco"""
        response = client.post('/tasks',
            json={
                'title': '  Título com espaços  ',
                'description': '  Descrição com espaços  '
            },
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['title'] == 'Título com espaços'
        assert data['description'] == 'Descrição com espaços'

    def test_create_task_with_nonexistent_category(self, client):
        """Deve aceitar category_id inexistente (FK permite NULL)"""
        response = client.post('/tasks',
            json={
                'title': 'Tarefa',
                'category_id': 9999
            },
            content_type='application/json'
        )
        
        assert response.status_code == 201


class TestTasksList:
    """Testes para GET /tasks"""
    
    def test_get_tasks_empty(self, client):
        """Deve retornar lista vazia"""
        response = client.get('/tasks')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['tasks'] == []
        assert data['meta']['total_items'] == 0
        assert data['meta']['total_pages'] == 0

    def test_get_tasks_with_pagination(self, client):
        """Deve retornar tarefas com paginação"""
        # Cria 15 tarefas
        for i in range(15):
            client.post('/tasks',
                json={'title': f'Tarefa {i}'},
                content_type='application/json'
            )
        
        response = client.get('/tasks?page=1&per_page=10')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['tasks']) == 10
        assert data['meta']['page'] == 1
        assert data['meta']['per_page'] == 10
        assert data['meta']['total_items'] == 15
        assert data['meta']['total_pages'] == 2

    def test_get_tasks_second_page(self, client):
        """Deve retornar segunda página"""
        for i in range(15):
            client.post('/tasks',
                json={'title': f'Tarefa {i}'},
                content_type='application/json'
            )
        
        response = client.get('/tasks?page=2&per_page=10')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['tasks']) == 5
        assert data['meta']['page'] == 2

    def test_get_tasks_filter_by_status(self, client):
        """Deve filtrar por status"""
        for i in range(3):
            client.post('/tasks',
                json={
                    'title': f'PENDING {i}',
                    'status': 'PENDING'
                },
                content_type='application/json'
            )
        
        for i in range(2):
            client.post('/tasks',
                json={
                    'title': f'IN_PROGRESS {i}',
                    'status': 'IN_PROGRESS'
                },
                content_type='application/json'
            )
        
        response = client.get('/tasks?status=PENDING')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['tasks']) == 3
        assert all(task['status'] == 'PENDING' for task in data['tasks'])

    def test_get_tasks_filter_with_invalid_status(self, client):
        """Deve falhar com filtro de status inválido"""
        response = client.get('/tasks?status=INVALID')
        
        assert response.status_code == 400
        assert 'Status inválido' in response.get_json()['error']

    def test_get_tasks_ordered_by_created_at_desc(self, client):
        """Deve ordenar por created_at decrescente (mais recentes primeiro)"""
        for i in range(3):
            client.post('/tasks',
                json={'title': f'Tarefa {i}'},
                content_type='application/json'
            )
        
        response = client.get('/tasks')
        data = response.get_json()
        tasks = data['tasks']
        
        for i in range(len(tasks) - 1):
            assert tasks[i]['created_at'] >= tasks[i+1]['created_at']

    def test_get_tasks_excludes_deleted(self, client):
        """Deve excluir tarefas deletadas (soft delete)"""
        task1 = client.post('/tasks', json={'title': 'Tarefa 1'}).get_json()
        task2 = client.post('/tasks', json={'title': 'Tarefa 2'}).get_json()
        
        # Deleta a primeira
        client.delete(f'/tasks/{task1["id"]}')
        
        # Deve retornar só a segunda
        response = client.get('/tasks')
        data = response.get_json()
        assert len(data['tasks']) == 1
        assert data['tasks'][0]['id'] == task2['id']

    @pytest.mark.parametrize('status', ['PENDING', 'IN_PROGRESS', 'DONE'])
    def test_get_tasks_filter_by_all_statuses(self, client, status):
        """Deve filtrar por cada status válido"""
        client.post('/tasks',
            json={'title': 'Tarefa', 'status': status},
            content_type='application/json'
        )
        
        response = client.get(f'/tasks?status={status}')
        assert response.status_code == 200
        assert len(response.get_json()['tasks']) == 1


class TestTasksGetById:
    """Testes para GET /tasks/<id>"""
    
    def test_get_task_by_id(self, client, sample_task):
        """Deve retornar tarefa pelo ID"""
        response = client.get(f'/tasks/{sample_task["id"]}')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['id'] == sample_task['id']
        assert data['title'] == sample_task['title']

    def test_get_task_nonexistent_id(self, client):
        """Deve retornar 404 para ID inexistente"""
        fake_uuid = str(uuid4())
        response = client.get(f'/tasks/{fake_uuid}')
        
        assert response.status_code == 404

    def test_get_deleted_task(self, client, sample_task):
        """Deve retornar 404 para tarefa deletada"""
        # Deleta a tarefa
        client.delete(f'/tasks/{sample_task["id"]}')
        
        # Tenta buscar
        response = client.get(f'/tasks/{sample_task["id"]}')
        assert response.status_code == 404

    def test_get_task_invalid_uuid_format(self, client):
        """Deve retornar 404 para UUID inválido"""
        response = client.get('/tasks/not-a-uuid')
        
        assert response.status_code == 404


class TestTasksUpdate:
    """Testes para PUT /tasks/<id>"""
    
    def test_update_task_title(self, client, sample_task):
        """Deve atualizar título"""
        response = client.put(f'/tasks/{sample_task["id"]}',
            json={'title': 'Novo título'},
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['title'] == 'Novo título'

    def test_update_task_status(self, client, sample_task):
        """Deve atualizar status"""
        response = client.put(f'/tasks/{sample_task["id"]}',
            json={'status': 'IN_PROGRESS'},
            content_type='application/json'
        )
        
        assert response.status_code == 200
        assert response.get_json()['status'] == 'IN_PROGRESS'

    def test_update_task_description(self, client, sample_task):
        """Deve atualizar descrição"""
        response = client.put(f'/tasks/{sample_task["id"]}',
            json={'description': 'Nova descrição'},
            content_type='application/json'
        )
        
        assert response.status_code == 200
        assert response.get_json()['description'] == 'Nova descrição'

    def test_update_task_multiple_fields(self, client, sample_task):
        """Deve atualizar múltiplos campos"""
        response = client.put(f'/tasks/{sample_task["id"]}',
            json={
                'title': 'Novo título',
                'status': 'DONE',
                'description': 'Nova descrição'
            },
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['title'] == 'Novo título'
        assert data['status'] == 'DONE'
        assert data['description'] == 'Nova descrição'

    def test_update_task_empty_title(self, client, sample_task):
        """Deve falhar ao tentar esvaziar título"""
        response = client.put(f'/tasks/{sample_task["id"]}',
            json={'title': ''},
            content_type='application/json'
        )
        
        assert response.status_code == 400
        assert 'não pode ser vazio' in response.get_json()['error']

    def test_update_task_invalid_status(self, client, sample_task):
        """Deve falhar com status inválido"""
        response = client.put(f'/tasks/{sample_task["id"]}',
            json={'status': 'INVALID'},
            content_type='application/json'
        )
        
        assert response.status_code == 400
        assert 'Status inválido' in response.get_json()['error']

    def test_update_task_nonexistent(self, client):
        """Deve retornar 404 ao atualizar tarefa inexistente"""
        fake_uuid = str(uuid4())
        response = client.put(f'/tasks/{fake_uuid}',
            json={'title': 'Novo'},
            content_type='application/json'
        )
        
        assert response.status_code == 404

    def test_update_deleted_task(self, client, sample_task):
        """Deve falhar ao atualizar tarefa deletada"""
        client.delete(f'/tasks/{sample_task["id"]}')
        
        response = client.put(f'/tasks/{sample_task["id"]}',
            json={'title': 'Novo'},
            content_type='application/json'
        )
        
        assert response.status_code == 404

    def test_update_task_strips_whitespace(self, client, sample_task):
        """Deve remover espaços em branco"""
        response = client.put(f'/tasks/{sample_task["id"]}',
            json={
                'title': '  Novo título  ',
                'description': '  Nova descrição  '
            },
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['title'] == 'Novo título'
        assert data['description'] == 'Nova descrição'

    @pytest.mark.parametrize('status', ['PENDING', 'IN_PROGRESS', 'DONE'])
    def test_update_task_all_valid_statuses(self, client, sample_task, status):
        """Deve aceitar todos os status válidos na atualização"""
        response = client.put(f'/tasks/{sample_task["id"]}',
            json={'status': status},
            content_type='application/json'
        )
        
        assert response.status_code == 200
        assert response.get_json()['status'] == status


class TestTasksDelete:
    """Testes para DELETE /tasks/<id>"""
    
    def test_delete_task(self, client, sample_task):
        """Deve deletar tarefa (soft delete)"""
        response = client.delete(f'/tasks/{sample_task["id"]}')
        
        assert response.status_code == 200
        assert 'removida com sucesso' in response.get_json()['message']

    def test_delete_task_sets_deleted_at(self, client, sample_task):
        """Deve preencher deleted_at"""
        client.delete(f'/tasks/{sample_task["id"]}')
        
        # Tenta buscar — deve retornar 404
        response = client.get(f'/tasks/{sample_task["id"]}')
        assert response.status_code == 404

    def test_delete_nonexistent_task(self, client):
        """Deve retornar 404 ao deletar inexistente"""
        fake_uuid = str(uuid4())
        response = client.delete(f'/tasks/{fake_uuid}')
        
        assert response.status_code == 404

    def test_delete_already_deleted_task(self, client, sample_task):
        """Deve falhar ao deletar tarefa já deletada"""
        client.delete(f'/tasks/{sample_task["id"]}')
        
        # Tenta deletar novamente
        response = client.delete(f'/tasks/{sample_task["id"]}')
        assert response.status_code == 404

    def test_delete_removes_from_list(self, client, sample_task):
        """Deve remover da listagem após deletar"""
        # Verifica que existe
        response = client.get('/tasks')
        assert len(response.get_json()['tasks']) == 1
        
        # Deleta
        client.delete(f'/tasks/{sample_task["id"]}')
        
        # Verifica que sumiu
        response = client.get('/tasks')
        assert len(response.get_json()['tasks']) == 0


class TestCategoriesCreate:
    """Testes para POST /categories"""
    
    def test_create_category_with_valid_name(self, client):
        """Deve criar categoria com nome válido"""
        response = client.post('/categories',
            json={'name': 'Desenvolvimento'},
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['name'] == 'Desenvolvimento'
        assert 'id' in data

    def test_create_category_without_name(self, client):
        """Deve falhar sem nome"""
        response = client.post('/categories',
            json={},
            content_type='application/json'
        )
        
        assert response.status_code == 400

    def test_create_category_empty_name(self, client):
        """Deve falhar com nome vazio"""
        response = client.post('/categories',
            json={'name': ''},
            content_type='application/json'
        )
        
        assert response.status_code == 400

    def test_create_category_duplicate_name(self, client):
        """Deve falhar com nome duplicado (unique constraint)"""
        client.post('/categories',
            json={'name': 'Desenvolvimento'},
            content_type='application/json'
        )
        
        response = client.post('/categories',
            json={'name': 'Desenvolvimento'},
            content_type='application/json'
        )
        
        assert response.status_code == 400
        assert 'já existe' in response.get_json()['error']

    def test_create_category_strips_whitespace(self, client):
        """Deve remover espaços em branco"""
        response = client.post('/categories',
            json={'name': '  Desenvolvimento  '},
            content_type='application/json'
        )
        
        assert response.status_code == 201
        assert response.get_json()['name'] == 'Desenvolvimento'


class TestCategoriesList:
    """Testes para GET /categories"""
    
    def test_get_categories_empty(self, client):
        """Deve retornar lista vazia"""
        response = client.get('/categories')
        
        assert response.status_code == 200
        assert response.get_json() == []

    def test_get_categories(self, client, sample_category):
        """Deve retornar categorias"""
        response = client.get('/categories')
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 1
        assert data[0]['name'] == sample_category['name']

    def test_get_categories_ordered_by_name(self, client):
        """Deve retornar categorias ordenadas por nome"""
        names = ['Zebra', 'Apple', 'Mango']
        for name in names:
            client.post('/categories',
                json={'name': name},
                content_type='application/json'
            )
        
        response = client.get('/categories')
        data = response.get_json()
        
        returned_names = [cat['name'] for cat in data]
        assert returned_names == sorted(names)


class TestIntegration:
    """Testes de integração completos"""
    
    def test_full_task_lifecycle(self, client, sample_category):
        """Teste completo: criar → atualizar → deletar"""
        # 1. Cria tarefa
        create_response = client.post('/tasks',
            json={
                'title': 'Tarefa do ciclo',
                'status': 'PENDING',
                'category_id': sample_category['id']
            },
            content_type='application/json'
        )
        assert create_response.status_code == 201
        task = create_response.get_json()
        task_id = task['id']
        
        # 2. Busca tarefa
        get_response = client.get(f'/tasks/{task_id}')
        assert get_response.status_code == 200
        assert get_response.get_json()['status'] == 'PENDING'
        
        # 3. Atualiza para IN_PROGRESS
        update_response = client.put(f'/tasks/{task_id}',
            json={'status': 'IN_PROGRESS'},
            content_type='application/json'
        )
        assert update_response.status_code == 200
        assert update_response.get_json()['status'] == 'IN_PROGRESS'
        
        # 4. Atualiza para DONE
        update_response = client.put(f'/tasks/{task_id}',
            json={'status': 'DONE'},
            content_type='application/json'
        )
        assert update_response.status_code == 200
        assert update_response.get_json()['status'] == 'DONE'
        
        # 5. Deleta
        delete_response = client.delete(f'/tasks/{task_id}')
        assert delete_response.status_code == 200
        
        # 6. Verifica que não existe mais
        get_response = client.get(f'/tasks/{task_id}')
        assert get_response.status_code == 404

    def test_filter_and_paginate(self, client):
        """Teste: criar múltiplas tarefas e filtrar + paginar"""
        # Cria 25 tarefas (10 pending, 10 in_progress, 5 done)
        for i in range(10):
            client.post('/tasks',
                json={'title': f'Pending {i}', 'status': 'PENDING'},
                content_type='application/json'
            )
        
        for i in range(10):
            client.post('/tasks',
                json={'title': f'In Progress {i}', 'status': 'IN_PROGRESS'},
                content_type='application/json'
            )
        
        for i in range(5):
            client.post('/tasks',
                json={'title': f'Done {i}', 'status': 'DONE'},
                content_type='application/json'
            )
        
        # Filtra por PENDING
        response = client.get('/tasks?status=PENDING&page=1&per_page=5')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['tasks']) == 5
        assert data['meta']['total_items'] == 10
        assert data['meta']['total_pages'] == 2
        assert all(t['status'] == 'PENDING' for t in data['tasks'])