import { create } from 'zustand';
import { socketClient } from '../lib/socket';
import type { EventEnvelope } from '../types/events';

export interface TimelineFilters {
  types: string[];
  agents: string[];
  ticks: number[];
  severities: string[];
}

export interface TimelineStoreState {
  events: EventEnvelope<any>[];
  selectedEventId: string | null;
  pinnedEventIds: Set<string>;
  searchQuery: string;
  filters: TimelineFilters;
  autoScroll: boolean;
  paused: boolean;
  
  // Actions
  addEvent: (event: EventEnvelope<any>) => void;
  clearEvents: () => void;
  selectEvent: (eventId: string | null) => void;
  togglePin: (eventId: string) => void;
  setSearchQuery: (query: string) => void;
  setFilters: (filters: TimelineFilters) => void;
  togglePause: () => void;
  toggleAutoScroll: () => void;
}

export const useTimelineStore = create<TimelineStoreState>((set, get) => {
  // TimelineStore subscribes independently to the WebSocket
  socketClient.onMessage((envelope) => {
    if (!get().paused) {
      get().addEvent(envelope);
    }
  });

  return {
    events: [],
    selectedEventId: null,
    pinnedEventIds: new Set<string>(),
    searchQuery: '',
    filters: { types: [], agents: [], ticks: [], severities: [] },
    autoScroll: true,
    paused: false,

    addEvent: (event) => set((state) => ({ events: [...state.events, event] })),
    clearEvents: () => set({ events: [], selectedEventId: null, pinnedEventIds: new Set() }),
    selectEvent: (eventId) => set({ selectedEventId: eventId }),
    togglePin: (eventId) => set((state) => {
      const newPins = new Set(state.pinnedEventIds);
      if (newPins.has(eventId)) {
        newPins.delete(eventId);
      } else {
        newPins.add(eventId);
      }
      return { pinnedEventIds: newPins };
    }),
    setSearchQuery: (query) => set({ searchQuery: query }),
    setFilters: (filters) => set({ filters }),
    togglePause: () => set((state) => ({ paused: !state.paused })),
    toggleAutoScroll: () => set((state) => ({ autoScroll: !state.autoScroll })),
  };
});
