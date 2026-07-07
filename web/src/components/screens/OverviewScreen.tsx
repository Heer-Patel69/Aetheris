import { Activity, Blocks, Brain, Shield, Zap, FileText, CheckCircle2, AlertTriangle } from 'lucide-react'
import MetricCard from '../widgets/MetricCard'
import ProgressBar from '../widgets/ProgressBar'
import StatusBadge from '../widgets/StatusBadge'
import { useAetheris } from '../../context/AetherisContext'

export default function OverviewScreen() {
  const { runtime, health, skills } = useAetheris();

  return (
    <div className="animate-in">
      <div className="screen-header">
        <h1 className="screen-title">Mission Overview</h1>
        <p className="screen-subtitle">Engineering Control Room — Live system state from .aetheris runtime</p>
      </div>

      {/* KPI Row */}
      <div className="grid-4" style={{ marginBottom: 'var(--space-xl)' }}>
        <MetricCard
          label="Engines Online"
          value={runtime && runtime.engines_online !== undefined ? `${runtime.engines_online}/${runtime.total_engines}` : null}
          detail="18-engine architecture"
          icon={<Zap size={14} />}
          accent="var(--accent-success)"
        />
        <MetricCard
          label="Brain State"
          value={runtime?.brain_state ?? null}
          detail={runtime?.workflow_phase ?? 'Awaiting data'}
          icon={<Brain size={14} />}
          accent="var(--accent-primary)"
        />
        <MetricCard
          label="Active Goal"
          value={runtime?.active_goal ?? null}
          detail={runtime?.current_branch ?? '—'}
          icon={<Activity size={14} />}
          accent="var(--accent-cyan)"
        />
        <MetricCard
          label="Skills Registered"
          value={skills ? skills.length : null}
          detail="Unified Skill Registry"
          icon={<Blocks size={14} />}
          accent="var(--accent-violet)"
        />
      </div>

      {/* Project Health */}
      <div className="section-card">
        <div className="section-card-title">
          <Shield size={18} />
          Project Health Dimensions
        </div>

        {health ? (
          <div className="grid-2">
            <ProgressBar label="Documentation" value={health.documentation} variant={health.documentation > 70 ? 'success' : 'warning'} />
            <ProgressBar label="Architecture" value={health.architecture} variant={health.architecture > 70 ? 'success' : 'warning'} />
            <ProgressBar label="Security" value={health.security} variant={health.security > 70 ? 'success' : 'danger'} />
            <ProgressBar label="Testing" value={health.testing} variant={health.testing > 70 ? 'success' : 'warning'} />
            <ProgressBar label="Performance" value={health.performance} />
            <ProgressBar label="Maintainability" value={health.maintainability} />
          </div>
        ) : (
          <div className="no-data">
            <FileText />
            <p>No project health data available. Run the Verification Engine to generate health scores.</p>
          </div>
        )}
      </div>

      {/* Engineering Workflow */}
      <div className="section-card">
        <div className="section-card-title">
          <CheckCircle2 size={18} />
          Engineering Workflow Status
        </div>
        <div className="workflow-steps">
          {['Discovery', 'Capability', 'Documentation', 'Architecture', 'Planning', 'Verification', 'Implementation', 'Review'].map((step, i) => (
            <span key={step}>
              <span className={`workflow-step ${i < 2 ? 'completed' : i === 2 ? 'active' : 'pending'}`}>
                {step}
              </span>
              {i < 7 && <span className="workflow-arrow"> → </span>}
            </span>
          ))}
        </div>
      </div>

      {/* System Alerts */}
      <div className="section-card">
        <div className="section-card-title">
          <AlertTriangle size={18} />
          Active Alerts
        </div>
        <div className="no-data">
          <p>No active alerts. System operating normally.</p>
        </div>
      </div>
    </div>
  );
}
