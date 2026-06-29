import type { EventEnvelope } from '../../types/events';

export class SocketSerializer {
  public static deserialize(data: string): EventEnvelope<any> | null {
    try {
      const envelope = JSON.parse(data) as EventEnvelope<any>;
      return envelope;
    } catch (e) {
      console.error(`[WebSocket] Failed to parse message:`, data);
      return null;
    }
  }
}
