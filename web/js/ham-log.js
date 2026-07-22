/**
 * HAM Radio Toolbox - 通联日志 Tab 模块
 * 包含日志CRUD、导入导出(ADI/Cabrillo/CSV)、备份恢复
 * 依赖: HAM.Core
 */
(function(global) {
  'use strict';

  var Core = global.HAM && global.HAM.Core;
  if (!Core) { console.error('HAM.Core not loaded'); return; }

  var Module = {};
  var LOG_KEY = 'ham_qso_log';

  Module.loadQsos = function() {
    try { return JSON.parse(localStorage.getItem(LOG_KEY)) || []; }
    catch(e) { return []; }
  };

  Module.saveQsos = function(qsos) {
    localStorage.setItem(LOG_KEY, JSON.stringify(qsos));
  };

  Module.logModeRstPreset = function() {
    var mode = document.getElementById('logMode').value;
    var isCW = mode === 'CW';
    document.getElementById('logRstS').value = isCW ? '599' : '59';
    document.getElementById('logRstR').value = isCW ? '599' : '59';
  };

  Module.logAdd = function() {
    var date = document.getElementById('logDate').value;
    var time = document.getElementById('logTime').value.trim();
    var call = document.getElementById('logCall').value.trim().toUpperCase();
    var freq = document.getElementById('logFreq').value.trim();
    var mode = document.getElementById('logMode').value;
    if (!date || !time || !call || !freq) { alert('请填写日期、时间、呼号和频率（必填项）。'); return; }
    var qso = {
      id: Date.now().toString(36) + Math.random().toString(36).substr(2,4),
      date: date, time: time, call: call, freq: parseFloat(freq) || freq, mode: mode,
      rst_s: document.getElementById('logRstS').value.trim(),
      rst_r: document.getElementById('logRstR').value.trim(),
      name: document.getElementById('logName').value.trim(),
      qth: document.getElementById('logQth').value.trim(),
      note: document.getElementById('logNote').value.trim()
    };
    var qsos = Module.loadQsos();
    qsos.unshift(qso);
    Module.saveQsos(qsos);
    Module.logRefreshTable();
    Module.logClearForm();
    if (global.HAM.EventBus) global.HAM.EventBus.emit('status', '通联记录已添加: ' + call);
    if (global.HAM.EventBus) global.HAM.EventBus.emit('log-updated');
  };

  Module.logDelete = function(id) {
    if (!confirm('确定删除此记录？')) return;
    var qsos = Module.loadQsos().filter(function(q) { return q.id !== id; });
    Module.saveQsos(qsos);
    Module.logRefreshTable();
    if (global.HAM.EventBus) global.HAM.EventBus.emit('status', '记录已删除');
    if (global.HAM.EventBus) global.HAM.EventBus.emit('log-updated');
  };

  Module.logClearForm = function() {
    ['logDate','logTime','logCall','logFreq','logRstS','logRstR','logName','logQth','logNote'].forEach(function(id) {
      document.getElementById(id).value = '';
    });
    var now = new Date();
    document.getElementById('logDate').value = now.toISOString().split('T')[0];
    document.getElementById('logTime').value = now.getUTCHours().toString().padStart(2,'0') + now.getUTCMinutes().toString().padStart(2,'0');
  };

  Module.logRefreshTable = function() {
    var search = (document.getElementById('logSearch').value || '').toLowerCase();
    var qsos = Module.loadQsos();
    if (search) qsos = qsos.filter(function(q) {
      return (q.call+q.mode+q.date+q.name+q.qth+q.note).toLowerCase().includes(search);
    });
    document.getElementById('logCount').textContent = '(' + qsos.length + ' 条)';
    var tbody = document.querySelector('#logTable tbody');
    if (!tbody) return;
    tbody.innerHTML = qsos.map(function(q) {
      return '<tr>' +
        '<td>' + q.date + '</td><td>' + q.time + '</td><td style="font-weight:600">' + q.call + '</td>' +
        '<td>' + q.freq + '</td><td>' + q.mode + '</td><td>' + (q.rst_s||'') + '</td><td>' + (q.rst_r||'') + '</td>' +
        '<td>' + (q.name||'') + '</td><td>' + (q.qth||'') + '</td><td>' + (q.note||'') + '</td>' +
        '<td><button class="btn btn-danger" style="padding:2px 8px;font-size:11px" onclick="HAM.Log.logDelete(\'' + q.id + '\')">删除</button></td>' +
      '</tr>';
    }).join('');
  };

  Module.downloadFile = function(name, content, type) {
    var blob = new Blob([content], { type: type });
    var a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = name;
    a.click();
    URL.revokeObjectURL(a.href);
  };

  Module.logExportAdi = function() {
    var qsos = Module.loadQsos();
    if (!qsos.length) { alert('无记录可导出。'); return; }
    var adi = '<ADIF_VER:5>3.1.0<EOH>\n';
    qsos.forEach(function(q) {
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
    Module.downloadFile(qsos[0].call + '_' + new Date().toISOString().split('T')[0] + '.adi', adi, 'text/plain');
    if (global.HAM.EventBus) global.HAM.EventBus.emit('status', 'ADI导出完成');
  };

  Module.logExportCabrillo = function() {
    var qsos = Module.loadQsos();
    if (!qsos.length) { alert('无记录可导出。'); return; }
    var cab = 'START-OF-LOG: 3.0\nCREATED-BY: HAM Radio Toolbox Web\n';
    cab += 'CONTEST: \nCALLSIGN: \n';
    qsos.forEach(function(q) {
      cab += 'QSO: ' + q.freq.toString().padStart(8) + ' ' + q.mode.padEnd(6) + ' ' +
        q.date.replace(/-/g,'') + ' ' + q.time.padStart(4,'0') + ' ' +
        q.call.padEnd(13) + ' ' + (q.rst_s||'59') + ' ' +
        q.call.padEnd(13) + ' ' + (q.rst_r||'59') + '\n';
    });
    cab += 'END-OF-LOG:\n';
    Module.downloadFile('cabrillo_' + new Date().toISOString().split('T')[0] + '.log', cab, 'text/plain');
    if (global.HAM.EventBus) global.HAM.EventBus.emit('status', 'Cabrillo导出完成');
  };

  Module.logExportCsv = function() {
    var qsos = Module.loadQsos();
    if (!qsos.length) { alert('无记录可导出。'); return; }
    var csv = '\uFEFF日期,时间,呼号,频率,模式,RST发送,RST接收,姓名,QTH,备注\n';
    qsos.forEach(function(q) {
      csv += [q.date,q.time,q.call,q.freq,q.mode,q.rst_s,q.rst_r,q.name,q.qth,q.note].map(function(v) {
        return '"' + (v||'').replace(/"/g,'""') + '"';
      }).join(',') + '\n';
    });
    Module.downloadFile('qso_' + new Date().toISOString().split('T')[0] + '.csv', csv, 'text/csv');
    if (global.HAM.EventBus) global.HAM.EventBus.emit('status', 'CSV导出完成');
  };

  Module.logImportAdi = function() { document.getElementById('adiFileInput').click(); };

  Module.logImportAdiFile = function(e) {
    var file = e.target.files[0];
    if (!file) return;
    var reader = new FileReader();
    reader.onload = function(ev) {
      var text = ev.target.result;
      var qsos = Module.loadQsos();
      var count = 0;
      var lines = text.split(/<eor>/i);
      for (var li = 0; li < lines.length; li++) {
        var current = {};
        var re = /<(\w+):(\d+)(?::\w)?>([^<]*)/gi;
        var match;
        while ((match = re.exec(lines[li])) !== null) {
          current[match[1].toUpperCase()] = match[3].trim();
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
      Module.saveQsos(qsos);
      Module.logRefreshTable();
      if (global.HAM.EventBus) global.HAM.EventBus.emit('status', 'ADI导入完成，新增 ' + count + ' 条记录');
      if (global.HAM.EventBus) global.HAM.EventBus.emit('log-updated');
      e.target.value = '';
    };
    reader.readAsText(file);
  };

  Module.logBackup = function() {
    var qsos = Module.loadQsos();
    if (!qsos.length) { alert('无记录可备份。'); return; }
    Module.downloadFile('qso_backup_' + new Date().toISOString().split('T')[0] + '.json', JSON.stringify(qsos, null, 2), 'application/json');
    if (global.HAM.EventBus) global.HAM.EventBus.emit('status', '备份完成');
  };

  Module.logRestore = function() { document.getElementById('restoreFileInput').click(); };

  Module.logRestoreFile = function(e) {
    var file = e.target.files[0];
    if (!file) return;
    var reader = new FileReader();
    reader.onload = function(ev) {
      try {
        var data = JSON.parse(ev.target.result);
        if (!Array.isArray(data)) throw new Error('格式错误');
        Module.saveQsos(data);
        Module.logRefreshTable();
        if (global.HAM.EventBus) global.HAM.EventBus.emit('status', '恢复完成，共 ' + data.length + ' 条记录');
        if (global.HAM.EventBus) global.HAM.EventBus.emit('log-updated');
      } catch(err) { alert('恢复失败: ' + err.message); }
      e.target.value = '';
    };
    reader.readAsText(file);
  };

  Module.init = function() {
    var modeSelect = document.getElementById('logMode');
    if (modeSelect) {
      Core.MODES.forEach(function(m) {
        var o = document.createElement('option');
        o.value = m; o.textContent = m;
        modeSelect.appendChild(o);
      });
    }
    Module.logClearForm();
    Module.logRefreshTable();
  };

  global.HAM.Log = Module;

})(window);