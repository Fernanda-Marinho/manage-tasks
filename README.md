# Gerenciador de Tarefas

Aplicação full stack para gestão de tarefas e categorias. O sistema permite criar, visualizar, editar e remover tarefas, associá-las a categorias opcionais e acompanhar o status de cada uma.

---

## Índice

- [Como executar](#como-executar)

---

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
