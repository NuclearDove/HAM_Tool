/**
 * HAM Radio Toolbox - 射频工具 Tab 模块
 * 包含天线计算、功率转换、SWR计算、馈线损耗
 * 依赖: HAM.Core
 */
(function(global) {
  'use strict';

  var Core = global.HAM && global.HAM.Core;
  if (!Core) { console.error('HAM.Core not loaded'); return; }

  var Module = {};

  Module.antennaCalc = function() {
    var f = parseFloat(document.getElementById('antFreq').value);
    if (isNaN(f) || f <= 0) { document.getElementById('antResult').textContent = '请输入有效频率。'; return; }
    var wl = Core.wavelength(f);
    var dip = Core.dipoleLength(f);
    var qw = Core.quarterWaveLength(f);
    var band = Core.freqToBand(f);
    var lines = [];
    lines.push('频率: ' + f + ' MHz');
    lines.push('波长: ' + (wl*100).toFixed(2) + ' cm (' + wl.toFixed(4) + ' m)');
    if (band) lines.push('业余频段: ' + band.name + ' (' + band.f_low + '-' + band.f_high + ' MHz)');
    lines.push('\n--- 半波偶极天线 ---');
    lines.push('总长: ' + (dip.halfWave*100).toFixed(1) + ' cm (' + dip.halfWave.toFixed(4) + ' m)');
    lines.push('每臂: ' + (dip.eachLeg*100).toFixed(1) + ' cm (' + dip.eachLeg.toFixed(4) + ' m)');
    lines.push('(含0.95缩短因子)');
    lines.push('\n--- 四分之一波长垂直/天线 ---');
    lines.push('长度: ' + (qw*100).toFixed(1) + ' cm (' + qw.toFixed(4) + ' m)');
    lines.push('(含0.95缩短因子)');
    document.getElementById('antResult').textContent = lines.join('\n');
    if (global.HAM.EventBus) global.HAM.EventBus.emit('status', '天线计算完成');
  };

  Module.powerConvert = function() {
    var val = parseFloat(document.getElementById('powVal').value);
    var unit = document.querySelector('input[name="powUnit"]:checked').value;
    if (isNaN(val)) { document.getElementById('powResult').textContent = '请输入有效数值。'; return; }
    var lines = [];
    if (unit === 'W') {
      if (val <= 0) { document.getElementById('powResult').textContent = '功率必须大于0。'; return; }
      lines.push(val + ' W = ' + Core.wattsToDbm(val).toFixed(2) + ' dBm');
      lines.push(val + ' W = ' + Core.wattsToDbw(val).toFixed(2) + ' dBW');
    } else if (unit === 'dBm') {
      var w = Core.dbmToWatts(val);
      lines.push(val + ' dBm = ' + (w < 0.001 ? w.toExponential(4) : w < 1 ? w.toFixed(6) : w.toFixed(4)) + ' W');
      lines.push(val + ' dBm = ' + Core.dbmToDbw(val).toFixed(2) + ' dBW');
    } else {
      var w2 = Core.dbwToWatts(val);
      lines.push(val + ' dBW = ' + (w2 < 0.001 ? w2.toExponential(4) : w2 < 1 ? w2.toFixed(6) : w2.toFixed(4)) + ' W');
      lines.push(val + ' dBW = ' + (val + 30).toFixed(2) + ' dBm');
    }
    document.getElementById('powResult').textContent = lines.join('\n');
    if (global.HAM.EventBus) global.HAM.EventBus.emit('status', '功率转换完成');
  };

  Module.swrFromPower = function() {
    var fw = parseFloat(document.getElementById('swrFw').value);
    var rw = parseFloat(document.getElementById('swrRw').value);
    if (isNaN(fw) || isNaN(rw) || fw <= 0) { document.getElementById('swrResult').textContent = '请输入有效功率值。'; return; }
    var swr = Core.swrFromPower(fw, rw);
    if (!swr) { document.getElementById('swrResult').textContent = '反射功率必须 ≥ 0 且 < 正向功率。'; return; }
    var refl = Math.sqrt(rw / fw);
    var retLoss = -20 * Math.log10(refl);
    var lines = ['正向功率: ' + fw + ' W', '反射功率: ' + rw + ' W', '', 'SWR: ' + swr.toFixed(3) + ' : 1', '反射系数: ' + (refl*100).toFixed(2) + '%', '回波损耗: ' + (isFinite(retLoss) ? retLoss.toFixed(2) : '∞') + ' dB'];
    if (swr <= 1.5) lines.push('\n✅ SWR良好 (≤1.5)');
    else if (swr <= 3) lines.push('\n⚠️ SWR偏高 (1.5-3.0)，建议调整天线');
    else lines.push('\n❌ SWR过高 (>3.0)，可能损坏设备！');
    document.getElementById('swrResult').textContent = lines.join('\n');
  };

  Module.swrToReflect = function() {
    var swr = parseFloat(document.getElementById('swrVal').value);
    var fw = parseFloat(document.getElementById('swrFw2').value);
    if (isNaN(swr) || isNaN(fw) || swr < 1 || fw <= 0) { document.getElementById('swrResult').textContent = 'SWR必须≥1，正向功率必须>0。'; return; }
    var rw = Core.swrToReflectPower(swr, fw);
    var refl = (swr - 1) / (swr + 1);
    var retLoss = -20 * Math.log10(refl);
    var lines = ['SWR: ' + swr.toFixed(3) + ' : 1', '正向功率: ' + fw + ' W', '', '反射功率: ' + rw.toFixed(4) + ' W', '反射系数: ' + (refl*100).toFixed(2) + '%', '回波损耗: ' + (isFinite(retLoss) ? retLoss.toFixed(2) : '∞') + ' dB', '效率: ' + ((1-refl*refl)*100).toFixed(2) + '%'];
    document.getElementById('swrResult').textContent = lines.join('\n');
  };

  Module.initCoaxSelect = function() {
    var sel = document.getElementById('coaxType');
    if (!sel) return;
    Object.keys(Core.COAX_TYPES).forEach(function(k) {
      var o = document.createElement('option');
      o.value = k; o.textContent = k;
      sel.appendChild(o);
    });
    var tbody = document.querySelector('#coaxRefTable tbody');
    if (!tbody) return;
    tbody.innerHTML = Object.entries(Core.COAX_TYPES).map(function(entry) {
      var name = entry[0], d = entry[1];
      return '<tr><td>' + name + '</td><td>' + (d[100]||'-') + '</td><td>' + (d[400]||'-') + '</td><td>' + (d[1000]||'-') + '</td></tr>';
    }).join('');
  };

  Module.coaxCalc = function() {
    var type = document.getElementById('coaxType').value;
    var freq = parseFloat(document.getElementById('coaxFreq').value);
    var len = parseFloat(document.getElementById('coaxLen').value);
    if (isNaN(freq) || isNaN(len) || freq <= 0 || len <= 0) { document.getElementById('coaxResult').textContent = '请输入有效频率和长度。'; return; }
    var atten = Core.coaxAttenuation(type, freq, len);
    if (atten === null) { document.getElementById('coaxResult').textContent = '无法计算。'; return; }
    var pLoss = Math.pow(10, atten / 10);
    var lines = ['馈线: ' + type, '频率: ' + freq + ' MHz', '长度: ' + len + ' m', '', '衰减: ' + atten.toFixed(2) + ' dB', '功率损失: ' + ((1-1/pLoss)*100).toFixed(2) + '%', '剩余功率: ' + (1/pLoss*100).toFixed(2) + '%'];
    document.getElementById('coaxResult').textContent = lines.join('\n');
    if (global.HAM.EventBus) global.HAM.EventBus.emit('status', '馈线损耗计算完成');
  };

  Module.init = function() {
    Module.initCoaxSelect();
  };

  global.HAM.RF = Module;

})(window);