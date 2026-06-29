import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { API_URL } from '../api';

const STATUS_LABELS = {
  PENDING: 'Pendente',
  IN_PROGRESS: 'Em Progresso',
  DONE: 'Concluída',
};

export default function TaskView() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [task, setTask] = useState(null);
  const [categories, setCategories] = useState([]);

  useEffect(() => {
    Promise.all([
      fetch(`${API_URL}/tasks/${id}`).then(res => res.json()),
      fetch(`${API_URL}/categories`).then(res => res.json()),
    ]).then(([taskData, categoriesData]) => {
      setTask(taskData);
      setCategories(categoriesData);
    });
  }, [id]);

  if (!task) return <p>Carregando...</p>;

  const categoryName = categories.find(cat => cat.id === task.category_id)?.name;

  return (
    <div className="view-container">
      <button onClick={() => navigate('/tasks')} className="btn-back">Voltar para Tarefas</button>
      <h2>Visualizar Tarefa</h2>
      
      <div className="task-details">
        <p><strong>ID:</strong> {task.id}</p>
        <p><strong>Título:</strong> {task.title}</p>
        <p><strong>Status:</strong> <span className={`badge ${task.status.toLowerCase()}`}>{STATUS_LABELS[task.status] || task.status}</span></p>
        <p><strong>Descrição:</strong> {task.description || 'Sem descrição'}</p>
        <p><strong>Categoria:</strong> {categoryName || 'Nenhuma'}</p>
        <p><strong>Criado em:</strong> {new Date(task.created_at).toLocaleString()}</p>
        {task.updated_at && (
          <p><strong>Atualizado em:</strong> {new Date(task.updated_at).toLocaleString()}</p>
        )}
      </div>
    </div>
  );
}