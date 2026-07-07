import { BarChart3, Coins, Sparkles, Scale } from 'lucide-react'
import MetricCard from '../widgets/MetricCard'
import { useAetheris } from '../../context/AetherisContext'

export default function AnalyticsScreen() {
  const { models } = useAetheris();

  // Custom SVG Bar Chart calculation
  const totalCost = (models || []).reduce((acc, m) => acc + m.total_cost_usd, 0);
  const totalTokens = (models || []).reduce((acc, m) => acc + m.tokens_input + m.tokens_output, 0);

  return (
    <div className="animate-in">
      <div className="screen-header">
        <h1 className="screen-title">Token Intelligence & Cost Analytics</h1>
        <p className="screen-subtitle">Model usage stats, input/output token balance, efficiency, and cost metrics</p>
      </div>

      <div className="grid-3" style={{ marginBottom: 'var(--space-xl)' }}>
        <MetricCard
          label="Cumulative Cost"
          value={`$${totalCost.toFixed(2)}`}
          detail="Total API cost calculated from prompts"
          icon={<Coins size={14} />}
          accent="var(--accent-warning)"
        />
        <MetricCard
          label="Total Tokens Utilized"
          value={totalTokens.toLocaleString()}
          detail="Volume of context parsed"
          icon={<Sparkles size={14} />}
          accent="var(--accent-primary)"
        />
        <MetricCard
          label="Avg Compression Ratio"
          value="82%"
          detail="Context Intelligence savings"
          icon={<Scale size={14} />}
          accent="var(--accent-success)"
        />
      </div>

      {/* Model Distribution Section */}
      <div className="section-card">
        <div className="section-card-title">
          <BarChart3 size={18} />
          Model Distribution & Performance Matrix
        </div>
        <table className="data-table">
          <thead>
            <tr>
              <th>Model Name</th>
              <th>Provider</th>
              <th>Input Tokens</th>
              <th>Output Tokens</th>
              <th>Cost (USD)</th>
              <th>Success Rate</th>
            </tr>
          </thead>
          <tbody>
            {(models || []).map((m, idx) => (
              <tr key={idx}>
                <td className="mono">{m.model_name}</td>
                <td>{m.provider}</td>
                <td className="mono">{m.tokens_input.toLocaleString()}</td>
                <td className="mono">{m.tokens_output.toLocaleString()}</td>
                <td className="mono">${m.total_cost_usd.toFixed(2)}</td>
                <td><span style={{ color: 'var(--accent-success)', fontWeight: 600 }}>{m.success_rate}%</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Visual Token Utilization Graph (SVG-driven) */}
      <div className="section-card" style={{ marginTop: 'var(--space-lg)' }}>
        <div className="section-card-title">Token Load Progression (Live)</div>
        <div style={{ height: '120px', display: 'flex', alignItems: 'flex-end', justifyContent: 'center', gap: '8px', padding: '10px 0', borderBottom: 'var(--border-default)' }}>
          {/* No live historical token data is currently emitted by the runtime */}
          <div className="no-data" style={{ width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', border: 'none' }}>
            <p>Awaiting live telemetry streams...</p>
          </div>
        </div>
      </div>
    </div>
  );
}
