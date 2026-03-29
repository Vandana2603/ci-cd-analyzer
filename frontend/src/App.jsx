import { useState } from 'react';
import { Toaster } from 'react-hot-toast';
import AnalyzePage from './pages/AnalyzePage';
import HistoryPage from './pages/HistoryPage';
import MetricsPage from './pages/MetricsPage';

const NAV = [
  { id: 'analyze', label: 'Analyze', icon: '⚡' },
  { id: 'history', label: 'History', icon: '📜' },
  { id: 'metrics', label: 'Metrics', icon: '📊' },
];

export default function App() {
  const [page, setPage] = useState('analyze');

  const renderPage = () => {
    switch (page) {
      case 'analyze': return <AnalyzePage />;
      case 'history': return <HistoryPage />;
      case 'metrics': return <MetricsPage />;
      default: return <AnalyzePage />;
    }
  };

  return (
    <>
      <Toaster
        position="top-right"
        toastOptions={{
          style: {
            background: '#181c24', color: '#e8eaf0',
            border: '1px solid #252b38',
            fontFamily: 'Space Mono, monospace', fontSize: 13,
          },
        }}
      />
      <div className="app-shell">
        <aside className="sidebar">
          <div className="sidebar-logo">
            <div className="logo-icon">🔬</div>
            <h2>CI/CD Analyzer</h2>
            <span>LLM + RAG Engine</span>
          </div>
          <nav>
            {NAV.map(item => (
              <div
                key={item.id}
                className={`nav-item ${page === item.id ? 'active' : ''}`}
                onClick={() => setPage(item.id)}
              >
                <span>{item.icon}</span>
                <span>{item.label}</span>
              </div>
            ))}
          </nav>
          <div style={{ flex: 1 }} />
          <div style={{ padding: '16px 20px', borderTop: '1px solid var(--border)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <span className="dot-live" />
              <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>Backend connected</span>
            </div>
          </div>
        </aside>
        <main className="main-content">
          {renderPage()}
        </main>
      </div>
    </>
  );
}
