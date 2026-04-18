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
let globalSubscribers: Set<(type: string, data: any[]) => void> = new Set();
let globalInit = false;
let globalTimer: ReturnType<typeof setInterval> | null = null;

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

  const init = useCallback(() => {
    // Only initialize once globally
    if (globalInit) return;
    globalInit = true;

    // Initial fetches
    fetchStops();
    fetchRoutes();
    fetchTrips();

    // Poll vehicles
    fetchVehicles();
    if (globalTimer) clearInterval(globalTimer);
    globalTimer = setInterval(fetchVehicles, VEHICLE_POLL_MS);
  }, [fetchStops, fetchRoutes, fetchTrips, fetchVehicles]);

  // Provide a reset if auth unmounts (optional, but good for global state)
  const reset = useCallback(() => {
    globalInit = false;
    if (globalTimer) {
      clearInterval(globalTimer);
      globalTimer = null;
    }
    globalStops = [];
    globalRoutes = [];
    globalVehicles = [];
    globalTrips = [];
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

      return () => {
        globalSubscribers.delete(callback);
      };
    },
    getStops: () => globalStops,
    getRoutes: () => globalRoutes,
    getTrips: () => globalTrips,
    getVehicles: () => globalVehicles,
  }), [init, reset]);
}
