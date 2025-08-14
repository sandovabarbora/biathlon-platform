import { useEffect, useRef, useCallback } from 'react';
import { useAthleteStore } from '@/lib/store/athlete-store';
import toast from 'react-hot-toast';

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000';

export function useWebSocket(athleteId: number | null) {
  const ws = useRef<WebSocket | null>(null);
  const reconnectTimeout = useRef<NodeJS.Timeout>();
  const { setConnected, updateRealtimeData } = useAthleteStore();

  const connect = useCallback(() => {
    if (!athleteId) return;

    try {
      ws.current = new WebSocket(`${WS_URL}/api/v1/ws/${athleteId}`);

      ws.current.onopen = () => {
        setConnected(true);
        toast.success('Connected to real-time data');
      };

      ws.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          if (data.type === 'sensor_data') {
            updateRealtimeData(data.data);
          } else if (data.type === 'prediction') {
            // Handle predictions
          }
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      ws.current.onerror = (error) => {
        console.error('WebSocket error:', error);
        toast.error('Connection error');
      };

      ws.current.onclose = () => {
        setConnected(false);
        
        // Attempt reconnection
        reconnectTimeout.current = setTimeout(() => {
          toast('Reconnecting...', { icon: '🔄' });
          connect();
        }, 5000);
      };
    } catch (error) {
      console.error('Failed to connect WebSocket:', error);
    }
  }, [athleteId, setConnected, updateRealtimeData]);

  const disconnect = useCallback(() => {
    if (reconnectTimeout.current) {
      clearTimeout(reconnectTimeout.current);
    }
    
    if (ws.current) {
      ws.current.close();
      ws.current = null;
    }
    
    setConnected(false);
  }, [setConnected]);

  const sendMessage = useCallback((type: string, data: any) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({ type, data }));
    }
  }, []);

  useEffect(() => {
    connect();
    return () => disconnect();
  }, [athleteId, connect, disconnect]);

  return { sendMessage, isConnected: ws.current?.readyState === WebSocket.OPEN };
}
