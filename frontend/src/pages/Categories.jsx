import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { API_URL } from '../api';

export default function Categories() {
  const [categories, setCategories] = useState([]);
  const [name, setName] = useState('');
  const navigate = useNavigate();

  const fetchCategories = async () => {
    const res = await fetch(`${API_URL}/categories`);
    const data = await res.json();
    setCategories(data);
  };

  useEffect(() => {
    fetchCategories();
  }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    if (!name.trim()) return alert("O nome é obrigatório");

    const res = await fetch(`${API_URL}/categories`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name })
    });

    if (res.ok) {
      setName('');
      fetchCategories();
    } else {
      const error = await res.json();
      alert(error.error || "Erro ao criar");
    }
  };

  return (
    <div>
      <button onClick={() => navigate('/')} className="btn-back">Voltar para Home</button>
      <h2>Categorias</h2>
      
      <form onSubmit={handleCreate} className="form-inline">
        <input 
          type="text" 
          placeholder="Nova categoria..." 
          value={name} 
          onChange={(e) => setName(e.target.value)} 
        />
        <button type="submit" className="btn-success">Criar Categoria</button>
      </form>

      <ul className="list">
        {categories.map(cat => (
          <li key={cat.id} className="list-item">
            {cat.name}
          </li>
        ))}
        {categories.length === 0 && <p>Nenhuma categoria encontrada.</p>}
      </ul>
    </div>
  );
}