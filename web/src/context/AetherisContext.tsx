import { createContext, useContext, useState, useEffect, type ReactNode } from 'react'
import type { RuntimeState, BrainState, MissionState, ProjectHealth, SkillEntry, ModelUsage, ReplayStep, RfcSpecCoverage, IntegrationCard, MemoryLog } from '../types'

interface AetherisState {
  runtime: (RuntimeState & { status: string; ide: string; interpreter: string; provider: string; model: string; project: string; workspace: string; branch: string; uptime: number; cpu: number; ram: number; }) | null;
  brain: BrainState | null;
  mission: MissionState | null;
  health: ProjectHealth | null;
  skills: SkillEntry[];
  models: ModelUsage[];
  replay: ReplayStep[];
  rfcSpecs: RfcSpecCoverage[];
  integrations: IntegrationCard[];
  memoryLogs: MemoryLog[];
  isConnected: boolean;
  loading: boolean;
}

const defaultState: AetherisState = {
  runtime: null,
  brain: null,
  mission: null,
  health: null,
  skills: [],
  models: [],
  replay: [],
  rfcSpecs: [],
  integrations: [],
  memoryLogs: [],
  isConnected: false,
  loading: true,
};

const AetherisContext = createContext<AetherisState>(defaultState);

export function useAetheris() { return useContext(AetherisContext); }

export function AetherisProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AetherisState>(defaultState);

  useEffect(() => {
    let ws: WebSocket | null = null;
    let reconnectTimeout: number | null = null;

    function connect() {
      const host = "127.0.0.1:8449";
      const protocol = "ws:";
      
      console.log(`[WebSocket] Connecting to ${protocol}//${host}/ws`);
      ws = new WebSocket(`${protocol}//${host}/ws`);

      ws.onopen = () => {
        console.log("[WebSocket] Connected to Dashboard Runtime Gateway (DRG)");
        setState(prev => ({ ...prev, isConnected: true, loading: false }));
      };

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          
          if (message.type === "RUNTIME_UPDATE") {
            const data = message.payload || {};
            setState(prev => ({
              ...prev,
              runtime: {
                ...prev.runtime,
                ...data,
                status: data.status || 'UNKNOWN',
                ide: data.ide || 'N/A',
                interpreter: data.interpreter || 'N/A',
                provider: data.provider || 'N/A',
                model: data.model_in_use || data.model || 'N/A',
                project: data.project || 'N/A',
                workspace: data.workspace || 'N/A',
                branch: data.branch || 'N/A',
                uptime: data.uptime || 0,
                cpu: data.cpu || 0,
                ram: data.ram || 0
              },
              loading: false
            }));
          } else if (message.type === "EXECUTION_UPDATE") {
            const data = message.payload || {};
            setState(prev => ({
              ...prev,
              brain: data.brain || prev.brain,
              mission: data.mission || prev.mission,
              health: data.health || prev.health,
              models: data.models || prev.models,
              replay: data.replay || prev.replay,
              rfcSpecs: data.rfcSpecs || prev.rfcSpecs,
              integrations: data.integrations || prev.integrations,
              skills: data.skills || prev.skills,
              memoryLogs: data.memoryLogs || prev.memoryLogs,
              loading: false
            }));
          }
        } catch (e) {
          console.error("[WebSocket] Failed to parse message:", e);
        }
      };

      ws.onclose = () => {
        console.log("[WebSocket] Connection closed. Attempting reconnect...");
        setState(prev => ({ ...prev, isConnected: false }));
        reconnectTimeout = window.setTimeout(connect, 3000);
      };

      ws.onerror = (err) => {
        console.error("[WebSocket] Error:", err);
        ws?.close();
      };
    }

    connect();

    return () => {
      ws?.close();
      if (reconnectTimeout) clearTimeout(reconnectTimeout);
    };
  }, []);

  return (
    <AetherisContext.Provider value={state}>
      {children}
    </AetherisContext.Provider>
  );
}
