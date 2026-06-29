import { useNavigate } from 'react-router-dom';

export default function Home() {
  const navigate = useNavigate();

  return (
    <div className="home-container">
      <h2>Gerenciador de Tarefas</h2>
      <p>Selecione uma opção para começar:</p>
      <div className="button-group-large">
        <button onClick={() => navigate('/tasks')} className="btn-primary">Tarefas</button>
        <button onClick={() => navigate('/categories')} className="btn-secondary">Categorias</button>
      </div>
    </div>
  );
}