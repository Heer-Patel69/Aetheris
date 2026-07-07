import { Wrench, CheckCircle, FileText, LayoutGrid, ShieldAlert, BadgeHelp } from 'lucide-react'
import ProgressBar from '../widgets/ProgressBar'
import StatusBadge from '../widgets/StatusBadge'
import { useAetheris } from '../../context/AetherisContext'

export default function EngineeringScreen() {
  const { health } = useAetheris();

  return (
    <div className="animate-in">
      <div className="screen-header">
        <h1 className="screen-title">Engineering Pipeline</h1>
        <p className="screen-subtitle">Repository intelligence, documentation coverage, architecture validation, and quality gates</p>
      </div>

      <div className="grid-2">
        {/* Quality Gates */}
        <div className="section-card">
          <div className="section-card-title">
            <CheckCircle size={18} />
            Mandatory Engineering Gates
          </div>

          <div className="inspector-row">
            <span className="inspector-label">PRD & BRD Generated</span>
            <StatusBadge status="success" label="PASSED" />
          </div>
          <div className="inspector-row">
            <span className="inspector-label">Architecture Validation</span>
            <StatusBadge status="success" label="PASSED" />
          </div>
          <div className="inspector-row">
            <span className="inspector-label">Implementation Plan (RFC)</span>
            <StatusBadge status="success" label="PASSED" />
          </div>
          <div className="inspector-row">
            <span className="inspector-label">Static Analysis / Compliance</span>
            <StatusBadge status="warning" label="COMPLY" />
          </div>
          <div className="inspector-row">
            <span className="inspector-label">Security Threat Model</span>
            <StatusBadge status="success" label="COMPLETED" />
          </div>
        </div>

        {/* Verification Coverage */}
        <div className="section-card">
          <div className="section-card-title">
            <LayoutGrid size={18} />
            Completeness Scoring
          </div>
          <ProgressBar label="PRD Compliance" value={health?.documentation ?? 0} variant="success" />
          <ProgressBar label="C4 Architecture Consistency" value={health?.architecture ?? 0} variant="success" />
          <ProgressBar label="Unit Testing Target (Min 80%)" value={health?.testing ?? 0} variant={ (health?.testing ?? 0) >= 80 ? 'success' : 'warning' } />
          <ProgressBar label="Security Risk Mitigation" value={100 - (health?.risk_index ?? 0) * 10} />
        </div>
      </div>

      {/* Continuous Documentation Audits */}
      <div className="section-card" style={{ marginTop: 'var(--space-lg)' }}>
        <div className="section-card-title">
          <FileText size={18} />
          Document Lifecycle Audit Trail
        </div>
        <table className="data-table">
          <thead>
            <tr>
              <th>File Name</th>
              <th>Workspace Path</th>
              <th>Quality Score</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td className="mono">PRD.md</td>
              <td>.aetheris/documentation/</td>
              <td>94/100</td>
              <td><StatusBadge status="success" label="Synchronized" /></td>
            </tr>
            <tr>
              <td className="mono">SYSTEM_ARCHITECTURE.md</td>
              <td>.aetheris/architecture/</td>
              <td>92/100</td>
              <td><StatusBadge status="success" label="Synchronized" /></td>
            </tr>
            <tr>
              <td className="mono">SOFTWARE_ARCHITECTURE.md</td>
              <td>.aetheris/architecture/</td>
              <td>90/100</td>
              <td><StatusBadge status="success" label="Synchronized" /></td>
            </tr>
            <tr>
              <td className="mono">SECURITY_ARCHITECTURE.md</td>
              <td>.aetheris/architecture/</td>
              <td>88/100</td>
              <td><StatusBadge status="warning" label="Stale (Pending Commit)" /></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}
