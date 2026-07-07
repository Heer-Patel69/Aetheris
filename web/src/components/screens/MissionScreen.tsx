import { Target, Flag, AlertOctagon, Users, Clock, GitBranch } from 'lucide-react'
import MetricCard from '../widgets/MetricCard'
import StatusBadge from '../widgets/StatusBadge'
import ProgressBar from '../widgets/ProgressBar'
import { useAetheris } from '../../context/AetherisContext'

export default function MissionScreen() {
  const { mission } = useAetheris();

  return (
    <div className="animate-in">
      <div className="screen-header">
        <h1 className="screen-title">Mission Control</h1>
        <p className="screen-subtitle">Live project state — sprint, milestones, blockers, and estimated completion</p>
      </div>

      <div className="grid-3" style={{ marginBottom: 'var(--space-xl)' }}>
        <MetricCard
          label="Health Score"
          value={mission?.health_score ?? null}
          detail="Composite project health"
          icon={<Target size={14} />}
          accent="var(--accent-success)"
        />
        <MetricCard
          label="Tasks Progress"
          value={mission ? `${mission.tasks_completed}/${mission.tasks_total}` : null}
          detail={mission?.sprint ?? 'No sprint active'}
          icon={<Flag size={14} />}
          accent="var(--accent-primary)"
        />
        <MetricCard
          label="Blockers"
          value={mission?.blockers?.length ?? null}
          detail="Active blockers requiring attention"
          icon={<AlertOctagon size={14} />}
          accent="var(--accent-danger)"
        />
      </div>

      {/* Mission Details */}
      <div className="grid-2">
        <div className="section-card">
          <div className="section-card-title">
            <Target size={18} />
            Current Mission
          </div>

          {mission ? (
            <>
              <div className="inspector-row">
                <span className="inspector-label">Project</span>
                <span className="inspector-value">{mission.project_name}</span>
              </div>
              <div className="inspector-row">
                <span className="inspector-label">Goal</span>
                <span className="inspector-value">{mission.current_goal}</span>
              </div>
              <div className="inspector-row">
                <span className="inspector-label">Milestone</span>
                <span className="inspector-value">{mission.milestone}</span>
              </div>
              <div className="inspector-row">
                <span className="inspector-label">Est. Completion</span>
                <span className="inspector-value">{mission.estimated_completion}</span>
              </div>
              <div style={{ marginTop: 'var(--space-lg)' }}>
                <ProgressBar
                  label="Overall Progress"
                  value={mission.tasks_completed}
                  max={mission.tasks_total}
                  variant="success"
                />
              </div>
            </>
          ) : (
            <div className="no-data">
              <p>No active mission. Start a project to see live mission data.</p>
            </div>
          )}
        </div>

        <div className="section-card">
          <div className="section-card-title">
            <Users size={18} />
            Active Engineer Roles
          </div>
          {mission?.active_roles?.length ? (
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
              {mission.active_roles.map(role => (
                <StatusBadge key={role} status="info" label={role} />
              ))}
            </div>
          ) : (
            <div className="no-data">
              <p>No active roles assigned.</p>
            </div>
          )}
        </div>
      </div>

      {/* Blockers */}
      {mission?.blockers?.length ? (
        <div className="section-card">
          <div className="section-card-title">
            <AlertOctagon size={18} />
            Active Blockers
          </div>
          {mission.blockers.map((blocker, i) => (
            <div key={i} style={{ padding: '8px 0', borderBottom: 'var(--border-subtle)', fontSize: '13px' }}>
              <StatusBadge status="danger" label={`B-${i + 1}`} />
              <span style={{ marginLeft: '8px' }}>{blocker}</span>
            </div>
          ))}
        </div>
      ) : null}
    </div>
  );
}
