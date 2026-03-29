import { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import toast from 'react-hot-toast';
import { uploadAndAnalyze, submitFeedback } from '../utils/api';
import { SAMPLE_LOGS } from '../utils/sampleLogs';

function CategoryBadge({ category }) {
  return <span className={`badge badge-${category || 'unknown'}`}>{category || 'unknown'}</span>;
}

function AnalysisResult({ result, onFeedback }) {
  const [feedbackGiven, setFeedbackGiven] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  const handleFeedback = async (isCorrect) => {
    setSubmitting(true);
    try {
      await submitFeedback(result.analysis_id, isCorrect);
      setFeedbackGiven(isCorrect);
      onFeedback && onFeedback(isCorrect);
      toast.success(isCorrect ? '✅ Marked as helpful!' : '📝 Feedback recorded');
    } catch (e) {
      toast.error('Failed to submit feedback');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div style={{ marginTop: 28 }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 20 }}>
        <CategoryBadge category={result.failure_category} />
        <span style={{ color: 'var(--text-muted)', fontSize: 12 }}>
          Analysis #{result.analysis_id} · Log #{result.log_entry_id}
        </span>
      </div>

      {/* Summary */}
      <div className="analysis-section">
        <div className="section-title">📋 Summary</div>
        <div className="card" style={{ fontSize: 13, lineHeight: 1.7 }}>
          {result.summary}
        </div>
      </div>

      {/* Root Cause */}
      <div className="analysis-section">
        <div className="section-title">🔍 Root Cause</div>
        <div className="card" style={{
          borderLeft: '3px solid var(--danger)',
          fontSize: 13, lineHeight: 1.7,
        }}>
          {result.root_cause}
        </div>
      </div>

      {/* Fixes */}
      <div className="analysis-section">
        <div className="section-title">🛠 Suggested Fixes</div>
        {result.suggested_fixes?.map((fix, i) => (
          <div key={i} className="fix-item">
            <span className="fix-num">#{i + 1}</span>
            <span>{fix}</span>
          </div>
        ))}
      </div>

      {/* Similar Issues */}
      {result.similar_issues?.length > 0 && (
        <div className="analysis-section">
          <div className="section-title">🔗 Similar Past Issues</div>
          {result.similar_issues.map((issue, i) => (
            <div key={i} className="similar-card">
              <div className="sim-score">
                ⭐ {(issue.similarity_score * 100).toFixed(0)}% match
                {issue.feedback_score > 0 && <span style={{ color: 'var(--success)', marginLeft: 8 }}>+{issue.feedback_score} feedback</span>}
              </div>
              <div style={{ fontSize: 12, color: 'var(--text-secondary)', marginBottom: 4 }}>
                {issue.summary}
              </div>
              <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                <strong style={{ color: 'var(--text-secondary)' }}>Root:</strong> {issue.root_cause}
              </div>
              {issue.fixes?.length > 0 && (
                <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 6 }}>
                  Fix: {issue.fixes[0]}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Feedback */}
      <div className="feedback-row">
        <span>Was this analysis helpful?</span>
        {feedbackGiven === null ? (
          <>
            <button
              className="btn btn-success"
              onClick={() => handleFeedback(true)}
              disabled={submitting}
              style={{ padding: '7px 14px', fontSize: 12 }}
            >
              👍 Yes
            </button>
            <button
              className="btn btn-danger"
              onClick={() => handleFeedback(false)}
              disabled={submitting}
              style={{ padding: '7px 14px', fontSize: 12 }}
            >
              👎 No
            </button>
          </>
        ) : (
          <span style={{ color: feedbackGiven ? 'var(--success)' : 'var(--danger)', fontSize: 12, fontWeight: 700 }}>
            {feedbackGiven ? '✅ Marked helpful' : '📝 Feedback recorded'}
          </span>
        )}
      </div>
    </div>
  );
}

export default function AnalyzePage() {
  const [logText, setLogText] = useState('');
  const [filename, setFilename] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [inputMode, setInputMode] = useState('paste'); // 'paste' | 'upload'

  const onDrop = useCallback((files) => {
    const f = files[0];
    if (!f) return;
    setFilename(f.name);
    const reader = new FileReader();
    reader.onload = (e) => setLogText(e.target.result);
    reader.readAsText(f);
    setInputMode('paste');
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'text/plain': ['.txt', '.log', '.out'] },
    multiple: false,
  });

  const handleAnalyze = async () => {
    if (!logText.trim()) { toast.error('Please paste or upload a log first'); return; }
    setLoading(true);
    setResult(null);
    try {
      const formData = new FormData();
      formData.append('raw_log', logText);
      const data = await uploadAndAnalyze(formData);
      setResult(data);
      toast.success('Analysis complete!');
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Analysis failed. Is the backend running?');
    } finally {
      setLoading(false);
    }
  };

  const loadSample = (type) => {
    setLogText(SAMPLE_LOGS[type]);
    setFilename(`sample_${type}_failure.log`);
    setResult(null);
    toast.success(`Loaded ${type} failure sample`);
  };

  return (
    <div>
      <div className="page-header">
        <h1>Analyze Log</h1>
        <p>Upload or paste a CI/CD log to get AI-powered failure analysis with RAG context</p>
      </div>
      <div className="page-body">
        <div className="two-col">
          {/* Left: Input */}
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 14 }}>
              <div className="tabs">
                <button className={`tab-btn ${inputMode === 'paste' ? 'active' : ''}`} onClick={() => setInputMode('paste')}>Paste Log</button>
                <button className={`tab-btn ${inputMode === 'upload' ? 'active' : ''}`} onClick={() => setInputMode('upload')}>Upload File</button>
              </div>
              <div style={{ flex: 1 }} />
              <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>Samples:</span>
              {['build', 'test', 'infrastructure'].map(t => (
                <button key={t} className="btn btn-ghost" style={{ padding: '4px 10px', fontSize: 11 }} onClick={() => loadSample(t)}>
                  {t}
                </button>
              ))}
            </div>

            {inputMode === 'upload' ? (
              <div {...getRootProps()} className={`dropzone ${isDragActive ? 'active' : ''}`}>
                <input {...getInputProps()} />
                <div className="dz-icon">📂</div>
                <h3>Drop log file here</h3>
                <p>or click to browse · .txt, .log, .out</p>
              </div>
            ) : (
              <textarea
                rows={16}
                placeholder={"Paste your CI/CD log here...\n\nExample:\n[ERROR] BUILD FAILURE\n[ERROR] Failed to execute goal...\nException: Cannot find symbol"}
                value={logText}
                onChange={e => { setLogText(e.target.value); setResult(null); }}
                style={{ fontFamily: 'var(--font-mono)' }}
              />
            )}

            {filename && (
              <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 6 }}>
                📄 {filename}
              </div>
            )}

            <div style={{ marginTop: 14, display: 'flex', gap: 10 }}>
              <button
                className="btn btn-primary"
                onClick={handleAnalyze}
                disabled={loading || !logText.trim()}
                style={{ flex: 1, justifyContent: 'center' }}
              >
                {loading ? <><div className="spinner" style={{ width: 16, height: 16 }} /> Analyzing...</> : '⚡ Analyze Failure'}
              </button>
              <button className="btn btn-ghost" onClick={() => { setLogText(''); setResult(null); setFilename(''); }}>
                Clear
              </button>
            </div>
          </div>

          {/* Right: Result */}
          <div>
            {result ? (
              <AnalysisResult result={result} />
            ) : (
              <div className="empty-state" style={{ border: '1px dashed var(--border)', borderRadius: 'var(--radius-lg)', minHeight: 400 }}>
                <div className="empty-icon">🔬</div>
                <h3 style={{ fontFamily: 'var(--font-display)', fontSize: 16, color: 'var(--text-secondary)' }}>Analysis will appear here</h3>
                <p>Paste a log and click Analyze</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
