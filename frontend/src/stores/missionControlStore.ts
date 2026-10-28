import { create } from 'zustand';
import { apiGet } from '../lib/api/client';

export interface MissionControlOverview {
  activeExecutions: number;
  queuedExecutions: number;
  completedExecutions: number;
  failedExecutions: number;
  cancelledExecutions: number;
  queueLength: number;
  schedulerWorkers: number;
  runningAgents: number;
  successRate: number;
  averageLatency: number;
  totalTokens: number;
  estimatedCost: number;
}

export interface ActiveExecutionSnapshot {
  id: string;
  status: string;
  userPrompt: string;
  currentAgent: string;
  progress: number;
  elapsed: number;
  executionMode: string;
}

export interface ActiveAgentSnapshot {
  agentName: string;
  executionId: string;
  status: string;
  tokens: number;
  latency: number;
  retryCount: number;
}

export interface QueuedExecutionSnapshot {
  id: string;
  position: number;
  waitingTime: number;
  executionMode: string;
  userPrompt: string;
}

export interface MissionControlEvent {
  executionId: string;
  timestamp: number;
  event: string;
  detail: string;
  agent?: string;
}

export interface MissionControlHealth {
  overall: 'GREEN' | 'YELLOW' | 'RED';
  scheduler: 'GREEN' | 'YELLOW' | 'RED';
  eventBus: 'GREEN' | 'YELLOW' | 'RED';
  store: 'GREEN' | 'YELLOW' | 'RED';
  queueDepth: number;
  workerCount: number;
  activeExecutionCount: number;
}

export interface MissionControlStoreState {
  overview: MissionControlOverview | null;
  activeExecutions: ActiveExecutionSnapshot[];
  activeAgents: ActiveAgentSnapshot[];
  queuedExecutions: QueuedExecutionSnapshot[];
  events: MissionControlEvent[];
  health: MissionControlHealth | null;
  isLoading: boolean;
  error: string | null;
  _refreshInterval: ReturnType<typeof setInterval> | null;

  fetchSnapshot: () => Promise<void>;
  startPolling: (intervalMs?: number) => void;
  stopPolling: () => void;
}

export const useMissionControlStore = create<MissionControlStoreState>((set, get) => {
  return {
    overview: null,
    activeExecutions: [],
    activeAgents: [],
    queuedExecutions: [],
    events: [],
    health: null,
    isLoading: false,
    error: null,
    _refreshInterval: null,

    fetchSnapshot: async () => {
      // Do not set global isLoading to true constantly to prevent flashing,
      // but do set it on the initial load.
      const isInitial = !get().overview;
      if (isInitial) {
        set({ isLoading: true });
      }

      try {
        const [overview, activeExecutions, activeAgents, queuedExecutions, events, health] = await Promise.all([
          apiGet<MissionControlOverview>('/mission-control/overview'),
          apiGet<ActiveExecutionSnapshot[]>('/mission-control/runtime'),
          apiGet<ActiveAgentSnapshot[]>('/mission-control/active-agents'),
          apiGet<QueuedExecutionSnapshot[]>('/mission-control/queued'),
          apiGet<MissionControlEvent[]>('/mission-control/events'),
          apiGet<MissionControlHealth>('/mission-control/health'),
        ]);

        set({
          overview,
          activeExecutions,
          activeAgents,
          queuedExecutions,
          events,
          health,
          error: null,
        });
      } catch (err: any) {
        set({ error: err.message || 'Failed to fetch Mission Control metrics.' });
      } finally {
        if (isInitial) {
          set({ isLoading: false });
        }
      }
    },

    startPolling: (intervalMs = 2000) => {
      const { _refreshInterval } = get();
      if (_refreshInterval) return;

      // Fetch immediately, then start interval
      get().fetchSnapshot().catch(() => {});

      const timer = setInterval(() => {
        get().fetchSnapshot().catch(() => {});
      }, intervalMs);

      set({ _refreshInterval: timer });
    },

    stopPolling: () => {
      const { _refreshInterval } = get();
      if (_refreshInterval) {
        clearInterval(_refreshInterval);
        set({ _refreshInterval: null });
      }
    },
  };
});
