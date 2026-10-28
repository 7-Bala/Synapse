import { create } from 'zustand';
import { socketClient } from '../lib/socket';
import type { EventEnvelope } from '../types/events';
import type { ExecutionGraph, ExecutionStatus, ExecutionRecord, AgentNode, TimelineEntry } from '../types/execution';
import type { SocketStatus } from '../lib/socket';
import { apiGet, apiPost } from '../lib/api/client';

const TERMINAL_STATES = new Set(['COMPLETED', 'FAILED', 'CANCELLED']);
const POLL_INTERVAL_MS = 2500;

export interface ExecutionStoreState {
  // Existing state
  connectionStatus: SocketStatus;
  executionStatus: ExecutionStatus;
  executionGraph: ExecutionGraph | null;
  selectedNode: string | null;
  currentTick: number;
  events: EventEnvelope<any>[];
  isConnected: boolean;
  isLoading: boolean;
  error: string | null;

  // Milestone 2 state
  executions: ExecutionRecord[];
  activeExecution: ExecutionRecord | null;
  activeAgents: AgentNode[];
  activeEvents: any[];

  // Milestone 3 state
  activeTimeline: TimelineEntry[];
  _pollTimer: ReturnType<typeof setInterval> | null;

  // Methods
  connect: () => void;
  disconnect: () => void;
  setExecution: (status: ExecutionStatus, graph: ExecutionGraph) => void;
  selectNode: (nodeId: string | null) => void;
  applyEvent: (event: EventEnvelope<any>) => void;
  clearExecution: () => void;
  loadExecutions: () => Promise<void>;
  selectExecution: (id: string) => Promise<void>;
  triggerExecution: (prompt: string, mode?: string) => Promise<void>;
  cancelExecution: (id: string) => Promise<void>;
  _startPolling: (id: string) => void;
  _stopPolling: () => void;
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

    // Refresh the active execution when we receive an event for it
    const active = get().activeExecution;
    if (active && envelope.executionId === active.id) {
      get().selectExecution(active.id).catch(() => {});
    }
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

    executions: [],
    activeExecution: null,
    activeAgents: [],
    activeEvents: [],
    activeTimeline: [],
    _pollTimer: null,

    connect: () => {
      set({ isLoading: true });
      socketClient.connect();
      set({ isLoading: false });
    },

    disconnect: () => {
      get()._stopPolling();
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

        let newStatus = state.executionStatus;
        let newGraph = state.executionGraph;
        let newTick = state.currentTick;

        const eventType = envelope.type as string;
        switch (eventType) {
          case 'ExecutionStarted':
            newStatus = 'RUNNING';
            if (!newGraph) {
              newGraph = { nodes: [], edges: [] };
            }
            break;

          case 'ExecutionFinished':
          case 'ExecutionCompleted':
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
          case 'AgentStarted':
            if (newGraph && envelope.payload) {
              const payload = envelope.payload as { nodeId?: string; agentName?: string; agent_id?: string };
              const nodeId = payload.nodeId ?? `${envelope.executionId}_${payload.agent_id}`;
              const agentName = payload.agentName ?? payload.agent_id ?? 'Unknown';
              const nodes = [...newGraph.nodes];
              const existingIdx = nodes.findIndex(n => n.id === nodeId);

              if (existingIdx >= 0) {
                nodes[existingIdx] = { ...nodes[existingIdx], status: 'RUNNING' };
              } else {
                nodes.push({ id: nodeId, agentName, status: 'RUNNING' });
              }
              newGraph = { ...newGraph, nodes };
            }
            break;

          case 'NodeCompleted':
          case 'AgentCompleted':
            if (newGraph && envelope.payload) {
              const payload = envelope.payload as { nodeId?: string; agent_id?: string };
              const nodeId = payload.nodeId ?? `${envelope.executionId}_${payload.agent_id}`;
              const nodes = [...newGraph.nodes];
              const existingIdx = nodes.findIndex(n => n.id === nodeId);
              if (existingIdx >= 0) {
                nodes[existingIdx] = { ...nodes[existingIdx], status: 'COMPLETE' };
                newGraph = { ...newGraph, nodes };
              }
            }
            break;
        }

        return { events: newEvents, executionStatus: newStatus, executionGraph: newGraph, currentTick: newTick };
      });
    },

    clearExecution: () => {
      get()._stopPolling();
      set({
        executionStatus: 'IDLE',
        executionGraph: null,
        selectedNode: null,
        currentTick: 0,
        events: [],
        activeExecution: null,
        activeAgents: [],
        activeEvents: [],
        activeTimeline: [],
      });
    },

    loadExecutions: async () => {
      set({ isLoading: true });
      try {
        const data = await apiGet<ExecutionRecord[]>('/executions');
        set({ executions: data, error: null });
      } catch (err: any) {
        set({ error: err.message || 'Failed to load executions' });
      } finally {
        set({ isLoading: false });
      }
    },

    selectExecution: async (id: string) => {
      try {
        const [execution, agents, events, timeline] = await Promise.all([
          apiGet<ExecutionRecord>(`/executions/${id}`),
          apiGet<AgentNode[]>(`/executions/${id}/agents`),
          apiGet<any[]>(`/executions/${id}/events`),
          apiGet<TimelineEntry[]>(`/executions/${id}/timeline`).catch(() => [] as TimelineEntry[]),
        ]);

        // Map AgentNodes to ExecutionGraph nodes for backward compatibility
        const nodes = agents.map(a => ({
          id: a.id,
          agentName: a.name,
          status: (a.status === 'COMPLETED' ? 'COMPLETE' : a.status) as any,
          startTime: a.latency ? '0' : undefined,
          endTime: undefined,
        }));

        const edges = agents
          .filter(a => a.parentId)
          .map(a => ({
            id: `edge_${a.parentId}_${a.id}`,
            source: a.parentId!,
            target: a.id,
          }));

        set({
          activeExecution: execution,
          activeAgents: agents,
          activeEvents: events,
          activeTimeline: timeline,
          executionGraph: { nodes, edges },
          error: null,
        });

        // Also refresh the executions list entry
        set(state => ({
          executions: state.executions.map(e => e.id === id ? execution : e),
        }));

        // Start or stop polling based on terminal state
        if (TERMINAL_STATES.has(execution.status)) {
          get()._stopPolling();
        } else {
          get()._startPolling(id);
        }
      } catch (err: any) {
        set({ error: err.message || 'Failed to select execution' });
      }
    },

    triggerExecution: async (prompt: string, mode = 'LIVE') => {
      set({ isLoading: true });
      try {
        const data = await apiPost<ExecutionRecord>('/executions', { prompt, mode });
        set((state) => ({
          executions: [data, ...state.executions],
          activeExecution: data,
          activeTimeline: data.timeline ?? [],
          error: null,
        }));
        await get().selectExecution(data.id);
      } catch (err: any) {
        set({ error: err.message || 'Failed to trigger execution' });
      } finally {
        set({ isLoading: false });
      }
    },

    cancelExecution: async (id: string) => {
      set({ isLoading: true });
      try {
        const data = await apiPost<ExecutionRecord>(`/executions/${id}/cancel`);
        get()._stopPolling();
        set((state) => ({
          executions: state.executions.map(e => e.id === id ? data : e),
          activeExecution: state.activeExecution?.id === id ? data : state.activeExecution,
          error: null,
        }));
      } catch (err: any) {
        set({ error: err.message || 'Failed to cancel execution' });
      } finally {
        set({ isLoading: false });
      }
    },

    _startPolling: (id: string) => {
      const { _pollTimer } = get();
      if (_pollTimer) return; // already polling

      const timer = setInterval(() => {
        const active = get().activeExecution;
        if (!active || active.id !== id) {
          get()._stopPolling();
          return;
        }
        if (TERMINAL_STATES.has(active.status)) {
          get()._stopPolling();
          return;
        }
        get().selectExecution(id).catch(() => {});
      }, POLL_INTERVAL_MS);

      set({ _pollTimer: timer });
    },

    _stopPolling: () => {
      const { _pollTimer } = get();
      if (_pollTimer) {
        clearInterval(_pollTimer);
        set({ _pollTimer: null });
      }
    },
  };
});
