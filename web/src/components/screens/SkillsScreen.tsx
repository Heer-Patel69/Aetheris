import { useState, useMemo } from 'react'
import { Blocks, Search, Filter } from 'lucide-react'
import MetricCard from '../widgets/MetricCard'
import CacheIndicator from '../widgets/CacheIndicator'
import StatusBadge from '../widgets/StatusBadge'
import { useAetheris } from '../../context/AetherisContext'

export default function SkillsScreen() {
  const [search, setSearch] = useState('');
  const [filterTier, setFilterTier] = useState<string>('all');
  const { skills } = useAetheris();

  const filtered = useMemo(() => {
    return (skills || []).filter(s => {
      const matchSearch = s.name.toLowerCase().includes(search.toLowerCase()) || s.category.toLowerCase().includes(search.toLowerCase());
      const matchTier = filterTier === 'all' || s.cache_tier === filterTier;
      return matchSearch && matchTier;
    });
  }, [skills, search, filterTier]);

  const hotCount = (skills || []).filter(s => s.cache_tier === 'hot').length;
  const warmCount = (skills || []).filter(s => s.cache_tier === 'warm').length;
  const coldCount = (skills || []).filter(s => s.cache_tier === 'cold').length;

  return (
    <div className="animate-in">
      <div className="screen-header">
        <h1 className="screen-title">Skill Intelligence</h1>
        <p className="screen-subtitle">Unified registry — {skills.length} skills across all repositories</p>
      </div>

      {/* KPIs */}
      <div className="grid-4" style={{ marginBottom: 'var(--space-xl)' }}>
        <MetricCard label="Total Skills" value={skills.length} icon={<Blocks size={14} />} accent="var(--accent-primary)" />
        <MetricCard label="Avg Success Rate" value={skills.length > 0 ? `${Math.round(skills.reduce((a, s) => a + s.success_rate, 0) / skills.length)}%` : '0%'} accent="var(--accent-success)" />
        <MetricCard label="Avg Exec Time" value={skills.length > 0 ? `${Math.round(skills.reduce((a, s) => a + s.execution_time_ms, 0) / skills.length)}ms` : '0ms'} accent="var(--accent-warning)" />
        <MetricCard label="Avg Quality" value={skills.length > 0 ? `${Math.round(skills.reduce((a, s) => a + s.quality_score, 0) / skills.length)}` : '0'} accent="var(--accent-violet)" />
      </div>

      {/* Cache Distribution */}
      <div className="section-card" style={{ marginBottom: 'var(--space-xl)' }}>
        <div className="section-card-title">3-Tier Runtime Cache</div>
        <CacheIndicator hot={hotCount} warm={warmCount} cold={coldCount} />
      </div>

      {/* Search & Filter */}
      <div style={{ display: 'flex', gap: '12px', marginBottom: 'var(--space-lg)', alignItems: 'center' }}>
        <div style={{ position: 'relative', flex: 1 }}>
          <Search size={14} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
          <input
            type="text"
            placeholder="Search skills..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            style={{
              width: '100%',
              padding: '8px 12px 8px 34px',
              background: 'var(--bg-card)',
              border: 'var(--border-default)',
              borderRadius: 'var(--radius-md)',
              color: 'var(--text-primary)',
              fontSize: '13px',
              fontFamily: 'var(--font-ui)',
              outline: 'none'
            }}
          />
        </div>
        <div style={{ display: 'flex', gap: '4px' }}>
          {['all', 'hot', 'warm', 'cold'].map(tier => (
            <button
              key={tier}
              onClick={() => setFilterTier(tier)}
              style={{
                padding: '6px 12px',
                fontSize: '11px',
                fontWeight: 600,
                borderRadius: 'var(--radius-sm)',
                border: 'none',
                cursor: 'pointer',
                background: filterTier === tier ? 'var(--accent-primary-dim)' : 'var(--bg-elevated)',
                color: filterTier === tier ? 'var(--accent-primary)' : 'var(--text-secondary)',
              }}
            >
              {tier.toUpperCase()}
            </button>
          ))}
        </div>
      </div>

      {/* Skills Table */}
      <div className="section-card" style={{ padding: 0, overflow: 'auto', maxHeight: '500px' }}>
        <table className="data-table">
          <thead>
            <tr>
              <th>Skill</th>
              <th>Category</th>
              <th>Cache</th>
              <th>Success</th>
              <th>Exec Time</th>
              <th>Quality</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map(skill => (
              <tr key={skill.id}>
                <td className="mono">{skill.name}</td>
                <td><StatusBadge status="neutral" label={skill.category} /></td>
                <td>
                  <StatusBadge
                    status={skill.cache_tier === 'hot' ? 'danger' : skill.cache_tier === 'warm' ? 'warning' : 'info'}
                    label={skill.cache_tier}
                  />
                </td>
                <td className="mono">{skill.success_rate}%</td>
                <td className="mono">{skill.execution_time_ms}ms</td>
                <td className="mono">{skill.quality_score}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
