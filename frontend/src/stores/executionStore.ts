import { create } from 'zustand';
import { socketClient } from '../lib/socket';
import type { EventEnvelope } from '../types/events';
import type { ExecutionGraph, ExecutionStatus } from '../types/execution';
import type { SocketStatus } from '../lib/socket';

export interface ExecutionStoreState {
  connectionStatus: SocketStatus;
  executionStatus: ExecutionStatus;
  executionGraph: ExecutionGraph | null;
  selectedNode: string | null;
  currentTick: number;
  events: EventEnvelope<any>[];
  isConnected: boolean;
  isLoading: boolean;
  error: string | null;

  connect: () => void;
  disconnect: () => void;
  setExecution: (status: ExecutionStatus, graph: ExecutionGraph) => void;
  selectNode: (nodeId: string | null) => void;
  applyEvent: (event: EventEnvelope<any>) => void;
  clearExecution: () => void;
}

export const useExecutionStore = create<ExecutionStoreState>((set, get) => {
  // Subscribe to socket status
  socketClient.onStatusChange((status) => {
    set({
      connectionStatus: status,
      isConnected: status === 'connected',
      error: status === 'error' ? 'Connection error' : null,
    });
  });

  // Subscribe to socket events
  socketClient.onMessage((envelope) => {
    get().applyEvent(envelope);
  });

  return {
    connectionStatus: 'disconnected',
    executionStatus: 'IDLE',
    executionGraph: null,
    selectedNode: null,
    currentTick: 0,
    events: [],
    isConnected: false,
    isLoading: false,
    error: null,

    connect: () => {
      set({ isLoading: true });
      socketClient.connect();
      set({ isLoading: false });
    },

    disconnect: () => {
      socketClient.disconnect();
    },

    setExecution: (status, graph) => {
      set({ executionStatus: status, executionGraph: graph });
    },

    selectNode: (nodeId) => {
      set({ selectedNode: nodeId });
    },

    applyEvent: (envelope) => {
      set((state) => {
        const newEvents = [...state.events, envelope];
        
        // Let's mutate only the necessary state based on event type
        let newStatus = state.executionStatus;
        let newGraph = state.executionGraph;
        let newTick = state.currentTick;

        switch (envelope.type) {
          case 'ExecutionStarted':
            newStatus = 'RUNNING';
            // Start with an empty graph if not initialized
            if (!newGraph) {
              newGraph = { nodes: [], edges: [] };
            }
            break;
            
          case 'ExecutionFinished':
            newStatus = 'FINISHED';
            break;
            
          case 'ExecutionFailed':
            newStatus = 'FAILED';
            break;

          case 'TickStarted':
            if (envelope.payload && 'tickId' in envelope.payload) {
              newTick = envelope.payload.tickId;
            }
            break;

          case 'NodeStarted':
            if (newGraph && envelope.payload && 'nodeId' in envelope.payload) {
              const payload = envelope.payload as { nodeId: string, agentName: string };
              // Make sure to clone nodes to trigger React re-render properly without replacing whole graph
              const nodes = [...newGraph.nodes];
              const existingNodeIndex = nodes.findIndex(n => n.id === payload.nodeId);
              
              if (existingNodeIndex >= 0) {
                nodes[existingNodeIndex] = { ...nodes[existingNodeIndex], status: 'RUNNING' };
              } else {
                nodes.push({
                  id: payload.nodeId,
                  agentName: payload.agentName,
                  status: 'RUNNING'
                });
              }
              
              newGraph = { ...newGraph, nodes };
            }
            break;
            
          case 'NodeCompleted':
            if (newGraph && envelope.payload && 'nodeId' in envelope.payload) {
              const payload = envelope.payload as { nodeId: string, agentName: string, output: unknown };
              const nodes = [...newGraph.nodes];
              const existingNodeIndex = nodes.findIndex(n => n.id === payload.nodeId);
              
              if (existingNodeIndex >= 0) {
                nodes[existingNodeIndex] = { ...nodes[existingNodeIndex], status: 'COMPLETE' };
                newGraph = { ...newGraph, nodes };
              }
            }
            break;
        }

        return {
          events: newEvents,
          executionStatus: newStatus,
          executionGraph: newGraph,
          currentTick: newTick
        };
      });
    },

    clearExecution: () => {
      set({
        executionStatus: 'IDLE',
        executionGraph: null,
        selectedNode: null,
        currentTick: 0,
        events: [],
      });
    }
  };
});
