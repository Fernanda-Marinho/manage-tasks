import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';

export default function CategoryForm() {
  const [name, setName] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    await fetch('/api/categories', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name })
    });
    navigate('/categories');
  };

  return (
    <div>
      <h2>Nova Categoria</h2>
      <form onSubmit={handleSubmit}>
        <input required type="text" placeholder="Nome da Categoria" value={name} onChange={e => setName(e.target.value)} />
        <div>
          <button type="submit" className="btn btn-primary">Salvar</button>
          <Link to="/categories" className="btn btn-secondary">Cancelar</Link>
        </div>
      </form>
    </div>
  );
}