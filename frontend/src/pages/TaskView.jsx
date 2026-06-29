import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { API_URL } from '../api';

export default function TaskView() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [task, setTask] = useState(null);

  useEffect(() => {
    fetch(`${API_URL}/tasks/${id}`)
      .then(res => res.json())
      .then(data => setTask(data));
  }, [id]);

  if (!task) return <p>Carregando...</p>;

  return (
    <div className="view-container">
      <button onClick={() => navigate('/tasks')} className="btn-back">Voltar para Tarefas</button>
      <h2>Visualizar Tarefa</h2>
      
      <div className="task-details">
        <p><strong>ID:</strong> {task.id}</p>
        <p><strong>Título:</strong> {task.title}</p>
        <p><strong>Status:</strong> <span className={`badge ${task.status.toLowerCase()}`}>{task.status}</span></p>
        <p><strong>Descrição:</strong> {task.description || 'Sem descrição'}</p>
        <p><strong>ID da Categoria:</strong> {task.category_id || 'Nenhuma'}</p>
        <p><strong>Criado em:</strong> {new Date(task.created_at).toLocaleString()}</p>
      </div>
    </div>
  );
}