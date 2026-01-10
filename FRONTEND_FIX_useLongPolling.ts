// COMPLETE WORKING useLongPolling.ts
// Copy this ENTIRE file - replace your current useLongPolling.ts

import { useEffect, useRef, useCallback } from 'react';

interface UseLongPollingOptions {
  apiBase?: string;
  enabled?: boolean;
  onConnect?: () => void;
  onDisconnect?: () => void;
  onError?: (error: Error) => void;
}

export const useLongPolling = (
  token: string | null,
  onEvent: (eventType: string, data: any) => void,
  options: UseLongPollingOptions = {}
) => {
  const {
    apiBase = 'http://127.0.0.1:8000/api/v1',
    enabled = true,
    onConnect,
    onDisconnect,
    onError
  } = options;

  const isPollingRef = useRef(false);
  const abortControllerRef = useRef<AbortController | null>(null);
  const mountedRef = useRef(true);

  const poll = useCallback(async () => {
    // CRITICAL: Prevent double polling
    if (isPollingRef.current) {
      console.log('[LongPolling] Already polling, ignoring duplicate call');
      return;
    }

    if (!token) {
      console.log('[LongPolling] No token, skipping poll');
      return;
    }

    console.log('[LongPolling] 🚀 Starting polling loop...');
    isPollingRef.current = true;
    onConnect?.();

    let requestCount = 0;

    // INFINITE LOOP - This is the key!
    while (isPollingRef.current && mountedRef.current) {
      requestCount++;
      console.log(`[LongPolling] 📡 Request #${requestCount} at ${new Date().toLocaleTimeString()}`);

      // Create fresh abort controller for each request
      abortControllerRef.current = new AbortController();

      try {
        const startTime = performance.now();

        const response = await fetch(
          `${apiBase}/communication/poll/events/?token=${token}`,
          {
            method: 'GET',
            signal: abortControllerRef.current.signal,
            headers: {
              'Accept': 'application/json',
            },
          }
        );

        const endTime = performance.now();
        const duration = (endTime - startTime) / 1000;

        console.log(`[LongPolling] ✅ Response received in ${duration.toFixed(2)}s`);

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();

        if (data.events && data.events.length > 0) {
          console.log(`[LongPolling] 📨 ${data.events.length} event(s) received`);

          // Process each event
          data.events.forEach((event: any, index: number) => {
            console.log(`[LongPolling] Processing event ${index + 1}: ${event.event}`);
            try {
              onEvent(event.event, event.data);
            } catch (error) {
              console.error('[LongPolling] Error in event handler:', error);
              // Don't stop polling if event handler fails
            }
          });
        } else {
          console.log('[LongPolling] No events (timeout)');
        }

        // CRITICAL: NO DELAY HERE!
        // Server already waited 5.5 seconds
        // Immediately continue the loop
        console.log('[LongPolling] 🔄 Continuing loop...');

      } catch (error: any) {
        if (error.name === 'AbortError') {
          console.log('[LongPolling] 🛑 Request aborted (component unmounting)');
          break; // Exit loop on abort
        }

        console.error('[LongPolling] ❌ Error:', error.message);
        onError?.(error);

        // Wait 2 seconds before retry on error
        console.log('[LongPolling] ⏳ Waiting 2s before retry...');
        await new Promise(resolve => setTimeout(resolve, 2000));

        if (!isPollingRef.current) break; // Check if we should still be polling
      }
    }

    console.log('[LongPolling] 🏁 Polling loop ended');
    isPollingRef.current = false;
    onDisconnect?.();

  }, [token, apiBase, onEvent, onConnect, onDisconnect, onError]);

  useEffect(() => {
    console.log('[LongPolling] Effect triggered - enabled:', enabled, 'hasToken:', !!token);

    // Set mounted flag
    mountedRef.current = true;

    if (enabled && token) {
      // Small delay to prevent double-mounting in React strict mode
      const timer = setTimeout(() => {
        if (mountedRef.current) {
          poll();
        }
      }, 100);

      return () => {
        console.log('[LongPolling] 🧹 Cleanup triggered');
        clearTimeout(timer);
        mountedRef.current = false;
        isPollingRef.current = false;

        if (abortControllerRef.current) {
          abortControllerRef.current.abort();
          abortControllerRef.current = null;
        }
      };
    }

    return () => {
      mountedRef.current = false;
    };
  }, [enabled, token, poll]);

  return {
    isPolling: isPollingRef.current
  };
};
