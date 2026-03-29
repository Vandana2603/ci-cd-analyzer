import { useState, useEffect } from 'react';
import { getHistory, getAnalysis } from '../utils/api';
import toast from 'react-hot-toast';

function CategoryBadge({ category }) {
  return <span className={`badge badge-${category || 'unknown'}`}>{category || 'unknown'}</span>;
}

function DetailModal({ item, onClose }) {
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getAnalysis(item.analysis_id)
      .then(setAnalysis)
      .catch(() => toast.error('Failed to load analysis'))
      .finally(() => setLoading(false));
  }, [item.analysis_id]);

  return (
    <div style={{
      position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.75)',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      zIndex: 1000, padding: 24,
    }} onClick={onClose}>
      <div
        style={{
          background: 'var(--bg-surface)', border: '1px solid var(--border)',
          borderRadius: 'var(--radius-lg)', padding: 28, width: '100%', maxWidth: 680,
          maxHeight: '85vh', overflow: 'auto',
        }}
        onClick={e => e.stopPropagation()}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 20 }}>
          <h2 style={{ fontSize: 18, flex: 1 }}>Analysis #{item.analysis_id}</h2>
          <CategoryBadge category={item.failure_category} />
          <button className="btn btn-ghost" style={{ padding: '6px 12px' }} onClick={onClose}>✕</button>
        </div>

        {loading ? (
          <div style={{ display: 'flex', justifyContent: 'center', padding: 40 }}>
            <div className="spinner" />
          </div>
        ) : analysis ? (
          <>
            <div className="analysis-section">
              <div className="section-title">📋 Summary</div>
              <div className="card" style={{ fontSize: 13, lineHeight: 1.7 }}>{analysis.summary}</div>
            </div>
            <div className="analysis-section">
              <div className="section-title">🔍 Root Cause</div>
              <div className="card" style={{ borderLeft: '3px solid var(--danger)', fontSize: 13, lineHeight: 1.7 }}>
                {analysis.root_cause}
              </div>
            </div>
            <div className="analysis-section">
              <div className="section-title">🛠 Fixes</div>
              {analysis.suggested_fixes?.map((fix, i) => (
                <div key={i} className="fix-item">
                  <span className="fix-num">#{i+1}</span>
                  <span>{fix}</span>
                </div>
              ))}
            </div>
          </>
        ) : <p style={{ color: 'var(--text-muted)' }}>Could not load analysis.</p>}
      </div>
    </div>
  );
}

export default function HistoryPage() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState(null);

  useEffect(() => {
    getHistory(0, 50)
      .then(setHistory)
      .catch(() => toast.error('Failed to load history'))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return (
    <div style={{ display: 'flex', justifyContent: 'center', padding: 80 }}>
      <div className="spinner" style={{ width: 32, height: 32 }} />
    </div>
  );

  return (
    <div>
      <div className="page-header">
        <h1>History</h1>
        <p>All past CI/CD failure analyses with feedback tracking</p>
      </div>
      <div className="page-body">
        {history.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">📜</div>
            <h3 style={{ fontFamily: 'var(--font-display)', fontSize: 16, color: 'var(--text-secondary)' }}>No analyses yet</h3>
            <p>Analyze your first log to see history here</p>
          </div>
        ) : (
          <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
            <table className="history-table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>File</th>
                  <th>Category</th>
                  <th>Summary</th>
                  <th>Root Cause</th>
                  <th>Feedback</th>
                  <th>Date</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {history.map((item) => {
                  const accuracy = item.feedback_count > 0
                    ? Math.round((item.correct_feedback_count / item.feedback_count) * 100)
                    : null;
                  return (
                    <tr key={item.analysis_id}>
                      <td style={{ color: 'var(--text-muted)', width: 40 }}>{item.analysis_id}</td>
                      <td style={{ maxWidth: 120, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', color: 'var(--text-secondary)' }}>
                        {item.filename || '—'}
                      </td>
                      <td><CategoryBadge category={item.failure_category} /></td>
                      <td style={{ maxWidth: 200, fontSize: 12, color: 'var(--text-secondary)' }}>
                        {item.summary?.slice(0, 80)}{item.summary?.length > 80 ? '…' : ''}
                      </td>
                      <td style={{ maxWidth: 180, fontSize: 12, color: 'var(--text-secondary)' }}>
                        {item.root_cause?.slice(0, 70)}{item.root_cause?.length > 70 ? '…' : ''}
                      </td>
                      <td>
                        {item.feedback_count > 0 ? (
                          <span style={{ fontSize: 12, color: accuracy >= 70 ? 'var(--success)' : 'var(--warning)' }}>
                            {accuracy}% ({item.correct_feedback_count}/{item.feedback_count})
                          </span>
                        ) : (
                          <span style={{ color: 'var(--text-muted)', fontSize: 12 }}>No feedback</span>
                        )}
                      </td>
                      <td style={{ color: 'var(--text-muted)', fontSize: 11, whiteSpace: 'nowrap' }}>
                        {new Date(item.created_at).toLocaleDateString()}
                      </td>
                      <td>
                        <button className="btn btn-ghost" style={{ padding: '5px 12px', fontSize: 11 }} onClick={() => setSelected(item)}>
                          View
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
      {selected && <DetailModal item={selected} onClose={() => setSelected(null)} />}
    </div>
  );
}
