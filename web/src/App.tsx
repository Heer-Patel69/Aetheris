import { useState } from 'react'
import { AetherisProvider } from './context/AetherisContext'
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

export default function App() {
  const [screen, setScreen] = useState<NavScreen>('overview');
  const [theme, setTheme] = useState<'dark' | 'light'>('dark');

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
      case 'spec': return <RfcSpecScreen />; // Alias to the unified screen
      case 'integrations': return <IntegrationsScreen />;
      case 'memory': return <MemoryScreen />;
      case 'settings': return <SettingsScreen />;
      case 'knowledge-graph': return <KnowledgeGraphScreen />;
      default: return <OverviewScreen />;
    }
  };

  return (
    <AetherisProvider>
      <div className="app-shell">
        <Sidebar activeScreen={screen} onNavigate={setScreen} theme={theme} onToggleTheme={toggleTheme} />
        <main className="main-canvas">
          {renderScreen()}
        </main>
        <Inspector />
      </div>
    </AetherisProvider>
  );
}
