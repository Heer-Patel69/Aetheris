import React, { createContext, useContext, useEffect, useState } from 'react';

type TelemetryEvent = {
  type: string;
  payload: any;
};

type WebSocketContextType = {
  events: TelemetryEvent[];
  runtimeState: any;
  executionState: any;
  connected: boolean;
};

const WebSocketContext = createContext<WebSocketContextType>({
  events: [],
  runtimeState: null,
  executionState: null,
  connected: false,
});

export const useWebSocket = () => useContext(WebSocketContext);

export const WebSocketProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [events, setEvents] = useState<TelemetryEvent[]>([]);
  const [runtimeState, setRuntimeState] = useState<any>(null);
  const [executionState, setExecutionState] = useState<any>(null);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    let ws: WebSocket;
    
    const connect = () => {
      ws = new WebSocket('ws://localhost:8449/ws');

      ws.onopen = () => {
        setConnected(true);
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data) as TelemetryEvent;
          setEvents(prev => [...prev, data].slice(-100)); // keep last 100
          
          if (data.type === 'RUNTIME_UPDATE') {
            setRuntimeState(data.payload);
          } else if (data.type === 'EXECUTION_UPDATE') {
            setExecutionState(data.payload);
          }
        } catch (e) {
          console.error("Failed to parse websocket message", e);
        }
      };

      ws.onclose = () => {
        setConnected(false);
        // Reconnect after 2 seconds
        setTimeout(connect, 2000);
      };
    };

    connect();

    return () => {
      if (ws) ws.close();
    };
  }, []);

  return (
    <WebSocketContext.Provider value={{ events, runtimeState, executionState, connected }}>
      {children}
    </WebSocketContext.Provider>
  );
};
