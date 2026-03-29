import { useState, useEffect } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, LineChart, Line, CartesianGrid, Legend,
} from 'recharts';
import { getMetrics } from '../utils/api';
import toast from 'react-hot-toast';

const CATEGORY_COLORS = {
  build: '#f97316',
  test: '#a855f7',
  infrastructure: '#06b6d4',
  unknown: '#4a5568',
};

const CHART_TOOLTIP_STYLE = {
  background: '#181c24',
  border: '1px solid #252b38',
  borderRadius: 8,
  color: '#e8eaf0',
  fontFamily: 'Space Mono, monospace',
  fontSize: 12,
};

export default function MetricsPage() {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);

  const loadMetrics = () => {
    setLoading(true);
    getMetrics()
      .then(setMetrics)
      .catch(() => toast.error('Failed to load metrics'))
      .finally(() => setLoading(false));
  };

  useEffect(() => { loadMetrics(); }, []);

  if (loading) return (
    <div style={{ display: 'flex', justifyContent: 'center', padding: 80 }}>
      <div className="spinner" style={{ width: 32, height: 32 }} />
    </div>
  );

  if (!metrics) return null;

  const pieData = Object.entries(metrics.failure_breakdown || {}).map(([name, value]) => ({
    name, value,
  }));

  const accuracyPct = Math.round((metrics.accuracy_rate || 0) * 100);

  return (
    <div>
      <div className="page-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <h1 style={{ flex: 1 }}>Metrics</h1>
          <button className="btn btn-ghost" style={{ fontSize: 12 }} onClick={loadMetrics}>
            ↻ Refresh
          </button>
        </div>
        <p>System performance, failure patterns, and feedback analytics</p>
      </div>
      <div className="page-body">

        {/* Stat cards */}
        <div className="stat-grid">
          <div className="stat-card">
            <div className="stat-value">{metrics.total_analyses}</div>
            <div className="stat-label">Total Analyses</div>
          </div>
          <div className={`stat-card ${accuracyPct >= 70 ? 'success' : 'warning'}`}>
            <div className="stat-value">{accuracyPct}%</div>
            <div className="stat-label">Accuracy Rate</div>
          </div>
          <div className="stat-card purple">
            <div className="stat-value">{metrics.avg_fixes_per_analysis}</div>
            <div className="stat-label">Avg Fixes / Analysis</div>
          </div>
          <div className="stat-card warning">
            <div className="stat-value">{pieData.length}</div>
            <div className="stat-label">Failure Categories</div>
          </div>
        </div>

        {/* Charts row */}
        <div className="two-col" style={{ marginBottom: 24 }}>

          {/* Weekly trend */}
          <div className="card">
            <div className="card-label">📈 Weekly Trend (last 7 days)</div>
            {metrics.weekly_trend?.every(d => d.count === 0) ? (
              <div className="empty-state" style={{ padding: 40 }}>
                <p>No data yet</p>
              </div>
            ) : (
              <ResponsiveContainer width="100%" height={200}>
                <LineChart data={metrics.weekly_trend} margin={{ top: 8, right: 8, bottom: 0, left: -20 }}>
                  <CartesianGrid stroke="#252b38" strokeDasharray="3 3" />
                  <XAxis dataKey="date" tick={{ fill: '#4a5568', fontSize: 10 }} tickFormatter={d => d.slice(5)} />
                  <YAxis tick={{ fill: '#4a5568', fontSize: 10 }} allowDecimals={false} />
                  <Tooltip contentStyle={CHART_TOOLTIP_STYLE} />
                  <Line type="monotone" dataKey="count" stroke="#3b82f6" strokeWidth={2} dot={{ fill: '#3b82f6', r: 3 }} />
                </LineChart>
              </ResponsiveContainer>
            )}
          </div>

          {/* Failure breakdown pie */}
          <div className="card">
            <div className="card-label">🥧 Failure Breakdown</div>
            {pieData.length === 0 ? (
              <div className="empty-state" style={{ padding: 40 }}>
                <p>No data yet</p>
              </div>
            ) : (
              <div style={{ display: 'flex', alignItems: 'center', gap: 20 }}>
                <ResponsiveContainer width="60%" height={200}>
                  <PieChart>
                    <Pie data={pieData} cx="50%" cy="50%" innerRadius={50} outerRadius={80} dataKey="value" paddingAngle={3}>
                      {pieData.map((entry) => (
                        <Cell key={entry.name} fill={CATEGORY_COLORS[entry.name] || '#4a5568'} />
                      ))}
                    </Pie>
                    <Tooltip contentStyle={CHART_TOOLTIP_STYLE} />
                  </PieChart>
                </ResponsiveContainer>
                <div style={{ flex: 1 }}>
                  {pieData.map(entry => (
                    <div key={entry.name} style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
                      <div style={{ width: 10, height: 10, borderRadius: 2, background: CATEGORY_COLORS[entry.name] || '#4a5568', flexShrink: 0 }} />
                      <span style={{ fontSize: 12, color: 'var(--text-secondary)', textTransform: 'capitalize' }}>{entry.name}</span>
                      <span style={{ marginLeft: 'auto', fontSize: 12, fontWeight: 700 }}>{entry.value}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Top root cause terms + accuracy bar */}
        <div className="two-col">
          <div className="card">
            <div className="card-label">🔑 Top Root Cause Terms</div>
            {metrics.top_root_causes?.length === 0 ? (
              <div className="empty-state" style={{ padding: 32 }}><p>No data yet</p></div>
            ) : (
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={metrics.top_root_causes} layout="vertical" margin={{ top: 0, right: 16, bottom: 0, left: 60 }}>
                  <XAxis type="number" tick={{ fill: '#4a5568', fontSize: 10 }} />
                  <YAxis type="category" dataKey="term" tick={{ fill: '#8892a4', fontSize: 11 }} width={60} />
                  <Tooltip contentStyle={CHART_TOOLTIP_STYLE} />
                  <Bar dataKey="count" fill="#3b82f6" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>

          <div className="card">
            <div className="card-label">📊 System Health</div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 16, paddingTop: 8 }}>
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12, marginBottom: 6 }}>
                  <span style={{ color: 'var(--text-secondary)' }}>Suggestion Accuracy</span>
                  <span style={{ color: accuracyPct >= 70 ? 'var(--success)' : 'var(--warning)' }}>{accuracyPct}%</span>
                </div>
                <div className="progress-bar">
                  <div className={`progress-fill ${accuracyPct >= 70 ? 'success' : 'warning'}`} style={{ width: `${accuracyPct}%` }} />
                </div>
              </div>

              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12, marginBottom: 6 }}>
                  <span style={{ color: 'var(--text-secondary)' }}>RAG Coverage</span>
                  <span style={{ color: 'var(--accent)' }}>{Math.min(100, metrics.total_analyses * 10)}%</span>
                </div>
                <div className="progress-bar">
                  <div className="progress-fill" style={{ width: `${Math.min(100, metrics.total_analyses * 10)}%` }} />
                </div>
              </div>

              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12, marginBottom: 6 }}>
                  <span style={{ color: 'var(--text-secondary)' }}>Avg Fix Quality</span>
                  <span style={{ color: '#a855f7' }}>{Math.min(100, Math.round(metrics.avg_fixes_per_analysis / 5 * 100))}%</span>
                </div>
                <div className="progress-bar">
                  <div className="progress-fill" style={{ width: `${Math.min(100, Math.round(metrics.avg_fixes_per_analysis / 5 * 100))}%`, background: '#a855f7' }} />
                </div>
              </div>

              <div style={{ borderTop: '1px solid var(--border)', paddingTop: 12 }}>
                <div className="card-label" style={{ marginBottom: 6 }}>Most Common Failure</div>
                <div>
                  {pieData.length > 0 ? (
                    <span className={`badge badge-${pieData.sort((a,b) => b.value - a.value)[0]?.name}`}>
                      {pieData.sort((a,b) => b.value - a.value)[0]?.name}
                    </span>
                  ) : <span style={{ color: 'var(--text-muted)', fontSize: 12 }}>N/A</span>}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
