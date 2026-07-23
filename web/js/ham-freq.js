/**
 * HAM Radio Toolbox - 频率/频段 Tab 模块 (ES Module)
 * @module ham-freq
 */
'use strict';

import { BANDS, CAT_CN, MODES_REF, freqToMHz, freqToBand, getSpectrumCat, wavelength, dipoleLength, quarterWaveLength, renderTable } from './core.js';
import { EventBus } from './event-bus.js';

/**
 * 搜索模式切换
 */
function onSearchModeChange() {
  const mode = document.getElementById('freqSearchMode').value;
  document.getElementById('freqInput2').style.display = mode === 'range' ? '' : 'none';
  document.getElementById('freqSep').style.display = mode === 'range' ? '' : 'none';
}

/**
 * 频率查询
 */
function freqQuery() {
  const mode = document.getElementById('freqSearchMode').value;
  const unit = document.getElementById('freqUnit').value;
  const f1 = freqToMHz(document.getElementById('freqInput').value, unit);
  if (isNaN(f1)) { document.getElementById('freqResult').textContent = '请输入有效频率值。'; return; }
  const lines = [];
  if (mode === 'freq') {
    const band = freqToBand(f1);
    const cat = getSpectrumCat(f1);
    const wl = wavelength(f1);
    lines.push('频率: ' + f1.toFixed(4) + ' MHz');
    lines.push('波长: ' + (wl*100).toFixed(2) + ' cm / ' + wl.toFixed(4) + ' m');
    lines.push('频段: ' + (cat ? (CAT_CN[cat]||cat) : '未知'));
    if (band) {
      lines.push('\n✅ 属于业余频段: ' + band.name);
      lines.push('  范围: ' + band.f_low + ' - ' + band.f_high + ' MHz');
      lines.push('  类型: ' + (CAT_CN[band.cat]||band.cat));
      lines.push('  执照: ' + band.license);
      lines.push('  业务: ' + band.svc);
      if (band.note) lines.push('  备注: ' + band.note);
      lines.push('\n天线计算:');
      const dip = dipoleLength(f1);
      lines.push('  半波偶极: ' + (dip.halfWave*100).toFixed(1) + ' cm (每臂 ' + (dip.eachLeg*100).toFixed(1) + ' cm)');
      lines.push('  四分之一波长: ' + (quarterWaveLength(f1)*100).toFixed(1) + ' cm');
    } else {
      lines.push('\n❌ 不属于业余频段');
    }
  } else {
    const f2 = freqToMHz(document.getElementById('freqInput2').value, unit);
    if (isNaN(f2)) { document.getElementById('freqResult').textContent = '请输入有效上限频率。'; return; }
    lines.push('搜索范围: ' + f1.toFixed(4) + ' - ' + f2.toFixed(4) + ' MHz\n');
    const found = BANDS.filter(b => b.f_low <= f2 && b.f_high >= f1);
    if (found.length === 0) {
      lines.push('该范围内无业余频段。');
    } else {
      found.forEach(b => {
        lines.push(b.name + ': ' + b.f_low + ' - ' + b.f_high + ' MHz (' + (CAT_CN[b.cat]||b.cat) + ') ' + b.svc + ' ' + b.license);
      });
    }
  }
  document.getElementById('freqResult').textContent = lines.join('\n');
  EventBus.emit('status', '频率查询完成');
}

/**
 * 清空频率查询表单
 */
function freqClear() {
  document.getElementById('freqInput').value = '';
  document.getElementById('freqInput2').value = '';
  document.getElementById('freqResult').textContent = '输入频率或频率区间，查询所属业余频段信息。';
}

/**
 * 初始化频段表
 */
function initBandTable() {
  renderTable('bandTable', BANDS, b =>
    '<tr><td>' + b.name + '</td><td>' + (CAT_CN[b.cat]||b.cat) + '</td><td>' + b.f_low + '</td><td>' + b.f_high + '</td><td>' + b.svc + '</td></tr>'
  );
}

/**
 * 初始化通信模式参考
 */
function initModesRef() {
  const div = document.getElementById('modesRef');
  if (!div) return;
  div.innerHTML = MODES_REF.map(cat =>
    '<div class="mode-ref"><h4>' + cat.cat + '</h4>' + cat.modes.map(m =>
      '<div class="mode-item"><span class="abbr">' + m.a + '</span><span class="name">' + m.n + '</span><span class="desc">' + m.d + '</span></div>'
    ).join('') + '</div>'
  ).join('');
}

/**
 * 模块初始化
 */
function init() {
  initBandTable();
  initModesRef();
}

export { onSearchModeChange, freqQuery, freqClear, init };