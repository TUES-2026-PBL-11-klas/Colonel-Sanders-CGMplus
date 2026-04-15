import { useEffect, useRef, useCallback } from 'react';

const GTFS_BASE = `http://192.168.1.52:5001/api/v1`;
const VEHICLE_POLL_MS = 10000;

// Global state to store fetched data
let globalStops: any[] = [];
let globalRoutes: any[] = [];
let globalVehicles: any[] = [];
let globalTrips: any[] = [];
let globalSubscribers: Set<(type: string, data: any[]) => void> = new Set();

export function useGtfsData() {
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const initRef = useRef(false);

  const fetchStops = useCallback(async () => {
    console.log('[GTFS-Global] Fetching stops from:', `${GTFS_BASE}/static/static/stops`);
    try {
      let page = 1, pages = 1, all: any[] = [];
      while (page <= pages) {
        const res = await fetch(`${GTFS_BASE}/static/static/stops?page=${page}`);
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
      console.error('[GTFS-Global] Stops error:', e.message);
    }
  }, []);

  const fetchRoutes = useCallback(async () => {
    console.log('[GTFS-Global] Fetching routes from:', `${GTFS_BASE}/static/static/routes`);
    try {
      let page = 1, pages = 1, all: any[] = [];
      while (page <= pages) {
        const res = await fetch(`${GTFS_BASE}/static/static/routes?page=${page}`);
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
      console.error('[GTFS-Global] Routes error:', e.message);
    }
  }, []);

  const fetchTrips = useCallback(async () => {
    console.log('[GTFS-Global] Fetching trips from:', `${GTFS_BASE}/static/static/trips`);
    try {
      let page = 1, pages = 1, all: any[] = [];
      while (page <= pages) {
        const res = await fetch(`${GTFS_BASE}/static/static/trips?page=${page}`);
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
      console.error('[GTFS-Global] Trips error:', e.message);
    }
  }, []);

  const fetchVehicles = useCallback(async () => {
    try {
      const res = await fetch(`${GTFS_BASE}/realtime/vehicle-positions`);
      if (!res.ok) throw new Error(`Vehicles HTTP ${res.status}`);
      const data = await res.json();
      const list = data.vehicle_positions || [];
      console.log('[GTFS-Global] Vehicles loaded:', list.length);
      globalVehicles = list;
      globalSubscribers.forEach(cb => cb('vehicles', list));
    } catch (e: any) {
      console.error('[GTFS-Global] Vehicles error:', e.message);
    }
  }, []);

  useEffect(() => {
    // Only initialize once
    if (initRef.current) return;
    initRef.current = true;

    // Initial fetches
    fetchStops();
    fetchRoutes();
    fetchTrips();

    // Poll vehicles
    fetchVehicles();
    timerRef.current = setInterval(fetchVehicles, VEHICLE_POLL_MS);

    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [fetchStops, fetchRoutes, fetchTrips, fetchVehicles]);

  return {
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
  };
}
