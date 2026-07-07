import { Plug, Wifi, Settings, Info } from 'lucide-react'
import StatusBadge from '../widgets/StatusBadge'
import { useAetheris } from '../../context/AetherisContext'

export default function IntegrationsScreen() {
  const { integrations } = useAetheris();

  return (
    <div className="animate-in">
      <div className="screen-header">
        <h1 className="screen-title">Integration Hub</h1>
        <p className="screen-subtitle">Monitor third-party runtime adapters, API latency, and dynamically mapped capabilities</p>
      </div>

      <div className="grid-3">
        {(integrations || []).map((adapter, idx) => (
          <div key={idx} className="metric-card" style={{ '--card-accent': adapter.adapter_health === 'healthy' ? 'var(--accent-success)' : 'var(--accent-warning)' } as React.CSSProperties}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-md)' }}>
              <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                <Plug size={16} color="var(--accent-primary)" />
                <span style={{ fontWeight: 700 }}>{adapter.name}</span>
              </div>
              <StatusBadge status={adapter.adapter_health === 'healthy' ? 'success' : 'warning'} label={adapter.adapter_health.toUpperCase()} />
            </div>

            <div className="inspector-row">
              <span className="inspector-label">Version</span>
              <span className="inspector-value">{adapter.version}</span>
            </div>
            <div className="inspector-row">
              <span className="inspector-label">Latency</span>
              <span className="inspector-value">{adapter.latency_ms}ms</span>
            </div>
            <div className="inspector-row">
              <span className="inspector-label">Mapped Skills</span>
              <span className="inspector-value">{adapter.capabilities_mapped}</span>
            </div>
            <div className="inspector-row">
              <span className="inspector-label">Compatibility</span>
              <span className="inspector-value">{adapter.compatibility_score}%</span>
            </div>
          </div>
        ))}
      </div>

      {/* Integration Registry Info */}
      <div className="section-card" style={{ marginTop: 'var(--space-lg)' }}>
        <div className="section-card-title">
          <Info size={18} />
          Integration Manifest Policies
        </div>
        <p style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: '1.6' }}>
          Adapters are loaded dynamically via plugins configuration manifests. The integration engine maps capabilities to the unified skill registry, allowing adapters to register tools dynamically without editing the EDO core engine.
        </p>
      </div>
    </div>
  );
}
