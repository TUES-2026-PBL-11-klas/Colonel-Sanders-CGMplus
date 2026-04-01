import React, { useRef, useEffect, useState } from 'react';
import { View, StyleSheet } from 'react-native';
import { WebView } from 'react-native-webview';

const GTFS_BASE = `http://localhost:5000/api/v1`; //replace with your ip using "$ ip a" and getting wlp0s20f3
const VEHICLE_POLL_MS = 10000;
const MIN_ZOOM = 16;

export default function MapScreen() {
  const webViewRef = useRef<WebView>(null);
  const [status, setStatus] = useState({ vehicles: 0, stops: 0, error: '' });

  // ── Native Data Fetching ───────────────────────────────────────────────

  const inject = (code: string) => {
    webViewRef.current?.injectJavaScript(code + '; true;');
  };

  const fetchStops = async () => {
    console.log('[Native] Fetching stops from:', `${GTFS_BASE}/static/static/stops`);
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
      console.log('[Native] Stops loaded:', all.length);
      setStatus(prev => ({ ...prev, stops: all.length }));
      inject(`window.receiveData('stops', ${JSON.stringify(all)})`);
    } catch (e: any) {
      console.error('[Native] Stops error:', e.message);
      setStatus(prev => ({ ...prev, error: 'Stops: ' + e.message }));
    }
  };

  const fetchVehicles = async () => {
    try {
      const res = await fetch(`${GTFS_BASE}/realtime/vehicle-positions`);
      if (!res.ok) throw new Error(`Vehicles HTTP ${res.status}`);
      const data = await res.json();
      const list = data.vehicle_positions || [];
      setStatus(prev => ({ ...prev, vehicles: list.length, error: '' }));
      inject(`window.receiveData('vehicles', ${JSON.stringify(list)})`);
    } catch (e: any) {
      console.error('[Native] Vehicles error:', e.message);
      setStatus(prev => ({ ...prev, error: 'Vehicles: ' + e.message }));
    }
  };

  useEffect(() => {
    fetchStops();
    const timer = setInterval(fetchVehicles, VEHICLE_POLL_MS);
    fetchVehicles(); // initial fetch
    return () => clearInterval(timer);
  }, []);

  // ── Leaflet HTML ───────────────────────────────────────────────────────

  const LEAFLET_HTML = `
<!DOCTYPE html>
<html>
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <style>
    body { margin: 0; padding: 0; font-family: sans-serif; }
    #map { width: 100vw; height: 100vh; }
    .hud { background: rgba(255,255,255,0.9); padding: 8px; border: 1px solid #ccc; font-size: 11px; border-radius: 4px; }
    .stop-icon  { font-size: 16px; line-height: 1; filter: drop-shadow(0 1px 2px rgba(0,0,0,.35)); }
    .vehicle-icon { font-size: 24px; line-height: 1; filter: drop-shadow(0 1px 3px rgba(0,0,0,.5)); }
  </style>
</head>
<body>
  <div id="map"></div>
  <script>
    const MIN_ZOOM = ${MIN_ZOOM};
    const map = L.map('map').setView([42.6977, 23.3219], 15);

    L.tileLayer('https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}{r}.png', {
      subdomains: 'abcd', maxZoom: 20,
    }).addTo(map);
    L.tileLayer('https://{s}.basemaps.cartocdn.com/light_only_labels/{z}/{x}/{y}{r}.png', {
      subdomains: 'abcd', maxZoom: 20, pane: 'shadowPane',
    }).addTo(map);

    const hud = L.control({ position: 'topright' });
    hud.onAdd = function() {
      this._div = L.DomUtil.create('div', 'hud');
      this.update('Initializing…');
      return this._div;
    };
    hud.update = function(html) { this._div.innerHTML = html; };
    hud.addTo(map);

    function updateHud(vCount, sCount, err) {
      hud.update('<b>Native Bridge Active</b><br>' +
                 'Vehicles: ' + vCount + '<br>' +
                 'Stops (cache): ' + sCount +
                 (err ? '<br><span style="color:red">Error: ' + err + '</span>' : ''));
    }

    // ── Icons & Markers ──────────────────────────────────────────────────
    function makeIcon(emoji, cls) {
      return L.divIcon({ className: '', html: '<div class="' + cls + '">' + emoji + '</div>',
                         iconSize: [28,28], iconAnchor: [14,14], popupAnchor: [0,-16] });
    }
    const ICONS = { s: makeIcon('📍', 'stop-icon'), v: makeIcon('🚌', 'vehicle-icon') };

    const stopsLayer = L.layerGroup().addTo(map);
    const vehicleMarkers = {};
    let allStops = [];
    let lastVehicles = [];

    window.receiveData = function(type, data) {
      if (type === 'stops') {
        allStops = data;
        renderStops();
      } else if (type === 'vehicles') {
        lastVehicles = data;
        updateVehicles(data);
      }
      updateHud(Object.keys(vehicleMarkers).length, allStops.length, '');
    };

    function renderStops() {
      stopsLayer.clearLayers();
      if (map.getZoom() < MIN_ZOOM) return;
      const bounds = map.getBounds();
      allStops.forEach(s => {
        const lat = parseFloat(s.stop_lat || s.lat);
        const lon = parseFloat(s.stop_lon || s.lon);
        if (bounds.contains([lat, lon])) {
          L.marker([lat, lon], { icon: ICONS.s })
            .bindPopup('<b>' + s.stop_name + '</b><br>Спирка №: ' + (s.stop_code || '—'))
            .addTo(stopsLayer);
        }
      });
    }

    function updateVehicles(list) {
      const seen = new Set();
      const tooZoomedOut = map.getZoom() < MIN_ZOOM;

      if (!tooZoomedOut) {
        list.forEach(v => {
          const id = v.vehicle?.id || v.id;
          const lat = parseFloat(v.position?.latitude);
          const lon = parseFloat(v.position?.longitude);
          if (!id || isNaN(lat) || isNaN(lon)) return;
          seen.add(id);
          const popup = '<b>' + (v.trip?.route_id || 'Bus') + '</b><br>ID: ' + id;
          if (vehicleMarkers[id]) {
            vehicleMarkers[id].setLatLng([lat, lon]).getPopup().setContent(popup);
          } else {
            vehicleMarkers[id] = L.marker([lat, lon], { icon: ICONS.v }).bindPopup(popup).addTo(map);
          }
        });
      }

      for (const id in vehicleMarkers) {
        if (!seen.has(id)) {
          map.removeLayer(vehicleMarkers[id]);
          delete vehicleMarkers[id];
        }
      }
    }

    map.on('moveend', function() {
      renderStops();
      updateVehicles(lastVehicles);
    });
  </script>
</body>
</html>
`;

  return (
    <View style={styles.container}>
      <WebView
        ref={webViewRef}
        originWhitelist={['*']}
        source={{ html: LEAFLET_HTML }}
        style={styles.map}
        javaScriptEnabled
        onMessage={(e) => console.log('[WebView]', e.nativeEvent.data)}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  map: { flex: 1 },
});
