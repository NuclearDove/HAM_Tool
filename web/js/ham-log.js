/**
 * HAM Radio Toolbox - 通联日志 Tab 模块 (ES Module)
 * 包含日志CRUD、导入导出(ADI/Cabrillo/CSV)、备份恢复
 * @module ham-log
 */
'use strict';

import { MODES, CONFIG } from './core.js';
import { EventBus } from './event-bus.js';

/** ADI导入允许的字段白名单（防止原型污染） */
const ADI_FIELDS = [
  'CALL','QSO_DATE','TIME_ON','FREQ','MODE','RST_SENT','RST_RCVD',
  'NAME','QTH','NOTES','BAND','DXCC','CQZ','ITUZ','STATE','CNTY',
  'CONTEST_ID','OPERATOR','STATION_CALLSIGN','MY_QTH','MY_RIG',
  'QSL_RCVD','QSL_SENT','QSL_VIA','LOTW_QSL_RCVD','LOTW_QSL_SENT',
  'EQSL_QSL_RCVD','EQSL_QSL_SENT','GRID','MY_GRIDSQUARE',
  'PROP_MODE','SAT_NAME','SAT_MODE','FREQ_RX','TX_PWR','COMMENT'
];

let editingId = null;

function loadQsos() {
  try { return JSON.parse(localStorage.getItem(CONFIG.LOG_KEY)) || []; }
  catch(e) { return []; }
}

function saveQsos(qsos) {
  localStorage.setItem(CONFIG.LOG_KEY, JSON.stringify(qsos));
}

function logModeRstPreset() {
  const mode = document.getElementById('logMode').value;
  const isCW = mode === 'CW';
  document.getElementById('logRstS').value = isCW ? '599' : '59';
  document.getElementById('logRstR').value = isCW ? '599' : '59';
}

function logAdd() {
  const date = document.getElementById('logDate').value;
  const time = document.getElementById('logTime').value.trim();
  const call = document.getElementById('logCall').value.trim().toUpperCase();
  const freq = document.getElementById('logFreq').value.trim();
  const mode = document.getElementById('logMode').value;
  if (!date || !time || !call || !freq) { alert('请填写日期、时间、呼号和频率（必填项）。'); return; }
  const qso = {
    id: editingId || (Date.now().toString(36) + Math.random().toString(36).substr(2,4)),
    date, time, call, freq: parseFloat(freq) || freq, mode,
    rst_s: document.getElementById('logRstS').value.trim(),
    rst_r: document.getElementById('logRstR').value.trim(),
    name: document.getElementById('logName').value.trim(),
    qth: document.getElementById('logQth').value.trim(),
    note: document.getElementById('logNote').value.trim()
  };
  const qsos = loadQsos();
  if (editingId) {
    const idx = qsos.findIndex(q => q.id === editingId);
    if (idx >= 0) qsos[idx] = qso;
    editingId = null;
    _updateAddBtn();
    EventBus.emit('status', '通联记录已更新: ' + call);
  } else {
    qsos.unshift(qso);
    EventBus.emit('status', '通联记录已添加: ' + call);
  }
  saveQsos(qsos);
  logRefreshTable();
  logClearForm();
  EventBus.emit('log-updated');
}

function logEdit(id) {
  const qsos = loadQsos();
  const qso = qsos.find(q => q.id === id);
  if (!qso) return;
  editingId = id;
  document.getElementById('logDate').value = qso.date;
  document.getElementById('logTime').value = qso.time;
  document.getElementById('logCall').value = qso.call;
  document.getElementById('logFreq').value = qso.freq;
  document.getElementById('logMode').value = qso.mode;
  document.getElementById('logRstS').value = qso.rst_s || '';
  document.getElementById('logRstR').value = qso.rst_r || '';
  document.getElementById('logName').value = qso.name || '';
  document.getElementById('logQth').value = qso.qth || '';
  document.getElementById('logNote').value = qso.note || '';
  _updateAddBtn();
  document.getElementById('logDate').scrollIntoView({ behavior: 'smooth', block: 'center' });
}

function logCancelEdit() {
  editingId = null;
  logClearForm();
  _updateAddBtn();
}

function _updateAddBtn() {
  const btn = document.getElementById('logAddBtn');
  const cancelBtn = document.getElementById('logCancelEditBtn');
  if (!btn) return;
  if (editingId) {
    btn.textContent = '更新记录';
    btn.className = 'btn btn-warning';
    if (cancelBtn) cancelBtn.style.display = 'inline-block';
  } else {
    btn.textContent = '添加记录';
    btn.className = 'btn btn-success';
    if (cancelBtn) cancelBtn.style.display = 'none';
  }
}

function logDelete(id) {
  if (!confirm('确定删除此记录？')) return;
  const qsos = loadQsos().filter(q => q.id !== id);
  saveQsos(qsos);
  logRefreshTable();
  EventBus.emit('status', '记录已删除');
  EventBus.emit('log-updated');
}

function logClearForm() {
  ['logDate','logTime','logCall','logFreq','logRstS','logRstR','logName','logQth','logNote'].forEach(id => {
    document.getElementById(id).value = '';
  });
  const now = new Date();
  document.getElementById('logDate').value = now.toISOString().split('T')[0];
  document.getElementById('logTime').value = now.getUTCHours().toString().padStart(2,'0') + now.getUTCMinutes().toString().padStart(2,'0');
}

function logRefreshTable() {
  const search = (document.getElementById('logSearch').value || '').toLowerCase();
  let qsos = loadQsos();
  if (search) qsos = qsos.filter(q =>
    (q.call+q.mode+q.date+q.name+q.qth+q.note).toLowerCase().includes(search)
  );
  document.getElementById('logCount').textContent = '(' + qsos.length + ' 条)';
  const tbody = document.querySelector('#logTable tbody');
  if (!tbody) return;
  tbody.innerHTML = qsos.map(q => {
    const isEditing = editingId === q.id;
    const rowStyle = isEditing ? ' style="background:#fff8e1"' : '';
    return '<tr' + rowStyle + '>' +
      '<td>' + q.date + '</td><td>' + q.time + '</td><td style="font-weight:600">' + q.call + '</td>' +
      '<td>' + q.freq + '</td><td>' + q.mode + '</td><td>' + (q.rst_s||'') + '</td><td>' + (q.rst_r||'') + '</td>' +
      '<td>' + (q.name||'') + '</td><td>' + (q.qth||'') + '</td><td>' + (q.note||'') + '</td>' +
      '<td style="white-space:nowrap">' +
        '<button class="btn btn-primary" style="padding:2px 8px;font-size:11px;margin-right:4px" onclick="logEdit(\'' + q.id + '\')">编辑</button>' +
        '<button class="btn btn-danger" style="padding:2px 8px;font-size:11px" onclick="logDelete(\'' + q.id + '\')">删除</button>' +
      '</td></tr>';
  }).join('');
}

function downloadFile(name, content, type) {
  const blob = new Blob([content], { type });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = name;
  a.click();
  URL.revokeObjectURL(a.href);
}

function logExportAdi() {
  const qsos = loadQsos();
  if (!qsos.length) { alert('无记录可导出。'); return; }
  let adi = '<ADIF_VER:5>3.1.0<EOH>\n';
  qsos.forEach(q => {
    adi += '<CALL:' + q.call.length + '>' + q.call +
      '<QSO_DATE:' + q.date.replace(/-/g,'').length + '>' + q.date.replace(/-/g,'') +
      '<TIME_ON:' + q.time.length + '>' + q.time +
      '<FREQ:' + String(q.freq).length + '>' + q.freq +
      '<MODE:' + q.mode.length + '>' + q.mode;
    if (q.rst_s) adi += '<RST_SENT:' + q.rst_s.length + '>' + q.rst_s;
    if (q.rst_r) adi += '<RST_RCVD:' + q.rst_r.length + '>' + q.rst_r;
    if (q.name) adi += '<NAME:' + q.name.length + '>' + q.name;
    if (q.qth) adi += '<QTH:' + q.qth.length + '>' + q.qth;
    if (q.note) adi += '<NOTES:' + q.note.length + '>' + q.note;
    adi += '<EOR>\n';
  });
  downloadFile(qsos[0].call + '_' + new Date().toISOString().split('T')[0] + '.adi', adi, 'text/plain');
  EventBus.emit('status', 'ADI导出完成');
}

function logExportCabrillo() {
  const qsos = loadQsos();
  if (!qsos.length) { alert('无记录可导出。'); return; }
  let cab = 'START-OF-LOG: 3.0\nCREATED-BY: HAM Radio Toolbox Web\n';
  cab += 'CONTEST: \nCALLSIGN: \n';
  qsos.forEach(q => {
    cab += 'QSO: ' + q.freq.toString().padStart(8) + ' ' + q.mode.padEnd(6) + ' ' +
      q.date.replace(/-/g,'') + ' ' + q.time.padStart(4,'0') + ' ' +
      q.call.padEnd(13) + ' ' + (q.rst_s||'59') + ' ' +
      q.call.padEnd(13) + ' ' + (q.rst_r||'59') + '\n';
  });
  cab += 'END-OF-LOG:\n';
  downloadFile('cabrillo_' + new Date().toISOString().split('T')[0] + '.log', cab, 'text/plain');
  EventBus.emit('status', 'Cabrillo导出完成');
}

function logExportCsv() {
  const qsos = loadQsos();
  if (!qsos.length) { alert('无记录可导出。'); return; }
  let csv = '\uFEFF日期,时间,呼号,频率,模式,RST发送,RST接收,姓名,QTH,备注\n';
  qsos.forEach(q => {
    csv += [q.date,q.time,q.call,q.freq,q.mode,q.rst_s,q.rst_r,q.name,q.qth,q.note].map(v =>
      '"' + (v||'').replace(/"/g,'""') + '"'
    ).join(',') + '\n';
  });
  downloadFile('qso_' + new Date().toISOString().split('T')[0] + '.csv', csv, 'text/csv');
  EventBus.emit('status', 'CSV导出完成');
}

function logImportAdi() { document.getElementById('adiFileInput').click(); }

/**
 * ADI文件导入（含白名单过滤防止原型污染）
 */
function logImportAdiFile(e) {
  const file = e.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = function(ev) {
    const text = ev.target.result;
    const qsos = loadQsos();
    let count = 0;
    const lines = text.split(/<eor>/i);
    for (let li = 0; li < lines.length; li++) {
      const current = {};
      const re = /<(\w+):(\d+)(?::\w)?>([^<]*)/gi;
      let match;
      while ((match = re.exec(lines[li])) !== null) {
        const fieldName = match[1].toUpperCase();
        // 白名单过滤：仅允许已知ADI字段
        if (ADI_FIELDS.includes(fieldName)) {
          current[fieldName] = match[3].trim();
        }
      }
      if (current.CALL) {
        qsos.unshift({
          id: Date.now().toString(36) + Math.random().toString(36).substr(2,4) + count,
          date: (current.QSO_DATE || '').replace(/(\d{4})(\d{2})(\d{2})/, '$1-$2-$3'),
          time: current.TIME_ON || '',
          call: current.CALL || '',
          freq: current.FREQ || '',
          mode: current.MODE || '',
          rst_s: current.RST_SENT || '',
          rst_r: current.RST_RCVD || '',
          name: current.NAME || '',
          qth: current.QTH || '',
          note: current.NOTES || ''
        });
        count++;
      }
    }
    saveQsos(qsos);
    logRefreshTable();
    EventBus.emit('status', 'ADI导入完成，新增 ' + count + ' 条记录');
    EventBus.emit('log-updated');
    e.target.value = '';
  };
  reader.readAsText(file);
}

function logBackup() {
  const qsos = loadQsos();
  if (!qsos.length) { alert('无记录可备份。'); return; }
  downloadFile('qso_backup_' + new Date().toISOString().split('T')[0] + '.json', JSON.stringify(qsos, null, 2), 'application/json');
  EventBus.emit('status', '备份完成');
}

function logRestore() { document.getElementById('restoreFileInput').click(); }

function logRestoreFile(e) {
  const file = e.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = function(ev) {
    try {
      const data = JSON.parse(ev.target.result);
      if (!Array.isArray(data)) throw new Error('格式错误');
      saveQsos(data);
      logRefreshTable();
      EventBus.emit('status', '恢复完成，共 ' + data.length + ' 条记录');
      EventBus.emit('log-updated');
    } catch(err) { alert('恢复失败: ' + err.message); }
    e.target.value = '';
  };
  reader.readAsText(file);
}

function init() {
  const modeSelect = document.getElementById('logMode');
  if (modeSelect) {
    MODES.forEach(m => {
      const o = document.createElement('option');
      o.value = m; o.textContent = m;
      modeSelect.appendChild(o);
    });
  }
  logClearForm();
  logRefreshTable();
}

export {
  logModeRstPreset, logAdd, logClearForm, logRefreshTable,
  logEdit, logCancelEdit, logDelete,
  logExportAdi, logExportCabrillo, logExportCsv,
  logImportAdi, logImportAdiFile,
  logBackup, logRestore, logRestoreFile,
  loadQsos, init
};