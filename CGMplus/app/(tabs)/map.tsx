import React from 'react';
import { View, StyleSheet } from 'react-native';
import { WebView } from 'react-native-webview';

const LEAFLET_HTML = `
<!DOCTYPE html>
<html>
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="referrerpolicy" content="origin-when-cross-origin" />
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <style>
    body { margin: 0; padding: 0; }
    #map { width: 100vw; height: 100vh; }
  </style>
</head>
<body>
  <div id="map"></div>
  <script>
    const map = L.map('map').setView([42.6977, 23.3219], 13);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
      // FIX 2: pass the policy here too so XHR/fetch for tiles obeys it
      referrerPolicy: 'origin-when-cross-origin',
    }).addTo(map);

    function makeIcon(emoji) {
      return L.divIcon({
        className: '',
        html: '<div style="font-size:20px;line-height:1;">' + emoji + '</div>',
        iconSize: [26, 26],
        iconAnchor: [13, 13],
        popupAnchor: [0, -14],
      });
    }
    const icons = {
      bus:     makeIcon('🚌'),
      tram:    makeIcon('🚃'),
      trolley: makeIcon('🚎'),
      subway:  makeIcon('🚇'),
    };

    async function loadStops() {
      const query = \`
        [out:json][timeout:25];
        (
          node["highway"="bus_stop"]({{bbox}});
          node["railway"="tram_stop"]({{bbox}});
          node["railway"="station"]["station"="subway"]({{bbox}});
          node["trolleybus"="yes"]({{bbox}});
        );
        out body;
      \`.replace(/\\{\\{bbox\\}\\}/g, getBbox());

      try {
        const res  = await fetch(
          'https://overpass-api.de/api/interpreter',
          { method: 'POST', body: 'data=' + encodeURIComponent(query) }
        );
        const data = await res.json();
        data.elements.forEach(addStopMarker);
      } catch (e) {
        console.error('Overpass fetch failed', e);
      }
    }

    function getBbox() {
      const b = map.getBounds();
      // Overpass expects: south,west,north,east
      return [
        b.getSouth().toFixed(6),
        b.getWest().toFixed(6),
        b.getNorth().toFixed(6),
        b.getEast().toFixed(6),
      ].join(',');
    }

    function detectType(tags) {
      if (tags.railway === 'station' && tags.station === 'subway') return 'subway';
      if (tags.railway === 'tram_stop')  return 'tram';
      if (tags.trolleybus === 'yes')     return 'trolley';
      if (tags.highway  === 'bus_stop')  return 'bus';
      return null;
    }

    function addStopMarker(node) {
      const type = detectType(node.tags || {});
      if (!type) return;                          // skip anything unrecognised
      const icon  = icons[type];
      const name  = node.tags.name || (type.charAt(0).toUpperCase() + type.slice(1) + ' stop');
      L.marker([node.lat, node.lon], { icon })
        .bindPopup('<b>' + name + '</b><br/><small>' + type + '</small>')
        .addTo(map);
    }

    map.whenReady(loadStops);
    map.on('moveend', loadStops);

    const vehicleMarkers = {};

    function handleVehicles(vehicles) {
      const seen         = new Set();
      const allowedTypes = ['bus', 'tram', 'trolley', 'subway'];

      vehicles.forEach(v => {
        if (!allowedTypes.includes((v.type || '').toLowerCase())) return;
        seen.add(v.id);
        const icon = icons[(v.type || '').toLowerCase()] || icons.bus;
        if (vehicleMarkers[v.id]) {
          vehicleMarkers[v.id].setLatLng([v.lat, v.lng]);
        } else {
          vehicleMarkers[v.id] = L.marker([v.lat, v.lng], { icon })
            .bindPopup('Route ' + v.routeId)
            .addTo(map);
        }
      });

      Object.keys(vehicleMarkers).forEach(id => {
        if (!seen.has(id)) {
          map.removeLayer(vehicleMarkers[id]);
          delete vehicleMarkers[id];
        }
      });
    }

    document.addEventListener('message', e => handleVehicles(JSON.parse(e.data)));
    window.addEventListener('message',   e => handleVehicles(JSON.parse(e.data)));
  </script>
</body>
</html>
`;

export default function MapScreen() {
  return (
    <View style={styles.container}>
      <WebView
        originWhitelist={['*']}
        source={{ html: LEAFLET_HTML }}
        style={styles.map}
        javaScriptEnabled
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  map:       { flex: 1 },
});
