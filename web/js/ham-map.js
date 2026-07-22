/**
 * HAM Radio Toolbox - 通联地图 Tab 模块
 * 依赖: HAM.Core, HAM.Log, Leaflet(可选)
 */
(function(global) {
  'use strict';

  var Core = global.HAM && global.HAM.Core;
  var Log = global.HAM && global.HAM.Log;
  if (!Core || !Log) { console.error('HAM.Core or HAM.Log not loaded'); return; }

  var Module = {};
  var mapInstance = null;

  // 高德地图瓦片（国内无需API Key，稳定可用）
  var TILE_URL = 'https://webrd0{s}.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x={x}&y={y}&z={z}';
  var TILE_ATTR = '&copy; 高德地图';
  var TILE_SUBDOMAINS = ['1', '2', '3', '4'];

  /**
   * 渲染地图（Leaflet可用时）或坐标列表（降级方案）
   */
  Module.mapRender = function() {
    var container = document.getElementById('map-container');
    if (!container) return;

    // 检查 Leaflet 是否可用
    if (typeof L === 'undefined') {
      Module.renderFallback(container);
      return;
    }

    // 初始化地图实例
    if (!mapInstance) {
      try {
        mapInstance = L.map(container).setView([35, 105], 4);
        L.tileLayer(TILE_URL, {
          attribution: TILE_ATTR,
          maxZoom: 18,
          subdomains: TILE_SUBDOMAINS
        }).addTo(mapInstance);
      } catch(e) {
        console.error('[HAM Map] Leaflet init failed:', e);
        mapInstance = null;
        Module.renderFallback(container);
        return;
      }
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

  /**
   * 降级方案：Leaflet不可用时显示坐标列表
   */
  Module.renderFallback = function(container) {
    var qsos = Log.loadQsos();
    var html = '<div style="padding:12px;font-size:13px;color:#666;">';
    html += '<p style="margin-bottom:8px;color:#c62828;">⚠️ 地图库加载失败，显示坐标列表：</p>';
    if (qsos.length === 0) {
      html += '<p>暂无通联记录</p>';
    } else {
      html += '<table class="data-table"><tr><th>呼号</th><th>QTH</th><th>纬度</th><th>经度</th><th>网格</th><th>日期</th><th>频率</th><th>模式</th></tr>';
      var count = 0;
      qsos.forEach(function(q) {
        if (!q.qth) return;
        var loc = Core.parseQth(q.qth);
        if (!loc) return;
        count++;
        html += '<tr><td>' + (q.call||'') + '</td><td>' + (q.qth||'') + '</td>';
        html += '<td>' + loc.lat.toFixed(4) + '</td><td>' + loc.lon.toFixed(4) + '</td>';
        html += '<td>' + (loc.grid||'-') + '</td><td>' + (q.date||'') + '</td>';
        html += '<td>' + (q.freq||'') + '</td><td>' + (q.mode||'') + '</td></tr>';
      });
      html += '</table>';
      document.getElementById('mapCount').textContent = count + ' 个坐标';
    }
    html += '</div>';
    container.innerHTML = html;
  };

  Module.init = function() { /* 地图在Tab切换时按需初始化 */ };

  global.HAM.Map = Module;

})(window);