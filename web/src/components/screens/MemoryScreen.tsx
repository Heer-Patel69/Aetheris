import { Database, Calendar, Eye, ShieldAlert } from 'lucide-react'
import StatusBadge from '../widgets/StatusBadge'
import { useAetheris } from '../../context/AetherisContext'

export default function MemoryScreen() {
  const { memoryLogs } = useAetheris();

  return (
    <div className="animate-in">
      <div className="screen-header">
        <h1 className="screen-title">Engineering Memory (EME)</h1>
        <p className="screen-subtitle">Browse persistent architectural decisions, rejected strategies, and structured lessons learned</p>
      </div>

      <div className="section-card">
        <div className="section-card-title">
          <Database size={18} />
          Structured Memory Log
        </div>
        <table className="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Category</th>
              <th>Title</th>
              <th>Description</th>
              <th>Timestamp</th>
            </tr>
          </thead>
          <tbody>
            {(memoryLogs || []).map((log) => (
              <tr key={log.id}>
                <td className="mono font-bold">{log.id}</td>
                <td>
                  <StatusBadge
                    status={log.category === 'decision' ? 'success' : log.category === 'rejected_idea' ? 'danger' : 'warning'}
                    label={log.category.toUpperCase().replace('_', ' ')}
                  />
                </td>
                <td style={{ fontWeight: 600 }}>{log.title}</td>
                <td style={{ fontSize: '12px', color: 'var(--text-secondary)', maxWidth: '350px' }}>{log.description}</td>
                <td className="mono">{log.timestamp}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
