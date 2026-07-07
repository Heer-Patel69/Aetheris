import { Cpu, Server, Network, Activity, ListOrdered, UserCheck } from 'lucide-react'
import MetricCard from '../widgets/MetricCard'
import StatusBadge from '../widgets/StatusBadge'
import ProgressBar from '../widgets/ProgressBar'
import { useAetheris } from '../../context/AetherisContext'

export default function RuntimeScreen() {
  const { runtime } = useAetheris();

  return (
    <div className="animate-in">
      <div className="screen-header">
        <h1 className="screen-title">Runtime Hypervisor</h1>
        <p className="screen-subtitle">Live scheduler queues, worker allocation, system load, and thread events</p>
      </div>

      {/* KPI Stats */}
      <div className="grid-4" style={{ marginBottom: 'var(--space-xl)' }}>
        <MetricCard
          label="Uptime"
          value={runtime ? `${Math.floor(runtime.uptime_seconds / 3600)}h ${Math.floor((runtime.uptime_seconds % 3600) / 60)}m` : null}
          detail="Continuous core daemon"
          icon={<Server size={14} />}
          accent="var(--accent-info)"
        />
        <MetricCard
          label="Active Workers"
          value={runtime ? "4 / 8" : null}
          detail="Concurrent thread pool"
          icon={<UserCheck size={14} />}
          accent="var(--accent-success)"
        />
        <MetricCard
          label="Event Bus Load"
          value={runtime ? `${runtime.events_per_second} ev/s` : null}
          detail="Total async payloads"
          icon={<Network size={14} />}
          accent="var(--accent-primary)"
        />
        <MetricCard
          label="Queue Depth"
          value={runtime ? "0" : null}
          detail="Pending tasks in RSE"
          icon={<ListOrdered size={14} />}
          accent="var(--accent-cyan)"
        />
      </div>

      {/* Resource Indicators */}
      <div className="section-card" style={{ marginBottom: 'var(--space-lg)' }}>
        <div className="section-card-title">
          <Activity size={18} />
          System Resources (Local Engine)
        </div>
        <div className="grid-3">
          <ProgressBar label="CPU Utilization" value={runtime?.cpu_usage ?? 0} variant={(runtime?.cpu_usage ?? 0) > 80 ? 'danger' : 'default'} />
          <ProgressBar label="RAM Allocation" value={runtime?.ram_usage ?? 0} variant={(runtime?.ram_usage ?? 0) > 85 ? 'warning' : 'default'} />
          <ProgressBar label="GPU Capacity" value={runtime?.gpu_usage ?? 0} />
        </div>
      </div>

      {/* Scheduler Queue View */}
      <div className="section-card">
        <div className="section-card-title">
          <ListOrdered size={18} />
          Live Execution Queue (RSE)
        </div>
        <table className="data-table">
          <thead>
            <tr>
              <th>Task ID</th>
              <th>Target Engine</th>
              <th>Order</th>
              <th>Policy</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td className="mono">task-4211</td>
              <td>Verification Engine (VRE)</td>
              <td>Sequential</td>
              <td>Retry: 3x, Timeout: 30s</td>
              <td><StatusBadge status="success" label="Active" pulse /></td>
            </tr>
            <tr>
              <td className="mono">task-4212</td>
              <td>Documentation Orchestrator (DOE)</td>
              <td>Parallel</td>
              <td>Retry: 1x, Timeout: 10s</td>
              <td><StatusBadge status="neutral" label="Scheduled" /></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}
