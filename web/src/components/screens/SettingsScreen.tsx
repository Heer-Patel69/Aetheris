import { Settings, Save, Trash2, Shield, FolderOpen } from 'lucide-react'
import { useState } from 'react'

export default function SettingsScreen() {
  const [targetWorkspace, setTargetWorkspace] = useState('c:\\AI\\Aehteris main');

  return (
    <div className="animate-in">
      <div className="screen-header">
        <h1 className="screen-title">System Settings</h1>
        <p className="screen-subtitle">Configure project workspace parameters, API gateways, and purge cached runtime states</p>
      </div>

      <div className="grid-2">
        {/* Workspace Configurations */}
        <div className="section-card">
          <div className="section-card-title">
            <FolderOpen size={18} />
            Workspace Parameters
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <label style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Target Workspace Directory</label>
            <input
              type="text"
              value={targetWorkspace}
              onChange={e => setTargetWorkspace(e.target.value)}
              style={{
                padding: '8px 12px',
                background: 'var(--bg-secondary)',
                border: 'var(--border-default)',
                borderRadius: 'var(--radius-md)',
                color: 'var(--text-primary)',
                fontFamily: 'var(--font-mono)',
                fontSize: '12px',
                outline: 'none'
              }}
            />
            <button className="status-badge status-badge--success" style={{ alignSelf: 'flex-start', border: 'none', cursor: 'pointer', padding: '8px 16px' }}>
              <Save size={12} style={{ marginRight: '6px' }} /> Update Path
            </button>
          </div>
        </div>

        {/* System Operations */}
        <div className="section-card">
          <div className="section-card-title">
            <Shield size={18} />
            Administrative Actions
          </div>
          <p style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: 'var(--space-md)' }}>
            Perform operations on the active .aetheris workspace.
          </p>
          <div style={{ display: 'flex', gap: '8px' }}>
            <button className="status-badge status-badge--warning" style={{ border: 'none', cursor: 'pointer', padding: '8px 16px' }}>
              Purge Cache (aetheris cleanup)
            </button>
            <button className="status-badge status-badge--danger" style={{ border: 'none', cursor: 'pointer', padding: '8px 16px' }}>
              <Trash2 size={12} style={{ marginRight: '6px' }} /> Purge Workspace (aetheris purge)
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
