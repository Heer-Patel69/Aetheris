import { Brain, Cpu, Clock, Sparkles, Database, CheckCircle2, XCircle, Gauge } from 'lucide-react'
import MetricCard from '../widgets/MetricCard'
import StatusBadge from '../widgets/StatusBadge'
import { useAetheris } from '../../context/AetherisContext'

export default function BrainScreen() {
  const { brain } = useAetheris();

  return (
    <div className="animate-in">
      <div className="screen-header">
        <h1 className="screen-title">Brain Intelligence</h1>
        <p className="screen-subtitle">Executive Decision Orchestrator state, reasoning metrics, and capability resolution</p>
      </div>

      {/* EDO State */}
      <div className="section-card">
        <div className="section-card-title">
          <Brain size={18} />
          Executive Decision Orchestrator (EDO)
        </div>
        <div className="workflow-steps">
          {['AWAITING_PROMPT', 'PLANNING_PHASE', 'ARCHITECTURE_PHASE', 'EXECUTION_PHASE', 'VERIFICATION_PHASE'].map((phase, i) => {
            const currentIdx = brain?.workflow_phase
              ? ['AWAITING_PROMPT', 'PLANNING_PHASE', 'ARCHITECTURE_PHASE', 'EXECUTION_PHASE', 'VERIFICATION_PHASE'].indexOf(brain.workflow_phase)
              : -1;
            return (
              <span key={phase}>
                <span className={`workflow-step ${i < currentIdx ? 'completed' : i === currentIdx ? 'active' : 'pending'}`}>
                  {phase.replace(/_/g, ' ')}
                </span>
                {i < 4 && <span className="workflow-arrow"> → </span>}
              </span>
            );
          })}
        </div>
      </div>

      {/* Brain Metrics */}
      <div className="grid-4" style={{ marginBottom: 'var(--space-xl)' }}>
        <MetricCard
          label="Decisions Made"
          value={brain?.decisions_made ?? null}
          detail="Total EDO approvals"
          icon={<CheckCircle2 size={14} />}
          accent="var(--accent-success)"
        />
        <MetricCard
          label="Reasoning Latency"
          value={brain?.reasoning_latency_ms ? `${brain.reasoning_latency_ms}ms` : null}
          detail="Average decision time"
          icon={<Clock size={14} />}
          accent="var(--accent-warning)"
        />
        <MetricCard
          label="Capabilities Resolved"
          value={brain?.capabilities_resolved ?? null}
          detail="CRE 3-Level Indexing"
          icon={<Sparkles size={14} />}
          accent="var(--accent-primary)"
        />
        <MetricCard
          label="Memory Retrievals"
          value={brain?.memory_retrievals ?? null}
          detail="EME structured lookups"
          icon={<Database size={14} />}
          accent="var(--accent-cyan)"
        />
      </div>

      {/* Context & Execution */}
      <div className="grid-2">
        <div className="section-card">
          <div className="section-card-title">
            <Gauge size={18} />
            Context Intelligence
          </div>
          <div className="inspector-row">
            <span className="inspector-label">Compression Ratio</span>
            <span className="inspector-value">
              {brain?.context_compression_ratio ? `${(brain.context_compression_ratio * 100).toFixed(1)}%` : '—'}
            </span>
          </div>
          <div className="inspector-row">
            <span className="inspector-label">Execution Success</span>
            <span className="inspector-value">
              {brain?.execution_success_rate ? `${(brain.execution_success_rate * 100).toFixed(1)}%` : '—'}
            </span>
          </div>
        </div>

        <div className="section-card">
          <div className="section-card-title">
            <Cpu size={18} />
            EDO Security Gate
          </div>
          <div style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '12px' }}>
            The EDO blocks all execution until the engineering workflow is complete.
          </div>
          <StatusBadge
            status={brain?.edo_state === 'EXECUTION_PHASE' ? 'success' : 'warning'}
            label={brain?.edo_state ?? 'No data'}
            pulse
          />
        </div>
      </div>
    </div>
  );
}
