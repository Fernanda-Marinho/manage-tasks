# Gerenciador de Tarefas

Aplicação full stack para gestão de tarefas e categorias. O sistema permite criar, visualizar, editar e remover tarefas, associá-las a categorias opcionais e acompanhar o status de cada uma.

## Como executar

```bash
git clone https://github.com/Fernanda-Marinho/manage-tasks
cd manage-tasks
docker-compose up --build
```

Na **primeira execução**, o Docker irá:

1. Subir o PostgreSQL e aguardar o banco ficar saudável
2. Executar os testes automatizados (`pytest`)
3. Aplicar as migrations do banco (`flask db upgrade`) e iniciar a API Flask
4. Instalar dependências e iniciar o frontend React (Vite)


### Comandos úteis

| Parar a aplicação | Remover o volume de dados do banco | Executar apenas os testes |
|-------------------|---------------------------------------------------------|---------------------------|
| `docker-compose down` | `docker-compose down -v` | `docker-compose up --build tests` |

---

## Fluxo de uso

### 1. Tela inicial
A tela inicial fica disponível em http://localhost:5173 e a partir dela, pode acessar **Tarefas** ou **Categorias**.
<img width="1091" height="466" alt="image" src="https://github.com/user-attachments/assets/82812429-c3cc-4fa8-b3fb-2cd228aca0e0" />

### 2. Categorias 
Apesar de ser opcional, é recomendado criar uma categoria antes de criar as tarefas. Para criar uma categoria basta digitar o nome. A lista é atualizada automaticamente e não é permitido nomes repetidos. 
<img width="1021" height="344" alt="image" src="https://github.com/user-attachments/assets/946d64e5-4969-4e20-a969-3df0732b62fb" />

### 3. Criar tarefa
Na tela de tarefas, existe o botão **Nova Tarefa** onde apenas o campo do título é obrigatório. Categoria e Status são campos select para facilitar a experiência do usuário. Ao criar uma tarefa, é exibida uma mensagem de sucesso (que dura 1 segundo) e **a tela não redireciona para a listagem**, mantendo assim criação e visualização em telas separadas. O campo status é definido por padrão como **pendente**.
<table>
  <tr>
    <td>
      <img width="500" alt="Criar tarefa" src="https://github.com/user-attachments/assets/a728dd46-5818-479d-90da-f350e0439ab5" />
    </td>
    <td>
      <img width="500" alt="Mensagem de sucesso" src="https://github.com/user-attachments/assets/595b9418-23b2-4b81-8ffc-b44fd438f3ed" />
    </td>
  </tr>
</table>

### 4. Tela de visualização
Ao acessar **Tarefas**, todas as tarefas criadas até o momento são exibidas. Há um filtro por status e a visualização é paginada, sendo exibida 10 tarefas por página em um grid de 5x2. As tarefas são ordenadas por hora da criação. 
<table>
  <tr>
    <td>
      <img width="500" alt="CListar" src="https://github.com/user-attachments/assets/7958838e-cd5b-4856-8bea-2584a50adf6f" />
    </td>
    <td>
      <img width="500" alt="Listar paginação" src="https://github.com/user-attachments/assets/67507d17-ccd8-4e30-b6f7-330a02e4d60d" />
    </td>
  </tr>
</table>

### 4. Visualizar, editar e deletar
É possível visualizar detalhes de uma tarefa específica e editar. Após a edição, aparece a informação de **Atualizado em**. Além disso, é possível remover uma tarefa (soft delete). 

<table>
  <tr>
    <td>
      <img width="500" alt="Visualizar" src="https://github.com/user-attachments/assets/a1b9326a-6846-4126-9e01-a6cfb1480636" />
    </td>
    <td>
      <img width="500" alt="Visualizar apos editar" src="https://github.com/user-attachments/assets/ffbf71e2-e74f-4f92-be11-2217f9d1efe0" />
    </td>
  </tr>
</table>

## Decisões técnicas

### Backend — Flask + SQLAlchemy + Flask-Migrate

- **Flask** escolhido conforme o desafio, com blueprint (`api_bp`) para organizar rotas.
- **SQLAlchemy** como ORM para modelagem relacional com PostgreSQL.
- **Flask-Migrate (Alembic)** para versionamento do schema; as tabelas são criadas automaticamente via `flask db upgrade` ao subir o container da API.

### Soft delete em vez de hard delete

O DELETE não remove o registro fisicamente — preenche `deleted_at`. Tarefas deletadas não aparecem nas listagens nem podem ser editadas, preservando histórico.

### Status em maiúsculo

Apesar dos exemplos de status estarem em minúsculo (`pending`), no o PostgreSQL ENUM foi definido como `PENDING`, `IN_PROGRESS`, `DONE` por consistência com convenções de enum e clareza na API. O frontend traduz para português na interface.

### Paginação e filtro no backend

A paginação e o filtro por status são resolvidos no backend (`paginate()` + query param `status`), evitando carregar todas as tarefas no frontend. A UI consome `page`, `per_page` e exibe metadados (`total_pages`, `total_items`).

### Categorias — lookup no frontend

A API retorna `category_id` nas tarefas. Na tela de visualização, o nome da categoria é resolvido buscando `/categories` e fazendo match pelo ID.

### Testes antes da API subir

O `docker-compose.yml` inclui um serviço `tests` que roda `pytest` antes de iniciar a API. Garante que o ambiente está funcional antes de expor os endpoints.

### CORS

`flask-cors` habilitado para permitir que o frontend (porta 5173) consuma a API (porta 5000) em desenvolvimento.

### Separação criação / visualização (UX)

Ao criar uma tarefa, o formulário exibe mensagem de sucesso e é resetado, sem redirecionar para a listagem. A edição, por outro lado, retorna à listagem após salvar, sinalizando fluxos distintos para cadastro e manutenção.

## Melhorias futuras

- CI/CD (GitHub Actions) rodando testes a cada PR
- Endpoints de editar e deletar categorias
- Incluir nome da categoria via join na API (evitar segunda requisição no frontend)
- Autenticação e autorização (JWT ou sessão)
- Exibir categoria nos cards da listagem
- Loading states e feedback visual durante requisições
- Padronização de ícones e identidade visual do sistema 


