import { RotateCcw, Play, CheckCircle2, AlertOctagon, CornerDownRight, FileEdit, FileJson, Calendar, Activity, Square, RefreshCw } from 'lucide-react'
import StatusBadge from '../widgets/StatusBadge'
import { useAetheris } from '../../context/AetherisContext'

export default function ReplayScreen() {
  const { 
    replay, 
    sessions, 
    replayMode, 
    replayProgress, 
    replayTotal, 
    startReplay, 
    stopReplay, 
    fetchSessions 
  } = useAetheris();

  return (
    <div className="animate-in">
      <div className="screen-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 className="screen-title">Engineering Replay System</h1>
          <p className="screen-subtitle">Reconstruct execution history, prompt triggers, capability mappings, and workspace modifications</p>
        </div>
        {!replayMode && (
          <button className="btn-secondary" onClick={fetchSessions} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <RefreshCw size={14} /> Refresh Sessions
          </button>
        )}
      </div>

      {/* Replay Controls Panel */}
      {replayMode && (
        <div className="section-card" style={{ border: '1px solid var(--accent-cyan)', background: 'rgba(6, 182, 212, 0.05)', marginBottom: 'var(--space-xl)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-md)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <span className="pulse-dot" style={{ backgroundColor: 'var(--accent-cyan)' }} />
              <div>
                <div style={{ fontWeight: 700, color: 'var(--accent-cyan)' }}>REPLAYING ACTIVE SESSION</div>
                <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Reconstructing state projection step-by-step from event ledger</div>
              </div>
            </div>
            <button className="btn-secondary" onClick={stopReplay} style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--accent-danger)' }}>
              <Square size={14} /> Halt Replay
            </button>
          </div>
          
          {/* Progress Bar */}
          <div style={{ height: '6px', background: 'var(--bg-secondary)', borderRadius: '3px', overflow: 'hidden', marginBottom: 'var(--space-xs)' }}>
            <div 
              style={{ 
                height: '100%', 
                background: 'linear-gradient(90deg, var(--accent-primary) 0%, var(--accent-cyan) 100%)', 
                width: `${replayTotal > 0 ? (replayProgress / replayTotal) * 100 : 0}%`,
                transition: 'width 0.2s ease-out'
              }} 
            />
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
            <span>PROGRESS: {replayProgress} / {replayTotal} events applied</span>
            <span>{replayTotal > 0 ? Math.round((replayProgress / replayTotal) * 100) : 0}%</span>
          </div>
        </div>
      )}

      <div className="grid-3" style={{ display: replayMode ? 'block' : 'grid', gap: 'var(--space-xl)', alignItems: 'flex-start' }}>
        
        {/* Sessions list */}
        {!replayMode && (
          <div className="section-card" style={{ gridColumn: 'span 1' }}>
            <div className="section-card-title">
              <Calendar size={18} />
              Session History Store
            </div>
            
            {sessions.length > 0 ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-md)' }}>
                {sessions.map((session) => (
                  <div 
                    key={session.session_id} 
                    style={{ 
                      padding: '12px', 
                      background: 'var(--bg-secondary)', 
                      borderRadius: 'var(--radius-md)', 
                      border: 'var(--border-subtle)',
                      display: 'flex',
                      flexDirection: 'column',
                      gap: '8px'
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                      <span style={{ fontWeight: 700, fontSize: '13px', color: 'var(--text-primary)' }}>
                        {session.project_id}
                      </span>
                      <span className="mono" style={{ fontSize: '10px', color: 'var(--text-muted)' }}>
                        {session.session_id.substring(0, 8)}...
                      </span>
                    </div>
                    
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                        {new Date(session.started * 1000).toLocaleString()}
                      </span>
                      <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                        {session.event_count} events
                      </span>
                    </div>

                    <button 
                      className="btn-primary" 
                      onClick={() => startReplay(session.session_id)}
                      style={{ 
                        display: 'flex', 
                        alignItems: 'center', 
                        justifyContent: 'center', 
                        gap: '6px', 
                        padding: '6px 12px',
                        fontSize: '12px',
                        marginTop: '4px'
                      }}
                    >
                      <Play size={12} fill="currentColor" /> Play Replay
                    </button>
                  </div>
                ))}
              </div>
            ) : (
              <div className="no-data">
                <p>No historical sessions located in events.db.</p>
              </div>
            )}
          </div>
        )}

        {/* Replay Timeline */}
        <div className="section-card" style={{ gridColumn: replayMode ? 'span 3' : 'span 2' }}>
          <div className="section-card-title">
            <Activity size={18} />
            Engineering Event Timeline
          </div>

          {replay.length > 0 ? (
            <div style={{ position: 'relative', paddingLeft: '24px', borderLeft: '2px solid var(--border-default)' }}>
              {replay.map((step, idx) => (
                <div key={idx} style={{ marginBottom: 'var(--space-xl)', position: 'relative' }}>
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
                </div>
              ))}
            </div>
          ) : (
            <div className="no-data">
              <p>Select a historical session on the left to start a replay sequence, or run a new execution to view logs live.</p>
            </div>
          )}
        </div>

      </div>
    </div>
  );
}
