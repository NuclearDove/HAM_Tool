/**
 * HAM Radio Toolbox - 通联地图 Tab 模块
 * 依赖: HAM.Core, HAM.Log, Leaflet
 */
(function(global) {
  'use strict';

  var Core = global.HAM && global.HAM.Core;
  var Log = global.HAM && global.HAM.Log;
  if (!Core || !Log) { console.error('HAM.Core or HAM.Log not loaded'); return; }

  var Module = {};
  var mapInstance = null;

  Module.mapRender = function() {
    var container = document.getElementById('map-container');
    if (!container) return;
    if (!mapInstance) {
      mapInstance = L.map(container).setView([30, 110], 3);
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap', maxZoom: 18
      }).addTo(mapInstance);
    }
    // 清除旧标记
    mapInstance.eachLayer(function(l) {
      if (l instanceof L.Marker || l instanceof L.Polyline) mapInstance.removeLayer(l);
    });
    var qsos = Log.loadQsos();
    var markers = [];
    qsos.forEach(function(q) {
      if (!q.qth) return;
      var loc = Core.parseQth(q.qth);
      if (!loc) return;
      var marker = L.marker([loc.lat, loc.lon]).addTo(mapInstance)
        .bindPopup('<b>' + q.call + '</b><br>' + q.date + ' ' + q.time + '<br>' + q.freq + ' MHz ' + q.mode + '<br>QTH: ' + q.qth + (loc.grid ? ' ('+loc.grid+')' : ''));
      markers.push({ marker: marker, loc: loc });
    });
    document.getElementById('mapCount').textContent = markers.length + ' 个标记';
    if (markers.length > 0) {
      var bounds = L.latLngBounds(markers.map(function(m) { return [m.loc.lat, m.loc.lon]; }));
      mapInstance.fitBounds(bounds, { padding: [30, 30] });
    }
    setTimeout(function() { mapInstance.invalidateSize(); }, 200);
  };

  Module.init = function() { /* 地图在Tab切换时按需初始化 */ };

  global.HAM.Map = Module;

})(window);