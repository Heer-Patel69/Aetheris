import {
  LayoutDashboard, Target, Brain, Cpu, Wrench, Blocks,
  FileText, BookOpen, Plug, Network, RotateCcw, BarChart3,
  Database, Settings, Sun, Moon
} from 'lucide-react'
import type { NavScreen } from '../../types'

interface Props {
  activeScreen: NavScreen;
  onNavigate: (s: NavScreen) => void;
  theme: 'dark' | 'light';
  onToggleTheme: () => void;
}

const sections = [
  {
    label: 'Command',
    items: [
      { id: 'overview' as NavScreen, icon: LayoutDashboard, label: 'Overview' },
      { id: 'mission' as NavScreen, icon: Target, label: 'Mission Control' },
      { id: 'brain' as NavScreen, icon: Brain, label: 'Brain' },
    ]
  },
  {
    label: 'Runtime',
    items: [
      { id: 'runtime' as NavScreen, icon: Cpu, label: 'Runtime' },
      { id: 'engineering' as NavScreen, icon: Wrench, label: 'Engineering' },
      { id: 'skills' as NavScreen, icon: Blocks, label: 'Skills' },
    ]
  },
  {
    label: 'Knowledge',
    items: [
      { id: 'rfc' as NavScreen, icon: FileText, label: 'RFC' },
      { id: 'spec' as NavScreen, icon: BookOpen, label: 'SPEC' },
      { id: 'integrations' as NavScreen, icon: Plug, label: 'Integrations' },
      { id: 'knowledge-graph' as NavScreen, icon: Network, label: 'Knowledge Graph' },
    ]
  },
  {
    label: 'Intelligence',
    items: [
      { id: 'replay' as NavScreen, icon: RotateCcw, label: 'Replay' },
      { id: 'analytics' as NavScreen, icon: BarChart3, label: 'Analytics' },
      { id: 'memory' as NavScreen, icon: Database, label: 'Memory' },
      { id: 'settings' as NavScreen, icon: Settings, label: 'Settings' },
    ]
  }
];

export default function Sidebar({ activeScreen, onNavigate, theme, onToggleTheme }: Props) {
  return (
    <nav className="sidebar">
      <div className="sidebar-brand">
        <div className="sidebar-brand-logo">A</div>
        <span className="sidebar-brand-text">Aetheris</span>
      </div>

      {sections.map(section => (
        <div key={section.label} className="sidebar-section">
          <div className="sidebar-section-label">{section.label}</div>
          {section.items.map(item => (
            <div
              key={item.id}
              className={`sidebar-item ${activeScreen === item.id ? 'active' : ''}`}
              onClick={() => onNavigate(item.id)}
            >
              <item.icon />
              <span>{item.label}</span>
            </div>
          ))}
        </div>
      ))}

      <div className="theme-toggle" onClick={onToggleTheme}>
        {theme === 'dark' ? <Sun size={14} /> : <Moon size={14} />}
        <span>{theme === 'dark' ? 'Light Mode' : 'Dark Mode'}</span>
      </div>
    </nav>
  );
}
