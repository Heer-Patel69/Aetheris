import { Activity, Cpu, HardDrive, Zap } from 'lucide-react'
import { useAetheris } from '../../context/AetherisContext'

export default function Inspector() {
  const { runtime } = useAetheris();

  return (
    <aside className="inspector">
      <div className="inspector-section">
        <div className="inspector-title">Runtime Inspector</div>

        <div className="inspector-row">
          <span className="inspector-label">Brain State</span>
          <span className="inspector-value">{runtime?.brain_state ?? '—'}</span>
        </div>
        <div className="inspector-row">
          <span className="inspector-label">Workflow</span>
          <span className="inspector-value">{runtime?.workflow_phase ?? '—'}</span>
        </div>
        <div className="inspector-row">
          <span className="inspector-label">Engines</span>
          <span className="inspector-value">
            {runtime ? `${runtime.engines_online}/${runtime.total_engines}` : '—'}
          </span>
        </div>
        <div className="inspector-row">
          <span className="inspector-label">Branch</span>
          <span className="inspector-value">{runtime?.current_branch ?? '—'}</span>
        </div>
      </div>

      <div className="inspector-section">
        <div className="inspector-title">System</div>
        <div className="inspector-row">
          <span className="inspector-label"><Activity size={12} /> CPU</span>
          <span className="inspector-value">—</span>
        </div>
        <div className="inspector-row">
          <span className="inspector-label"><HardDrive size={12} /> RAM</span>
          <span className="inspector-value">—</span>
        </div>
        <div className="inspector-row">
          <span className="inspector-label"><Cpu size={12} /> GPU</span>
          <span className="inspector-value">—</span>
        </div>
        <div className="inspector-row">
          <span className="inspector-label"><Zap size={12} /> Events/s</span>
          <span className="inspector-value">—</span>
        </div>
      </div>

      <div className="inspector-section">
        <div className="inspector-title">Active Context</div>
        <div className="no-data" style={{ padding: '16px 0' }}>
          No execution in progress
        </div>
      </div>
    </aside>
  );
}
