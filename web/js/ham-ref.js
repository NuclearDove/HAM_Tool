/**
 * HAM Radio Toolbox - 参考数据 Tab 模块
 * 包含Q简语、英文缩略语、数字缩略语查询
 * 依赖: HAM.Core
 */
(function(global) {
  'use strict';

  var Core = global.HAM && global.HAM.Core;
  if (!Core) { console.error('HAM.Core not loaded'); return; }

  var Module = {};

  Module.initRefTables = function() {
    var qt = document.querySelector('#qcodeTable tbody');
    if (qt) qt.innerHTML = Core.Q_CODES.map(function(q) {
      return '<tr><td>' + q[0] + '</td><td>' + q[1] + '</td><td>' + q[2] + '</td></tr>';
    }).join('');

    var et = document.querySelector('#engabbrTable tbody');
    if (et) et.innerHTML = Core.ENG_ABBREV.map(function(a) {
      return '<tr><td>' + a[0] + '</td><td>' + a[1] + '</td><td>' + a[2] + '</td></tr>';
    }).join('');

    var nt = document.querySelector('#numabbrTable tbody');
    if (nt) nt.innerHTML = Core.NUM_ABBREV.map(function(a) {
      return '<tr><td>' + a[0] + '</td><td>' + a[1] + '</td><td>' + a[2] + '</td></tr>';
    }).join('');
  };

  Module.abbrevLookup = function(type) {
    var search, data, resultId;
    if (type === 'qcode') {
      search = document.getElementById('qcodeSearch').value.trim().toUpperCase();
      data = Core.Q_CODES; resultId = 'qcodeResult';
    } else if (type === 'engabbr') {
      search = document.getElementById('engabbrSearch').value.trim().toUpperCase();
      data = Core.ENG_ABBREV; resultId = 'engabbrResult';
    } else {
      search = document.getElementById('numabbrSearch').value.trim();
      data = Core.NUM_ABBREV; resultId = 'numabbrResult';
    }
    if (!search) { document.getElementById(resultId).textContent = '请输入查询内容。'; return; }
    var found = data.filter(function(d) { return d[0].toUpperCase().includes(search); });
    if (found.length === 0) {
      document.getElementById(resultId).textContent = '未找到匹配项。';
    } else {
      document.getElementById(resultId).textContent = found.map(function(d) {
        return d[0] + ': ' + d[1] + '\n' + (d[2] ? '  (' + d[2] + ')' : '');
      }).join('\n\n');
    }
  };

  Module.init = function() {
    Module.initRefTables();
  };

  global.HAM.Ref = Module;

})(window);