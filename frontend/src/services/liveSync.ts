import { EventSourcePolyfill } from 'event-source-polyfill';

export interface LiveSyncEvent {
  type: 'route_update' | 'store_update' | 'status_change' | 'optimization_complete';
  data: any;
  timestamp: string;
}

export type LiveSyncCallback = (event: LiveSyncEvent) => void;

class LiveSyncService {
  private eventSource: EventSourcePolyfill | null = null;
  private callbacks: Map<string, LiveSyncCallback[]> = new Map();
  private reconnectTimeout: NodeJS.Timeout | null = null;
  private maxReconnectAttempts = 5;
  private reconnectAttempts = 0;
  private reconnectDelay = 1000; // Start with 1 second

  private get baseUrl() {
    return process.env.NODE_ENV === 'production' 
      ? 'https://api.routeforce.com'
      : 'http://localhost:8000';
  }

  // Initialize connection
  connect(): void {
    if (this.eventSource) {
      this.disconnect();
    }

    try {
      this.eventSource = new EventSourcePolyfill(`${this.baseUrl}/api/livesync/stream`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token') || ''}`,
        },
      });

      this.eventSource.onopen = () => {
        console.log('LiveSync connected');
        this.reconnectAttempts = 0;
        this.reconnectDelay = 1000;
      };

      this.eventSource.onmessage = (event) => {
        try {
          const data: LiveSyncEvent = JSON.parse(event.data);
          this.handleEvent(data);
        } catch (error) {
          console.error('Failed to parse LiveSync event:', error);
        }
      };

      this.eventSource.onerror = () => {
        console.warn('LiveSync connection error');
        this.handleConnectionError();
      };

    } catch (error) {
      console.error('Failed to establish LiveSync connection:', error);
      this.fallbackToPolling();
    }
  }

  // Disconnect from live stream
  disconnect(): void {
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
    }
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
      this.reconnectTimeout = null;
    }
  }

  // Subscribe to specific event types
  subscribe(eventType: string, callback: LiveSyncCallback): () => void {
    if (!this.callbacks.has(eventType)) {
      this.callbacks.set(eventType, []);
    }
    this.callbacks.get(eventType)!.push(callback);

    // Return unsubscribe function
    return () => {
      const callbacks = this.callbacks.get(eventType);
      if (callbacks) {
        const index = callbacks.indexOf(callback);
        if (index > -1) {
          callbacks.splice(index, 1);
        }
      }
    };
  }

  // Handle incoming events
  private handleEvent(event: LiveSyncEvent): void {
    const callbacks = this.callbacks.get(event.type);
    if (callbacks) {
      callbacks.forEach(callback => {
        try {
          callback(event);
        } catch (error) {
          console.error('Error in LiveSync callback:', error);
        }
      });
    }
  }

  // Handle connection errors and reconnection
  private handleConnectionError(): void {
    this.disconnect();

    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      this.reconnectTimeout = setTimeout(() => {
        console.log(`Attempting LiveSync reconnection (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
        this.connect();
      }, this.reconnectDelay);

      // Exponential backoff
      this.reconnectDelay = Math.min(this.reconnectDelay * 2, 30000);
    } else {
      console.warn('Max LiveSync reconnection attempts reached, falling back to polling');
      this.fallbackToPolling();
    }
  }

  // Fallback to polling when SSE fails
  private fallbackToPolling(): void {
    console.log('Using polling fallback for live updates');
    
    // Poll every 30 seconds for updates
    setInterval(async () => {
      try {
        const response = await fetch(`${this.baseUrl}/api/livesync/poll`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('auth_token') || ''}`,
          },
        });
        
        if (response.ok) {
          const events: LiveSyncEvent[] = await response.json();
          events.forEach(event => this.handleEvent(event));
        }
      } catch (error) {
        console.error('Polling failed:', error);
      }
    }, 30000);
  }

  // Manually trigger refresh for specific data types
  async triggerRefresh(dataType: 'routes' | 'stores' | 'all'): Promise<void> {
    try {
      await fetch(`${this.baseUrl}/api/livesync/trigger`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token') || ''}`,
        },
        body: JSON.stringify({ dataType }),
      });
    } catch (error) {
      console.error('Failed to trigger refresh:', error);
    }
  }
}

// Create singleton instance
export const liveSyncService = new LiveSyncService();

// React hook for easy integration
export function useLiveSync(eventType: string, callback: LiveSyncCallback) {
  const React = require('react');
  
  React.useEffect(() => {
    const unsubscribe = liveSyncService.subscribe(eventType, callback);
    return unsubscribe;
  }, [eventType, callback]);
}

// Auto-start connection when service is imported
if (typeof window !== 'undefined') {
  liveSyncService.connect();
}
