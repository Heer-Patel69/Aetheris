import { BookOpen, FileText, CheckCircle2, ShieldAlert } from 'lucide-react'
import StatusBadge from '../widgets/StatusBadge'
import ProgressBar from '../widgets/ProgressBar'
import { useAetheris } from '../../context/AetherisContext'

export default function RfcSpecScreen() {
  const { rfcSpecs } = useAetheris();

  return (
    <div className="animate-in">
      <div className="screen-header">
        <h1 className="screen-title">RFC & SPEC Validation Matrix</h1>
        <p className="screen-subtitle">Track project specifications, functional coverage metrics, and implementation synchronization</p>
      </div>

      <div className="section-card">
        <div className="section-card-title">
          <BookOpen size={18} />
          Specification Validation Coverage
        </div>
        <table className="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Title</th>
              <th>Type</th>
              <th>Coverage</th>
              <th>Referenced Skills</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {(rfcSpecs || []).map((item) => (
              <tr key={item.id}>
                <td className="mono font-bold">{item.id}</td>
                <td>{item.title}</td>
                <td><StatusBadge status="neutral" label={item.type} /></td>
                <td>
                  <ProgressBar label="" value={item.coverage_percentage} max={100} />
                </td>
                <td className="mono" style={{ fontSize: '11px' }}>{item.referenced_skills.join(', ')}</td>
                <td>
                  <StatusBadge
                    status={item.verification_status === 'passed' ? 'success' : 'warning'}
                    label={item.verification_status.toUpperCase()}
                  />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Gap Analysis */}
      <div className="section-card" style={{ marginTop: 'var(--space-lg)' }}>
        <div className="section-card-title">
          <ShieldAlert size={18} />
          Missing Implementation Gaps
        </div>
        <table className="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Missing Component</th>
              <th>Impact</th>
            </tr>
          </thead>
          <tbody>
            {(rfcSpecs || []).filter(item => item.missing_implementations.length > 0).map((item) => (
              <tr key={item.id}>
                <td className="mono">{item.id}</td>
                <td>{item.missing_implementations.join(', ')}</td>
                <td><StatusBadge status="danger" label="HIGH" /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
