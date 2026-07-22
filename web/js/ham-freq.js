/**
 * HAM Radio Toolbox - 频率/频段 Tab 模块
 * 依赖: HAM.Core
 */
(function(global) {
  'use strict';

  var Core = global.HAM && global.HAM.Core;
  if (!Core) { console.error('HAM.Core not loaded'); return; }

  var Module = {};

  Module.onSearchModeChange = function() {
    var mode = document.getElementById('freqSearchMode').value;
    document.getElementById('freqInput2').style.display = mode === 'range' ? '' : 'none';
    document.getElementById('freqSep').style.display = mode === 'range' ? '' : 'none';
  };

  Module.freqQuery = function() {
    var mode = document.getElementById('freqSearchMode').value;
    var unit = document.getElementById('freqUnit').value;
    var f1 = Core.freqToMHz(document.getElementById('freqInput').value, unit);
    if (isNaN(f1)) { document.getElementById('freqResult').textContent = '请输入有效频率值。'; return; }
    var lines = [];
    if (mode === 'freq') {
      var band = Core.freqToBand(f1);
      var cat = Core.getSpectrumCat(f1);
      var wl = Core.wavelength(f1);
      lines.push('频率: ' + f1.toFixed(4) + ' MHz');
      lines.push('波长: ' + (wl*100).toFixed(2) + ' cm / ' + wl.toFixed(4) + ' m');
      lines.push('频段: ' + (cat ? (Core.CAT_CN[cat]||cat) : '未知'));
      if (band) {
        lines.push('\n✅ 属于业余频段: ' + band.name);
        lines.push('  范围: ' + band.f_low + ' - ' + band.f_high + ' MHz');
        lines.push('  类型: ' + (Core.CAT_CN[band.cat]||band.cat));
        lines.push('  执照: ' + band.license);
        lines.push('  业务: ' + band.svc);
        lines.push('\n天线计算:');
        var dip = Core.dipoleLength(f1);
        lines.push('  半波偶极: ' + (dip.halfWave*100).toFixed(1) + ' cm (每臂 ' + (dip.eachLeg*100).toFixed(1) + ' cm)');
        lines.push('  四分之一波长: ' + (Core.quarterWaveLength(f1)*100).toFixed(1) + ' cm');
      } else {
        lines.push('\n❌ 不属于业余频段');
      }
    } else {
      var f2 = Core.freqToMHz(document.getElementById('freqInput2').value, unit);
      if (isNaN(f2)) { document.getElementById('freqResult').textContent = '请输入有效上限频率。'; return; }
      lines.push('搜索范围: ' + f1.toFixed(4) + ' - ' + f2.toFixed(4) + ' MHz\n');
      var found = Core.BANDS.filter(function(b) { return b.f_low <= f2 && b.f_high >= f1; });
      if (found.length === 0) {
        lines.push('该范围内无业余频段。');
      } else {
        found.forEach(function(b) {
          lines.push(b.name + ': ' + b.f_low + ' - ' + b.f_high + ' MHz (' + (Core.CAT_CN[b.cat]||b.cat) + ') ' + b.svc + ' ' + b.license);
        });
      }
    }
    document.getElementById('freqResult').textContent = lines.join('\n');
    if (global.HAM.EventBus) global.HAM.EventBus.emit('status', '频率查询完成');
  };

  Module.freqClear = function() {
    document.getElementById('freqInput').value = '';
    document.getElementById('freqInput2').value = '';
    document.getElementById('freqResult').textContent = '输入频率或频率区间，查询所属业余频段信息。';
  };

  Module.initBandTable = function() {
    var tbody = document.querySelector('#bandTable tbody');
    if (!tbody) return;
    tbody.innerHTML = Core.BANDS.map(function(b) {
      return '<tr><td>' + b.name + '</td><td>' + (Core.CAT_CN[b.cat]||b.cat) + '</td><td>' + b.f_low + '</td><td>' + b.f_high + '</td><td>' + b.svc + '</td></tr>';
    }).join('');
  };

  Module.initModesRef = function() {
    var div = document.getElementById('modesRef');
    if (!div) return;
    div.innerHTML = Core.MODES_REF.map(function(cat) {
      return '<div class="mode-ref"><h4>' + cat.cat + '</h4>' + cat.modes.map(function(m) {
        return '<div class="mode-item"><span class="abbr">' + m.a + '</span><span class="name">' + m.n + '</span><span class="desc">' + m.d + '</span></div>';
      }).join('') + '</div>';
    }).join('');
  };

  Module.init = function() {
    Module.initBandTable();
    Module.initModesRef();
  };

  // 暴露到全局
  global.HAM.Freq = Module;

})(window);