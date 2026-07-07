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
        <div className="section-card-title">Token Load Progression (Last 24 Hours)</div>
        <div style={{ height: '120px', display: 'flex', alignItems: 'flex-end', gap: '8px', padding: '10px 0', borderBottom: 'var(--border-default)' }}>
          {[20, 35, 45, 30, 60, 75, 40, 50, 65, 80, 95, 70, 85, 90, 60, 45, 55, 68, 72, 80, 85, 92, 74, 98].map((pct, idx) => (
            <div
              key={idx}
              style={{
                flex: 1,
                height: `${pct}%`,
                background: 'linear-gradient(to top, var(--accent-primary), var(--accent-cyan))',
                borderRadius: '2px 2px 0 0',
                transition: 'height 0.5s ease',
                position: 'relative'
              }}
              title={`Hour ${idx + 1}: ${pct}% load`}
            />
          ))}
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '10px', color: 'var(--text-muted)', marginTop: '4px' }}>
          <span>24 Hours Ago</span>
          <span>12 Hours Ago</span>
          <span>Active (Now)</span>
        </div>
      </div>
    </div>
  );
}
