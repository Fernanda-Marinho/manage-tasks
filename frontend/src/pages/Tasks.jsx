import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { API_URL } from '../api';

export default function Tasks() {
  const [tasks, setTasks] = useState([]);
  const [meta, setMeta] = useState({});
  const [page, setPage] = useState(1);
  const navigate = useNavigate();

  const fetchTasks = async (currentPage) => {
    const res = await fetch(`${API_URL}/tasks?page=${currentPage}&per_page=5`);
    const data = await res.json();
    if (res.ok) {
      setTasks(data.tasks);
      setMeta(data.meta);
    }
  };

  useEffect(() => {
    fetchTasks(page);
  }, [page]);

  const handleDelete = async (id) => {
    if (window.confirm("Deseja realmente deletar?")) {
      await fetch(`${API_URL}/tasks/${id}`, { method: 'DELETE' });
      fetchTasks(page);
    }
  };

  return (
    <div>
      <div className="header-actions">
        <button onClick={() => navigate('/')} className="btn-back">Voltar para Home</button>
        <button onClick={() => navigate('/tasks/new')} className="btn-success">Nova Tarefa</button>
      </div>
      
      <h2>Lista de Tarefas</h2>
      
      <div className="task-list">
        {tasks.map(task => (
          <div key={task.id} className="task-card">
            <h3>{task.title}</h3>
            <span className={`badge ${task.status.toLowerCase()}`}>{task.status}</span>
            <div className="card-actions">
              <button onClick={() => navigate(`/tasks/view/${task.id}`)} className="btn-primary">Visualizar</button>
              <button onClick={() => navigate(`/tasks/edit/${task.id}`)} className="btn-secondary">Editar</button>
              <button onClick={() => handleDelete(task.id)} className="btn-danger">Deletar</button>
            </div>
          </div>
        ))}
        {tasks.length === 0 && <p>Nenhuma tarefa encontrada.</p>}
      </div>

      <div className="pagination">
        <button 
          disabled={page === 1} 
          onClick={() => setPage(page - 1)}>
          Anterior
        </button>
        <span>Página {meta.page} de {meta.total_pages || 1}</span>
        <button 
          disabled={page === meta.total_pages || !meta.total_pages} 
          onClick={() => setPage(page + 1)}>
          Próxima
        </button>
      </div>
    </div>
  );
}