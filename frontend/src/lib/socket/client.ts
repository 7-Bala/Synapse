import { SocketSerializer } from './serializer';
import { SubscriptionManager } from './subscriptions';
import type { SocketCallback, StatusCallback } from './subscriptions';
import { ReconnectStrategy } from './reconnect';

export class WebSocketClient {
  private url: string;
  private ws: WebSocket | null = null;
  
  private subscriptions = new SubscriptionManager();
  private reconnectStrategy = new ReconnectStrategy();

  constructor(url: string = 'ws://localhost:8000/ws') {
    this.url = url;
  }

  public connect() {
    if (this.ws?.readyState === WebSocket.OPEN) return;
    
    this.subscriptions.notifyStatus('connecting');
    try {
      this.ws = new WebSocket(this.url);

      this.ws.onopen = () => {
        this.subscriptions.notifyStatus('connected');
        this.reconnectStrategy.reset();
      };

      this.ws.onmessage = (event) => {
        const envelope = SocketSerializer.deserialize(event.data);
        if (envelope) {
          this.subscriptions.notifyEvent(envelope);
        }
      };

      this.ws.onerror = (error) => {
        console.error(`[WebSocket] Error:`, error);
        this.subscriptions.notifyStatus('error');
      };

      this.ws.onclose = () => {
        this.subscriptions.notifyStatus('disconnected');
        this.ws = null;
        this.reconnectStrategy.attempt(() => this.connect());
      };
    } catch (e) {
      console.error(`[WebSocket] Connection failed:`, e);
      this.subscriptions.notifyStatus('error');
      this.reconnectStrategy.attempt(() => this.connect());
    }
  }

  public disconnect() {
    this.reconnectStrategy.clearTimer();
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.subscriptions.notifyStatus('disconnected');
  }

  public onMessage(handler: SocketCallback) {
    return this.subscriptions.addEventHandler(handler);
  }

  public onStatusChange(handler: StatusCallback) {
    return this.subscriptions.addStatusHandler(handler);
  }
}

export const socketClient = new WebSocketClient();
