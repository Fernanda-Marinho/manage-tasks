import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { API_URL } from '../api';

const STATUS_LABELS = {
  PENDING: 'Pendente',
  IN_PROGRESS: 'Em Progresso',
  DONE: 'Concluída',
};

export default function Tasks() {
  const [tasks, setTasks] = useState([]);
  const [meta, setMeta] = useState({});
  const [page, setPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState('');
  const navigate = useNavigate();

  const fetchTasks = async (currentPage, status) => {
    const params = new URLSearchParams({
      page: currentPage,
      per_page: 10,
    });
    if (status) params.set('status', status);

    const res = await fetch(`${API_URL}/tasks?${params}`);
    const data = await res.json();
    if (res.ok) {
      setTasks(data.tasks);
      setMeta(data.meta);
    }
  };

  useEffect(() => {
    fetchTasks(page, statusFilter);
  }, [page, statusFilter]);

  const handleStatusFilterChange = (value) => {
    setStatusFilter(value);
    setPage(1);
  };

  const handleDelete = async (id) => {
    if (window.confirm("Deseja realmente deletar?")) {
      await fetch(`${API_URL}/tasks/${id}`, { method: 'DELETE' });
      fetchTasks(page, statusFilter);
    }
  };

  return (
    <div>
      <div className="header-actions">
        <button onClick={() => navigate('/')} className="btn-back">Voltar para Home</button>
        <button onClick={() => navigate('/tasks/new')} className="btn-success">Nova Tarefa</button>
      </div>
      
      <h2>Lista de Tarefas</h2>

      <div className="task-filters">
        <label htmlFor="status-filter">Filtrar por status:</label>
        <select
          id="status-filter"
          value={statusFilter}
          onChange={(e) => handleStatusFilterChange(e.target.value)}
        >
          <option value="">Todos</option>
          <option value="PENDING">Pendente</option>
          <option value="IN_PROGRESS">Em Progresso</option>
          <option value="DONE">Concluída</option>
        </select>
      </div>
      
      <div className="task-grid">
        {tasks.map(task => (
          <div key={task.id} className="task-card">
            <h3>{task.title}</h3>
            <span className={`badge ${task.status.toLowerCase()}`}>
              {STATUS_LABELS[task.status] || task.status}
            </span>
            <div className="card-actions">
              <button onClick={() => navigate(`/tasks/view/${task.id}`)} className="btn-primary">Visualizar</button>
              <button onClick={() => navigate(`/tasks/edit/${task.id}`)} className="btn-secondary">Editar</button>
              <button onClick={() => handleDelete(task.id)} className="btn-danger">Deletar</button>
            </div>
          </div>
        ))}
        {tasks.length === 0 && <p className="task-grid-empty">Nenhuma tarefa encontrada.</p>}
      </div>

      <div className="pagination">
        <button
          className="btn-pagination"
          disabled={page === 1}
          onClick={() => setPage(page - 1)}
        >
          Anterior
        </button>
        <span className="pagination-info">Página {meta.page} de {meta.total_pages || 1}</span>
        <button
          className="btn-pagination"
          disabled={page === meta.total_pages || !meta.total_pages}
          onClick={() => setPage(page + 1)}
        >
          Próxima
        </button>
      </div>
    </div>
  );
}