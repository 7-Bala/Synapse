import type { EventEnvelope } from '../../types/events';

export type SocketStatus = 'connected' | 'disconnected' | 'connecting' | 'error';
export type SocketCallback = (envelope: EventEnvelope<any>) => void;
export type StatusCallback = (status: SocketStatus) => void;

export class SubscriptionManager {
  private eventHandlers: Set<SocketCallback> = new Set();
  private statusHandlers: Set<StatusCallback> = new Set();
  private currentStatus: SocketStatus = 'disconnected';

  public addEventHandler(handler: SocketCallback) {
    this.eventHandlers.add(handler);
    return () => this.eventHandlers.delete(handler);
  }

  public addStatusHandler(handler: StatusCallback) {
    this.statusHandlers.add(handler);
    // Send current status immediately upon subscription
    handler(this.currentStatus);
    return () => this.statusHandlers.delete(handler);
  }

  public notifyEvent(envelope: EventEnvelope<any>) {
    this.eventHandlers.forEach(handler => handler(envelope));
  }

  public notifyStatus(status: SocketStatus) {
    if (this.currentStatus !== status) {
      this.currentStatus = status;
      this.statusHandlers.forEach(handler => handler(status));
    }
  }
}
