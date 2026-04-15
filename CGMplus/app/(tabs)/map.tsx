import React, { useRef, useEffect, useState } from 'react';
import { View, StyleSheet } from 'react-native';
import { WebView } from 'react-native-webview';
import { useGtfsData } from '@/hooks/use-gtfs-data';

const MIN_ZOOM = 16;

export default function MapScreen() {
  const webViewRef = useRef<WebView>(null);
  const [status, setStatus] = useState({ vehicles: 0, stops: 0, error: '' });
  const gtfsData = useGtfsData();

  // ── WebView Injection ───────────────────────────────────────────────────

  const inject = (code: string) => {
    webViewRef.current?.injectJavaScript(code + '; true;');
  };

  useEffect(() => {
    // Subscribe to global GTFS data
    const unsubscribe = gtfsData.subscribe((type: string, data: any[]) => {
      if (type === 'stops') {
        setStatus(prev => ({ ...prev, stops: data.length }));
        inject(`window.receiveData('stops', ${JSON.stringify(data)})`);
      } else if (type === 'routes') {
        inject(`window.receiveData('routes', ${JSON.stringify(data)})`);
      } else if (type === 'trips') {
        inject(`window.receiveData('trips', ${JSON.stringify(data)})`);
      } else if (type === 'vehicles') {
        setStatus(prev => ({ ...prev, vehicles: data.length, error: '' }));
        inject(`window.receiveData('vehicles', ${JSON.stringify(data)})`);
      }
    });

    return () => unsubscribe();
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
    const map = L.map('map', {
      preferCanvas: true,
      maxNativeZoom: 18,
      zoomAnimation: false,
      fadeAnimation: false,
      markerZoomAnimation: false
    }).setView([42.6977, 23.3219], 15);

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

    function getVehicleType(vehicleId) {
      if (vehicleId.startsWith('TB')) return { type: 'trolley', color: '#2175e2' };
      if (vehicleId.startsWith('TM')) return { type: 'tram', color: '#ffae6f' };
      if (vehicleId.startsWith('A')) return { type: 'bus', color: '#bd3535' };
      return { type: 'unknown', color: '#999999' };
    }

    function makeVehicleIcon(routeNumber, vehicleId, heading, headsign, isExpanded) {
      const { type, color } = getVehicleType(vehicleId);
      const rotation = heading || 0;
      const displayHeadsign = (headsign || '').substring(0, 25); // Truncate headsign

      let svgWidth, rectWidth, svg;

      if (isExpanded) {
        // Expanded mode: show route number and headsign
        const headsignLength = displayHeadsign.length;
        const baseWidth = 56;
        const charWidth = 4.5;
        rectWidth = baseWidth + (headsignLength * charWidth);
        svgWidth = Math.max(80, rectWidth + 8);

        const rectX = -(rectWidth / 2);
        const headsignX = rectX + rectWidth - 6;

        svg = '<svg width="' + svgWidth + '" height="48" viewBox="0 0 ' + svgWidth + ' 48" xmlns="http://www.w3.org/2000/svg">' +
          '<g transform="translate(' + (svgWidth / 2) + ',20) rotate(' + rotation + ')">' +
            '<rect x="' + rectX + '" y="-11" width="' + rectWidth + '" height="22" fill="' + color + '" stroke="white" stroke-width="2" rx="8"/>' +
            '<polygon points="' + (rectX + rectWidth + 5) + ',0 ' + (rectX + rectWidth + 10) + ',8 ' + (rectX + rectWidth) + ',8" fill="white"/>' +
            '<text x="' + (rectX + 12) + '" y="3" font-size="12" font-weight="900" fill="white" text-anchor="middle" dominant-baseline="middle">' + routeNumber + '</text>' +
            '<text x="' + headsignX + '" y="3" font-size="8" font-weight="700" fill="white" text-anchor="end" dominant-baseline="middle">' + displayHeadsign + '</text>' +
          '</g>' +
          '</svg>';
      } else {
        // Collapsed mode: show only route number
        rectWidth = 36;
        svgWidth = 48;
        const rectX = -18;

        svg = '<svg width="' + svgWidth + '" height="48" viewBox="0 0 ' + svgWidth + ' 48" xmlns="http://www.w3.org/2000/svg">' +
          '<g transform="translate(' + (svgWidth / 2) + ',20) rotate(' + rotation + ')">' +
            '<rect x="' + rectX + '" y="-11" width="' + rectWidth + '" height="22" fill="' + color + '" stroke="white" stroke-width="2" rx="8"/>' +
            '<polygon points="19,0 24,8 14,8" fill="white"/>' +
            '<text x="0" y="2" font-size="12" font-weight="900" fill="white" text-anchor="middle" dominant-baseline="middle">' + routeNumber + '</text>' +
          '</g>' +
          '</svg>';
      }

      return L.divIcon({ className: '', html: svg, iconSize: [svgWidth, 48], iconAnchor: [svgWidth / 2, 24], popupAnchor: [0, -24] });
    }
    const ICONS = { s: makeIcon('📍', 'stop-icon') };

    const stopsLayer = L.layerGroup().addTo(map);
    const vehicleMarkers = {};
    const expandedVehicles = new Set();
    let allStops = [];
    let allRoutes = [];
    let allTrips = [];
    let lastVehicles = [];

    window.receiveData = function(type, data) {
      if (type === 'stops') {
        allStops = data;
        renderStops();
      } else if (type === 'routes') {
        allRoutes = data;
        console.log('Routes data received:', allRoutes.length);
      } else if (type === 'trips') {
        allTrips = data;
        console.log('Trips data received:', allTrips.length);
      } else if (type === 'vehicles') {
        lastVehicles = data;
        updateVehicles(data);
      }
      updateHud(Object.keys(vehicleMarkers).length, allStops.length, '');
    };

    function getRouteInfo(routeId) {
      const route = allRoutes.find(r => r.route_id === routeId);
      if (route) {
        return {
          shortName: route.route_short_name || routeId,
          longName: route.route_long_name || 'N/A',
          color: '#' + (route.route_color || 'CCCCCC'),
          textColor: '#' + (route.route_text_color || '000000')
        };
      }
      return { shortName: routeId, longName: 'Unknown', color: '#CCCCCC', textColor: '#000000' };
    }

    function getTripHeadsign(tripId, routeId) {
      if (tripId) {
        const trip = allTrips.find(t => t.trip_id === tripId);
        if (trip) return trip.trip_headsign || 'Unknown';
      }
      return 'Unknown';
    }

    function renderStops() {
      stopsLayer.clearLayers();
      if (map.getZoom() < MIN_ZOOM) return;
      const bounds = map.getBounds();
      allStops.forEach(s => {
        if (!s.stop_id || !s.stop_code || !s.stop_name) return;
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
      const bounds = map.getBounds();
      const padding = 0.01; // Padding to load markers slightly outside view
      const expandedBounds = bounds.pad(padding);

      if (!tooZoomedOut) {
        list.forEach(v => {
          const id = v.vehicle?.id || v.id;
          const lat = parseFloat(v.position?.latitude);
          const lon = parseFloat(v.position?.longitude);
          if (!id || isNaN(lat) || isNaN(lon)) return;

          const latlng = L.latLng(lat, lon);
          const inBounds = expandedBounds.contains(latlng);

          if (inBounds) {
            seen.add(id);
            const routeId = v.trip?.route_id || 'Unknown';
            const tripId = v.trip?.trip_id;
            const routeInfo = getRouteInfo(routeId);
            const headsign = getTripHeadsign(tripId, routeId);
            const heading = v.position?.bearing || 0;
            const popup = '<b>' + routeInfo.shortName + '</b><br>' +
                          '<small>' + headsign + '</small><br>' +
                          'ID: ' + id;

            if (vehicleMarkers[id]) {
              vehicleMarkers[id].setLatLng([lat, lon]);
              const isExpanded = expandedVehicles.has(id);
              vehicleMarkers[id].setIcon(makeVehicleIcon(routeInfo.shortName, id, heading, headsign, isExpanded));
              vehicleMarkers[id].getPopup().setContent(popup);
            } else {
              const isExpanded = false;
              vehicleMarkers[id] = L.marker([lat, lon], {
                icon: makeVehicleIcon(routeInfo.shortName, id, heading, headsign, isExpanded)
              }).bindPopup(popup).addTo(map);

              // Track popup state to control expanded view
              vehicleMarkers[id].on('popupopen', function() {
                expandedVehicles.add(id);
                const currentData = lastVehicles.find(v => (v.vehicle?.id || v.id) === id);
                if (currentData) {
                  const rid = currentData.trip?.route_id || 'Unknown';
                  const rInfo = getRouteInfo(rid);
                  const h = currentData.position?.bearing || 0;
                  const hs = currentData.trip?.trip_id ? (allTrips.find(t => t.trip_id === currentData.trip?.trip_id)?.trip_headsign || 'Unknown') : 'Unknown';
                  vehicleMarkers[id].setIcon(makeVehicleIcon(rInfo.shortName, id, h, hs, true));
                }
              });

              vehicleMarkers[id].on('popupclose', function() {
                expandedVehicles.delete(id);
                const currentData = lastVehicles.find(v => (v.vehicle?.id || v.id) === id);
                if (currentData) {
                  const rid = currentData.trip?.route_id || 'Unknown';
                  const rInfo = getRouteInfo(rid);
                  const h = currentData.position?.bearing || 0;
                  const hs = currentData.trip?.trip_id ? (allTrips.find(t => t.trip_id === currentData.trip?.trip_id)?.trip_headsign || 'Unknown') : 'Unknown';
                  vehicleMarkers[id].setIcon(makeVehicleIcon(rInfo.shortName, id, h, hs, false));
                }
              });
            }
          }
        });
      }

      // Remove vehicles outside bounds
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
        javaScriptEnabled={true}
        scrollEnabled={false}
        scalesPageToFit={false}
        nestedScrollEnabled={false}
        startInLoadingState={true}
        allowFileAccessFromFileURLs={true}
        allowUniversalAccessFromFileURLs={true}
        onMessage={(e) => console.log('[WebView]', e.nativeEvent.data)}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  map: { flex: 1 },
});
