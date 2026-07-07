import { useState } from 'react'
import { AetherisProvider, useAetheris } from './context/AetherisContext'
import Sidebar from './components/layout/Sidebar'
import Inspector from './components/layout/Inspector'
import OverviewScreen from './components/screens/OverviewScreen'
import MissionScreen from './components/screens/MissionScreen'
import BrainScreen from './components/screens/BrainScreen'
import SkillsScreen from './components/screens/SkillsScreen'
import RuntimeScreen from './components/screens/RuntimeScreen'
import EngineeringScreen from './components/screens/EngineeringScreen'
import AnalyticsScreen from './components/screens/AnalyticsScreen'
import ReplayScreen from './components/screens/ReplayScreen'
import RfcSpecScreen from './components/screens/RfcSpecScreen'
import IntegrationsScreen from './components/screens/IntegrationsScreen'
import MemoryScreen from './components/screens/MemoryScreen'
import SettingsScreen from './components/screens/SettingsScreen'
import KnowledgeGraphScreen from './components/screens/KnowledgeGraphScreen'
import type { NavScreen } from './types'

function DashboardContent() {
  const [screen, setScreen] = useState<NavScreen>('overview');
  const [theme, setTheme] = useState<'dark' | 'light'>('dark');
  const { runtime, isConnected } = useAetheris();

  const toggleTheme = () => {
    const next = theme === 'dark' ? 'light' : 'dark';
    setTheme(next);
    document.documentElement.setAttribute('data-theme', next);
  };

  const renderScreen = () => {
    switch (screen) {
      case 'overview': return <OverviewScreen />;
      case 'mission': return <MissionScreen />;
      case 'brain': return <BrainScreen />;
      case 'skills': return <SkillsScreen />;
      case 'runtime': return <RuntimeScreen />;
      case 'engineering': return <EngineeringScreen />;
      case 'analytics': return <AnalyticsScreen />;
      case 'replay': return <ReplayScreen />;
      case 'rfc': return <RfcSpecScreen />;
      case 'spec': return <RfcSpecScreen />;
      case 'integrations': return <IntegrationsScreen />;
      case 'memory': return <MemoryScreen />;
      case 'settings': return <SettingsScreen />;
      case 'knowledge-graph': return <KnowledgeGraphScreen />;
      default: return <OverviewScreen />;
    }
  };

  return (
    <div className="app-shell-container">
      {/* Offline Mode Reconnection Alert */}
      {!isConnected && (
        <div className="reconnect-banner">
          ⚠️ Runtime Disconnected. Attempting reconnection...
        </div>
      )}

      <div className="app-shell">
        <Sidebar activeScreen={screen} onNavigate={setScreen} theme={theme} onToggleTheme={toggleTheme} />
        <main className="main-canvas">
          {renderScreen()}
        </main>
        <Inspector />
      </div>

      {/* Runtime Status Bar */}
      <footer className="status-bar">
        <div className="status-bar-section">
          <span className="status-bar-label">Runtime:</span>
          <span className={`status-bar-value ${isConnected ? 'connected' : 'disconnected'}`}>
            {isConnected ? 'CONNECTED' : 'OFFLINE'}
          </span>
        </div>
        <div className="status-bar-section">
          <span className="status-bar-label">Brain:</span>
          <span className="status-bar-value">{runtime ? 'READY' : 'WAITING'}</span>
        </div>
        <div className="status-bar-section">
          <span className="status-bar-label">IDE:</span>
          <span className="status-bar-value">{runtime?.ide ?? 'Discovering...'}</span>
        </div>
        <div className="status-bar-section">
          <span className="status-bar-label">Provider:</span>
          <span className="status-bar-value">{runtime?.provider ?? '—'}</span>
        </div>
        <div className="status-bar-section">
          <span className="status-bar-label">Model:</span>
          <span className="status-bar-value">{runtime?.model ?? '—'}</span>
        </div>
        <div className="status-bar-section">
          <span className="status-bar-label">Project:</span>
          <span className="status-bar-value">{runtime?.project ?? '—'}</span>
        </div>
        <div className="status-bar-section">
          <span className="status-bar-label">Branch:</span>
          <span className="status-bar-value">{runtime?.branch ?? '—'}</span>
        </div>
      </footer>
    </div>
  );
}

export default function App() {
  return (
    <AetherisProvider>
      <DashboardContent />
    </AetherisProvider>
  );
}
