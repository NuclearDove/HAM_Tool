/**
 * HAM Radio Toolbox - 网格坐标 Tab 模块 (ES Module)
 * @module ham-grid
 */
'use strict';

import { gridToLatLon, latLonToGrid, distanceBearing } from './core.js';
import { EventBus } from './event-bus.js';

function llToGrid() {
  const lat = parseFloat(document.getElementById('latIn').value);
  const lon = parseFloat(document.getElementById('lonIn').value);
  if (isNaN(lat) || isNaN(lon) || lat < -90 || lat > 90 || lon < -180 || lon > 180) {
    document.getElementById('gridResult').textContent = '请输入有效经纬度 (纬度 -90~90, 经度 -180~180)。'; return;
  }
  const grid = latLonToGrid(lat, lon);
  const lines = ['经纬度: ' + lat + '°, ' + lon + '°', '网格坐标: ' + grid, '4位: ' + grid.substring(0,4), grid.length >= 6 ? '6位: ' + grid.substring(0,6) : ''];
  document.getElementById('gridResult').textContent = lines.filter(Boolean).join('\n');
  EventBus.emit('status', '经纬度→网格转换完成');
}

function gridToLl() {
  const grid = document.getElementById('gridIn').value.trim().toUpperCase();
  const c = gridToLatLon(grid);
  if (!c) { document.getElementById('gridResult').textContent = '无效网格格式 (如 OM89 或 OM89MM)。'; return; }
  const lines = ['网格: ' + grid, '纬度: ' + c.lat.toFixed(6) + '°', '经度: ' + c.lon.toFixed(6) + '°', '', 'Google Maps: https://maps.google.com/?q=' + c.lat + ',' + c.lon];
  document.getElementById('gridResult').textContent = lines.join('\n');
  EventBus.emit('status', '网格→经纬度转换完成');
}

function gridDistance() {
  const g1 = document.getElementById('distG1').value.trim().toUpperCase();
  const g2 = document.getElementById('distG2').value.trim().toUpperCase();
  const c1 = gridToLatLon(g1), c2 = gridToLatLon(g2);
  if (!c1 || !c2) { document.getElementById('gridResult').textContent = '无效网格格式。'; return; }
  const d = distanceBearing(c1.lat, c1.lon, c2.lat, c2.lon);
  const lines = ['网格1: ' + g1 + ' → ' + c1.lat.toFixed(4) + '°, ' + c1.lon.toFixed(4) + '°', '网格2: ' + g2 + ' → ' + c2.lat.toFixed(4) + '°, ' + c2.lon.toFixed(4) + '°', '', '距离: ' + d.distance.toFixed(1) + ' km', '方位角: ' + d.bearing.toFixed(1) + '°'];
  document.getElementById('gridResult').textContent = lines.join('\n');
  EventBus.emit('status', '网格距离计算完成');
}

function init() { /* 无需特殊初始化 */ }

export { llToGrid, gridToLl, gridDistance, init };