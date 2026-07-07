import { createContext, useContext, useState, useEffect, useRef, type ReactNode } from 'react'
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
  sessions: any[];
  replayMode: boolean;
  replayProgress: number;
  replayTotal: number;
  replayEvents: any[];
  startReplay: (executionId: string) => void;
  fetchSessions: () => void;
  stopReplay: () => void;
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
  sessions: [],
  replayMode: false,
  replayProgress: 0,
  replayTotal: 0,
  replayEvents: [],
  startReplay: () => {},
  fetchSessions: () => {},
  stopReplay: () => {}
};

const AetherisContext = createContext<AetherisState>(defaultState);

export function useAetheris() { return useContext(AetherisContext); }

export function AetherisProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AetherisState>(defaultState);
  const wsRef = useRef<WebSocket | null>(null);

  const startReplay = (executionId: string) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      setState(prev => ({
        ...prev,
        replayMode: true,
        replayProgress: 0,
        replayTotal: 0,
        replayEvents: [],
        skills: [],
        rfcSpecs: [],
        models: [],
        replay: [],
        health: {
          architecture: 0,
          security: 0,
          testing: 0,
          performance: 0,
          documentation: 0,
          maintainability: 0,
          technical_debt: 0,
          risk_index: 0
        }
      }));
      wsRef.current.send(JSON.stringify({ type: "START_REPLAY", execution_id: executionId }));
    }
  };

  const fetchSessions = () => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: "GET_SESSIONS" }));
    }
  };

  const stopReplay = () => {
    setState(prev => ({ ...prev, replayMode: false, replayEvents: [], replayProgress: 0 }));
    fetchSessions();
  };

  useEffect(() => {
    let reconnectTimeout: number | null = null;

    function connect() {
      const host = "127.0.0.1:8449";
      const protocol = "ws:";
      
      console.log(`[WebSocket] Connecting to ${protocol}//${host}/ws`);
      const ws = new WebSocket(`${protocol}//${host}/ws`);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log("[WebSocket] Connected to Dashboard Runtime Gateway (DRG)");
        setState(prev => ({ ...prev, isConnected: true, loading: false }));
        ws.send(JSON.stringify({ type: "GET_SESSIONS" }));
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
            setState(prev => {
              if (prev.replayMode) return prev;
              return {
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
              };
            });
          } else if (message.type === "SESSIONS_LIST") {
            setState(prev => ({ ...prev, sessions: message.payload || [] }));
          } else if (message.type === "REPLAY_START") {
            setState(prev => ({
              ...prev,
              replayMode: true,
              replayProgress: 0,
              replayTotal: message.total || 0,
              replayEvents: []
            }));
          } else if (message.type === "REPLAY_EVENT") {
            setState(prev => {
              const newEvent = message.payload;
              const newEvents = [...prev.replayEvents, newEvent];
              
              const category = newEvent.category;
              const payload = newEvent.payload;
              let skills = [...prev.skills];
              let rfcSpecs = [...prev.rfcSpecs];
              let health = prev.health ? { ...prev.health } : {
                architecture: 0, security: 0, testing: 0, performance: 0, documentation: 0, maintainability: 0, technical_debt: 0, risk_index: 0
              };
              let models = [...prev.models];
              let replay = [...prev.replay];
              let runtime = prev.runtime ? { ...prev.runtime } : null;

              if (category === "SYSTEM_BOOT" && runtime) {
                runtime = { ...runtime, ...payload, status: "READY" };
              } else if (category === "SKILL_INDEXED") {
                if (!skills.some(s => s.name === payload.name)) {
                  skills.push(payload);
                }
              } else if (category === "SKILL_LOADED") {
                skills = skills.map(s => s.name === payload.name ? { ...s, status: "active" } : s);
              } else if (category === "RFC_DISCOVERED") {
                if (!rfcSpecs.some(r => r.id === payload.name)) {
                  rfcSpecs.push({
                    id: payload.name,
                    title: payload.name,
                    type: payload.type || 'RFC',
                    coverage_percentage: payload.coverage || 100,
                    referenced_skills: [],
                    missing_implementations: [],
                    verification_status: 'passed'
                  });
                }
              } else if (category === "VERIFICATION_COMPLETED") {
                health = { 
                  ...health, 
                  ...payload.health,
                  technical_debt: payload.health.technical_debt || 0,
                  risk_index: payload.health.risk_index || 0
                };
              } else if (category === "TOKEN_TRACKING") {
                const model_name = payload.model;
                const idx = models.findIndex(m => m.model_name === model_name);
                if (idx !== -1) {
                  models[idx] = {
                    ...models[idx],
                    tokens_input: (models[idx].tokens_input || 0) + (payload.tokens || 0),
                    tokens_output: (models[idx].tokens_output || 0) + (payload.tokens_out || 0),
                    total_cost_usd: (models[idx].total_cost_usd || 0.0) + (payload.cost || 0.0)
                  };
                } else {
                  models.push({ 
                    model_name: model_name, 
                    provider: payload.provider || "Google", 
                    tokens_input: payload.tokens || 0, 
                    tokens_output: payload.tokens_out || 0, 
                    total_cost_usd: payload.cost || 0.0, 
                    latency_ms: payload.latency || 0,
                    success_rate: 100
                  });
                }
              } else if (["TASK_STARTED", "TASK_COMPLETED", "DECISION_MADE"].includes(category)) {
                replay.push({
                  step_number: replay.length + 1,
                  timestamp: new Date(newEvent.timestamp * 1000).toLocaleTimeString(),
                  stage: payload.phase || "Execution",
                  description: payload.detail || payload.description || "",
                  input_prompt: "",
                  selected_capabilities: [],
                  loaded_skills: [],
                  models_used: [payload.model || "Gemini 1.5 Pro"],
                  status: payload.status === "completed" || payload.status === "success" ? "success" : "warning",
                  files_modified: payload.files_modified || [],
                  tokens_consumed: payload.tokens || 0,
                  retries: 0
                });
                if (runtime) {
                  if (category === "TASK_STARTED") {
                    runtime.brain_state = "BUSY";
                    runtime.workflow_phase = payload.phase || "Execution";
                    runtime.active_goal = payload.task || "";
                  } else if (category === "TASK_COMPLETED") {
                    runtime.brain_state = "IDLE";
                    runtime.workflow_phase = "Awaiting task";
                    runtime.active_goal = "None";
                  }
                }
              }

              return {
                ...prev,
                replayEvents: newEvents,
                replayProgress: prev.replayProgress + 1,
                skills,
                rfcSpecs,
                health,
                models,
                replay,
                runtime
              };
            });
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
        ws.close();
      };
    }

    connect();

    return () => {
      wsRef.current?.close();
      if (reconnectTimeout) clearTimeout(reconnectTimeout);
    };
  }, []);

  return (
    <AetherisContext.Provider value={{
      ...state,
      startReplay,
      fetchSessions,
      stopReplay
    }}>
      {children}
    </AetherisContext.Provider>
  );
}
