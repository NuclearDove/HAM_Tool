/**
 * HAM Radio Toolbox - 网格坐标 Tab 模块
 * 依赖: HAM.Core
 */
(function(global) {
  'use strict';

  var Core = global.HAM && global.HAM.Core;
  if (!Core) { console.error('HAM.Core not loaded'); return; }

  var Module = {};

  Module.llToGrid = function() {
    var lat = parseFloat(document.getElementById('latIn').value);
    var lon = parseFloat(document.getElementById('lonIn').value);
    if (isNaN(lat) || isNaN(lon) || lat < -90 || lat > 90 || lon < -180 || lon > 180) {
      document.getElementById('gridResult').textContent = '请输入有效经纬度 (纬度 -90~90, 经度 -180~180)。'; return;
    }
    var grid = Core.latLonToGrid(lat, lon);
    var lines = ['经纬度: ' + lat + '°, ' + lon + '°', '网格坐标: ' + grid, '4位: ' + grid.substring(0,4), grid.length >= 6 ? '6位: ' + grid.substring(0,6) : ''];
    document.getElementById('gridResult').textContent = lines.filter(Boolean).join('\n');
    if (global.HAM.EventBus) global.HAM.EventBus.emit('status', '经纬度→网格转换完成');
  };

  Module.gridToLl = function() {
    var grid = document.getElementById('gridIn').value.trim().toUpperCase();
    var c = Core.gridToLatLon(grid);
    if (!c) { document.getElementById('gridResult').textContent = '无效网格格式 (如 OM89 或 OM89MM)。'; return; }
    var lines = ['网格: ' + grid, '纬度: ' + c.lat.toFixed(6) + '°', '经度: ' + c.lon.toFixed(6) + '°', '', 'Google Maps: https://maps.google.com/?q=' + c.lat + ',' + c.lon];
    document.getElementById('gridResult').textContent = lines.join('\n');
    if (global.HAM.EventBus) global.HAM.EventBus.emit('status', '网格→经纬度转换完成');
  };

  Module.gridDistance = function() {
    var g1 = document.getElementById('distG1').value.trim().toUpperCase();
    var g2 = document.getElementById('distG2').value.trim().toUpperCase();
    var c1 = Core.gridToLatLon(g1), c2 = Core.gridToLatLon(g2);
    if (!c1 || !c2) { document.getElementById('gridResult').textContent = '无效网格格式。'; return; }
    var d = Core.distanceBearing(c1.lat, c1.lon, c2.lat, c2.lon);
    var lines = ['网格1: ' + g1 + ' → ' + c1.lat.toFixed(4) + '°, ' + c1.lon.toFixed(4) + '°', '网格2: ' + g2 + ' → ' + c2.lat.toFixed(4) + '°, ' + c2.lon.toFixed(4) + '°', '', '距离: ' + d.distance.toFixed(1) + ' km', '方位角: ' + d.bearing.toFixed(1) + '°'];
    document.getElementById('gridResult').textContent = lines.join('\n');
    if (global.HAM.EventBus) global.HAM.EventBus.emit('status', '网格距离计算完成');
  };

  Module.init = function() { /* 无需特殊初始化 */ };

  global.HAM.Grid = Module;

})(window);