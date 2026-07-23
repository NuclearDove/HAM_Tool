/**
 * HAM Radio Toolbox - 通联地图 Tab 模块 (ES Module)
 * 依赖: Core, Log, Leaflet(可选，CDN延迟加载)
 * @module ham-map
 */
'use strict';

import { CONFIG, parseQth } from './core.js';
import { EventBus } from './event-bus.js';

let mapInstance = null;

/**
 * 渲染地图（Leaflet可用时）或坐标列表（降级方案）
 */
function mapRender() {
  const container = document.getElementById('map-container');
  if (!container) return;

  // 检查 Leaflet 是否可用
  if (typeof L === 'undefined') {
    renderFallback(container);
    return;
  }

  // 初始化地图实例
  if (!mapInstance) {
    try {
      mapInstance = L.map(container).setView([35, 105], 4);
      L.tileLayer(CONFIG.MAP_TILE_URL, {
        attribution: '&copy; 高德地图',
        maxZoom: 18,
        subdomains: CONFIG.MAP_SUBDOMAINS
      }).addTo(mapInstance);
    } catch(e) {
      console.error('[HAM Map] Leaflet init failed:', e);
      mapInstance = null;
      renderFallback(container);
      return;
    }
  }

  // 清除旧标记
  mapInstance.eachLayer(l => {
    if (l instanceof L.Marker || l instanceof L.Polyline) mapInstance.removeLayer(l);
  });

  // 动态导入Log模块获取数据
  import('./ham-log.js').then(({ loadQsos }) => {
    const qsos = loadQsos();
    const markers = [];
    qsos.forEach(q => {
      if (!q.qth) return;
      const loc = parseQth(q.qth);
      if (!loc) return;
      const marker = L.marker([loc.lat, loc.lon]).addTo(mapInstance)
        .bindPopup('<b>' + q.call + '</b><br>' + q.date + ' ' + q.time + '<br>' + q.freq + ' MHz ' + q.mode + '<br>QTH: ' + q.qth + (loc.grid ? ' ('+loc.grid+')' : ''));
      markers.push({ marker, loc });
    });

    document.getElementById('mapCount').textContent = markers.length + ' 个标记';
    if (markers.length > 0) {
      const bounds = L.latLngBounds(markers.map(m => [m.loc.lat, m.loc.lon]));
      mapInstance.fitBounds(bounds, { padding: [30, 30] });
    }
    setTimeout(() => mapInstance.invalidateSize(), 200);
  });
}

/**
 * 降级方案：Leaflet不可用时显示坐标列表
 */
function renderFallback(container) {
  import('./ham-log.js').then(({ loadQsos }) => {
    const qsos = loadQsos();
    let html = '<div style="padding:12px;font-size:13px;color:#666;">';
    html += '<p style="margin-bottom:8px;color:#c62828;">⚠️ 地图库加载失败，显示坐标列表：</p>';
    if (qsos.length === 0) {
      html += '<p>暂无通联记录</p>';
    } else {
      html += '<table class="data-table"><tr><th>呼号</th><th>QTH</th><th>纬度</th><th>经度</th><th>网格</th><th>日期</th><th>频率</th><th>模式</th></tr>';
      let count = 0;
      qsos.forEach(q => {
        if (!q.qth) return;
        const loc = parseQth(q.qth);
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
  });
}

function init() { /* 地图在Tab切换时按需初始化 */ }

export { mapRender, init };