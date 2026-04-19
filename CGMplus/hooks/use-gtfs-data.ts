import React, { useEffect, useRef, useCallback } from 'react';

const API_HOST = process.env.EXPO_PUBLIC_GTFS_HOST || process.env.EXPO_PUBLIC_API_HOST || '192.168.1.109';
const API_PORT = process.env.EXPO_PUBLIC_GTFS_PORT || process.env.EXPO_PUBLIC_API_PORT || '5000';
const GTFS_API_PREFIX_RAW = process.env.EXPO_PUBLIC_GTFS_API_PREFIX || process.env.EXPO_PUBLIC_API_PREFIX || '/api/v1';
const GTFS_API_PREFIX = GTFS_API_PREFIX_RAW.startsWith('/') ? GTFS_API_PREFIX_RAW : `/${GTFS_API_PREFIX_RAW}`;
const GTFS_BASE = `http://${API_HOST}:${API_PORT}${GTFS_API_PREFIX}`;
const VEHICLE_POLL_MS = 10000;

// Global state to store fetched data
let globalStops: any[] = [];
let globalRoutes: any[] = [];
let globalVehicles: any[] = [];
let globalTrips: any[] = [];
let globalAlerts: any[] = [];
let globalSubscribers: Set<(type: string, data: any[]) => void> = new Set();
let globalInit = false;
let globalTimer: ReturnType<typeof setInterval> | null = null;
let globalAlertsTimer: ReturnType<typeof setInterval> | null = null;

export function useGtfsData() {
  const fetchStops = useCallback(async () => {
    const url = `${GTFS_BASE}/static/static/stops`;
    console.log('[GTFS-Global] Fetching stops from:', url);
    try {
      let page = 1, pages = 1, all: any[] = [];
      while (page <= pages) {
        const res = await fetch(`${url}?page=${page}`);
        if (!res.ok) throw new Error(`Stops HTTP ${res.status}`);
        const data = await res.json();
        all = all.concat(data.stops || []);
        pages = data.pagination?.pages || 1;
        page++;
      }
      console.log('[GTFS-Global] Stops loaded:', all.length);
      globalStops = all;
      globalSubscribers.forEach(cb => cb('stops', all));
    } catch (e: any) {
      console.error('[GTFS-Global] Stops error:', e.message, '| URL:', url);
    }
  }, []);

  const fetchRoutes = useCallback(async () => {
    const url = `${GTFS_BASE}/static/static/routes`;
    console.log('[GTFS-Global] Fetching routes from:', url);
    try {
      let page = 1, pages = 1, all: any[] = [];
      while (page <= pages) {
        const res = await fetch(`${url}?page=${page}`);
        if (!res.ok) throw new Error(`Routes HTTP ${res.status}`);
        const data = await res.json();
        all = all.concat(data.routes || []);
        pages = data.pagination?.pages || 1;
        page++;
      }
      console.log('[GTFS-Global] Routes loaded:', all.length);
      globalRoutes = all;
      globalSubscribers.forEach(cb => cb('routes', all));
    } catch (e: any) {
      console.error('[GTFS-Global] Routes error:', e.message, '| URL:', url);
    }
  }, []);

  const fetchTrips = useCallback(async () => {
    const url = `${GTFS_BASE}/static/static/trips`;
    console.log('[GTFS-Global] Fetching trips from:', url);
    try {
      let page = 1, pages = 1, all: any[] = [];
      while (page <= pages) {
        const res = await fetch(`${url}?page=${page}`);
        if (!res.ok) throw new Error(`Trips HTTP ${res.status}`);
        const data = await res.json();
        all = all.concat(data.trips || []);
        pages = data.pagination?.pages || 1;
        page++;
      }
      console.log('[GTFS-Global] Trips loaded:', all.length);
      globalTrips = all;
      globalSubscribers.forEach(cb => cb('trips', all));
    } catch (e: any) {
      console.error('[GTFS-Global] Trips error:', e.message, '| URL:', url);
    }
  }, []);

  const fetchVehicles = useCallback(async () => {
    const url = `${GTFS_BASE}/realtime/vehicle-positions`;
    try {
      const res = await fetch(url);
      if (!res.ok) throw new Error(`Vehicles HTTP ${res.status}`);
      const data = await res.json();
      const list = data.vehicle_positions || [];
      console.log('[GTFS-Global] Vehicles loaded:', list.length);
      globalVehicles = list;
      globalSubscribers.forEach(cb => cb('vehicles', list));
    } catch (e: any) {
      console.error('[GTFS-Global] Vehicles error:', e.message, '| URL:', url);
    }
  }, []);

  const fetchAlerts = useCallback(async () => {
    const url = `${GTFS_BASE}/realtime/alerts`;
    console.log('[GTFS-Global] Fetching alerts from:', url);
    try {
      const alertsResponse = await fetch(url);
      if (!alertsResponse.ok) throw new Error(`Alerts HTTP ${alertsResponse.status}`);
      const alertsData = await alertsResponse.json();
      const rawAlerts = alertsData.alerts || [];

      // Create route map for translating route_id to route_short_name
      const routeMap: Record<string, string> = {};
      if (globalRoutes.length > 0) {
        globalRoutes.forEach((route: any) => {
          routeMap[route.route_id] = route.route_short_name || route.route_id;
        });
      }

      // Process alerts
      const processedAlerts: any[] = [];

      rawAlerts.forEach((alert: any) => {
        // Get Bulgarian description
        const descriptions = alert.description || [];
        const bgDescription = descriptions.find((d: any) => d.language === 'bg')?.text;

        if (!bgDescription) return; // Skip if no Bulgarian description

        // Get affected routes
        const affectedRoutes = new Set<string>();
        const informedEntities = alert.informed_entities || [];

        informedEntities.forEach((entity: any) => {
          if (entity.route_id) {
            const routeNum = routeMap[entity.route_id] || entity.route_id;
            affectedRoutes.add(routeNum);
          }
        });

        // Get start time for sorting
        const activePeriods = alert.active_periods || [];
        const startTime = activePeriods[0]?.start || 0;

        if (affectedRoutes.size > 0) {
          processedAlerts.push({
            id: alert.id,
            start_time: startTime,
            routes: Array.from(affectedRoutes).sort((a, b) => {
              // Sort route numbers numerically
              const numA = parseInt(a, 10);
              const numB = parseInt(b, 10);
              if (!isNaN(numA) && !isNaN(numB)) return numA - numB;
              return a.localeCompare(b);
            }),
            description: bgDescription,
          });
        }
      });

      // Sort by start time descending (latest first)
      processedAlerts.sort((a, b) => b.start_time - a.start_time);

      console.log('[GTFS-Global] Alerts loaded:', processedAlerts.length);
      globalAlerts = processedAlerts;
      globalSubscribers.forEach(cb => cb('alerts', processedAlerts));
    } catch (e: any) {
      console.error('[GTFS-Global] Alerts error:', e.message, '| URL:', url);
    }
  }, []);

  const init = useCallback(() => {
    // Only initialize once globally
    if (globalInit) return;
    globalInit = true;

    // Initial fetches
    fetchStops();
    fetchRoutes();
    fetchTrips();
    fetchAlerts();

    // Poll vehicles
    fetchVehicles();
    if (globalTimer) clearInterval(globalTimer);
    globalTimer = setInterval(fetchVehicles, VEHICLE_POLL_MS);

    // Poll alerts every 5 minutes
    if (globalAlertsTimer) clearInterval(globalAlertsTimer);
    globalAlertsTimer = setInterval(fetchAlerts, 5 * 60 * 1000);
  }, [fetchStops, fetchRoutes, fetchTrips, fetchVehicles, fetchAlerts]);

  // Provide a reset if auth unmounts (optional, but good for global state)
  const reset = useCallback(() => {
    globalInit = false;
    if (globalTimer) {
      clearInterval(globalTimer);
      globalTimer = null;
    }
    if (globalAlertsTimer) {
      clearInterval(globalAlertsTimer);
      globalAlertsTimer = null;
    }
    globalStops = [];
    globalRoutes = [];
    globalVehicles = [];
    globalTrips = [];
    globalAlerts = [];
  }, []);

  return React.useMemo(() => ({
    init,
    reset,
    subscribe: (callback: (type: string, data: any[]) => void) => {
      globalSubscribers.add(callback);
      // Send current data immediately if available
      if (globalStops.length > 0) callback('stops', globalStops);
      if (globalRoutes.length > 0) callback('routes', globalRoutes);
      if (globalTrips.length > 0) callback('trips', globalTrips);
      if (globalVehicles.length > 0) callback('vehicles', globalVehicles);
      if (globalAlerts.length > 0) callback('alerts', globalAlerts);

      return () => {
        globalSubscribers.delete(callback);
      };
    },
    getStops: () => globalStops,
    getRoutes: () => globalRoutes,
    getTrips: () => globalTrips,
    getVehicles: () => globalVehicles,
    getAlerts: () => globalAlerts,
  }), [init, reset]);
}
