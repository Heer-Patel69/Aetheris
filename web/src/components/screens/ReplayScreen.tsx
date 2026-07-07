import { RotateCcw, Play, CheckCircle2, AlertOctagon, CornerDownRight, FileEdit, FileJson } from 'lucide-react'
import StatusBadge from '../widgets/StatusBadge'
import { useAetheris } from '../../context/AetherisContext'

export default function ReplayScreen() {
  const { replay } = useAetheris();

  return (
    <div className="animate-in">
      <div className="screen-header">
        <h1 className="screen-title">Engineering Replay System</h1>
        <p className="screen-subtitle">Reconstruct execution history, prompt triggers, capability mappings, and workspace modifications</p>
      </div>

      <div className="section-card">
        <div className="section-card-title">
          <RotateCcw size={18} />
          Active Execution Lifecycle Logs
        </div>

        {replay.length > 0 ? (
          <div style={{ position: 'relative', paddingLeft: '24px', borderLeft: '2px solid var(--border-default)' }}>
            {replay.map((step) => (
              <div key={step.step_number} style={{ marginBottom: 'var(--space-xl)', position: 'relative' }}>
                {/* Dot */}
                <div
                  style={{
                    position: 'absolute',
                    left: '-31px',
                    top: '2px',
                    width: '12px',
                    height: '12px',
                    borderRadius: '50%',
                    background: step.status === 'success' ? 'var(--accent-success)' : 'var(--accent-warning)',
                    border: '3px solid var(--bg-primary)',
                    boxShadow: step.status === 'success' ? 'var(--glow-success)' : 'none'
                  }}
                />

                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 'var(--space-xs)' }}>
                  <span style={{ fontSize: '13px', fontWeight: 700, color: 'var(--text-primary)' }}>
                    Step {step.step_number}: {step.stage}
                  </span>
                  <span style={{ fontSize: '11px', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
                    {step.timestamp}
                  </span>
                </div>

                <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '8px' }}>
                  {step.description}
                </p>

                {/* Subdetails */}
                <div style={{ background: 'var(--bg-secondary)', padding: '12px', borderRadius: 'var(--radius-md)', border: 'var(--border-subtle)' }}>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', fontSize: '12px' }}>
                    <div style={{ display: 'flex', gap: '8px' }}>
                      <span style={{ color: 'var(--text-muted)', width: '130px' }}>Models Utilized:</span>
                      <span className="mono">{step.models_used.join(', ')}</span>
                    </div>
                    {step.selected_capabilities.length > 0 && (
                      <div style={{ display: 'flex', gap: '8px' }}>
                        <span style={{ color: 'var(--text-muted)', width: '130px' }}>Capabilities:</span>
                        <div style={{ display: 'flex', gap: '4px', flexWrap: 'wrap' }}>
                          {step.selected_capabilities.map((c, i) => (
                            <StatusBadge key={i} status="info" label={c} />
                          ))}
                        </div>
                      </div>
                    )}
                    {step.loaded_skills.length > 0 && (
                      <div style={{ display: 'flex', gap: '8px' }}>
                        <span style={{ color: 'var(--text-muted)', width: '130px' }}>Loaded Skills:</span>
                        <div style={{ display: 'flex', gap: '4px', flexWrap: 'wrap' }}>
                          {step.loaded_skills.map((s, i) => (
                            <StatusBadge key={i} status="neutral" label={s} />
                          ))}
                        </div>
                      </div>
                    )}
                    {step.files_modified.length > 0 && (
                      <div style={{ display: 'flex', gap: '8px', alignItems: 'flex-start' }}>
                        <span style={{ color: 'var(--text-muted)', width: '130px', display: 'flex', alignItems: 'center', gap: '4px' }}>
                          <FileEdit size={12} /> Modifications:
                        </span>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }} className="mono">
                          {step.files_modified.map((file, i) => (
                            <span key={i} style={{ color: 'var(--accent-cyan)' }}>{file}</span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="no-data">
            <p>No replay steps captured in this session.</p>
          </div>
        )}
      </div>
    </div>
  );
}
