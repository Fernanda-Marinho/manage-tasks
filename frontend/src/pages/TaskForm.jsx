import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { API_URL } from '../api';

export default function TaskForm() {
  const { id } = useParams();
  const navigate = useNavigate();
  const isEditing = Boolean(id);

  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [status, setStatus] = useState('PENDING');
  const [categoryId, setCategoryId] = useState('');
  const [categories, setCategories] = useState([]);
  const [successMessage, setSuccessMessage] = useState('');

  useEffect(() => {
    fetch(`${API_URL}/categories`)
      .then(res => res.json())
      .then(data => setCategories(data));

    if (isEditing) {
      fetch(`${API_URL}/tasks/${id}`)
        .then(res => res.json())
        .then(data => {
          setTitle(data.title);
          setDescription(data.description || '');
          setStatus(data.status);
          setCategoryId(data.category_id || '');
        });
    }
  }, [id, isEditing]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const payload = {
      title,
      description,
      status,
      category_id: categoryId ? parseInt(categoryId) : null
    };

    const url = isEditing ? `${API_URL}/tasks/${id}` : `${API_URL}/tasks`;
    const method = isEditing ? 'PUT' : 'POST';

    const res = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (res.ok) {
      if (isEditing) {
        navigate('/tasks');
      } else {
        setTitle('');
        setDescription('');
        setStatus('PENDING');
        setCategoryId('');
        setSuccessMessage('Tarefa criada com sucesso!');
        setTimeout(() => setSuccessMessage(''), 1000);
      }
    } else {
      const error = await res.json();
      alert(error.error || "Erro ao salvar");
    }
  };

  return (
    <div>
      <button onClick={() => navigate('/tasks')} className="btn-back">Voltar</button>
      <h2>{isEditing ? 'Editar Tarefa' : 'Nova Tarefa'}</h2>

      {successMessage && (
        <div className="alert-success">{successMessage}</div>
      )}
      
      <form onSubmit={handleSubmit} className="form-vertical">
        <label>Título:</label>
        <input 
          type="text" 
          value={title} 
          onChange={(e) => setTitle(e.target.value)} 
          required 
        />

        <label>Descrição:</label>
        <textarea 
          value={description} 
          onChange={(e) => setDescription(e.target.value)} 
        />

        <label>Status:</label>
        <select value={status} onChange={(e) => setStatus(e.target.value)}>
          <option value="PENDING">Pendente</option>
          <option value="IN_PROGRESS">Em Progresso</option>
          <option value="DONE">Concluída</option>
        </select>

        <label>Categoria (Opcional):</label>
        <select value={categoryId} onChange={(e) => setCategoryId(e.target.value)}>
          <option value="">Nenhuma</option>
          {categories.map(cat => (
            <option key={cat.id} value={cat.id}>{cat.name}</option>
          ))}
        </select>

        <button type="submit" className="btn-success">Salvar Tarefa</button>
      </form>
    </div>
  );
}