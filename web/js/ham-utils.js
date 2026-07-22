/**
 * HAM Radio Toolbox - 工具 Tab 模块
 * 包含世界时钟、传播条件、RST信号报告
 * 依赖: HAM.Core
 */
(function(global) {
  'use strict';

  var Core = global.HAM && global.HAM.Core;
  if (!Core) { console.error('HAM.Core not loaded'); return; }

  var Module = {};

  // 自定义时钟
  var customClocks = [];
  try { customClocks = JSON.parse(localStorage.getItem('ham_custom_clocks')) || []; } catch(e) {}

  Module.updateClocks = function() {
    var grid = document.getElementById('clockGrid');
    if (!grid) return;
    var all = Core.DEFAULT_CLOCKS.concat(customClocks);
    grid.innerHTML = all.map(function(c) {
      var now = new Date();
      var time = now.toLocaleTimeString('zh-CN', { timeZone: c.tz, hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });
      var date = now.toLocaleDateString('zh-CN', { timeZone: c.tz, month: '2-digit', day: '2-digit', weekday: 'short' });
      return '<div class="clock-card"><div class="tz-name">' + c.name + '</div><div class="tz-time">' + time + '</div><div style="font-size:10px;color:#999">' + date + '</div></div>';
    }).join('');
  };

  Module.addCustomClock = function() {
    var input = document.getElementById('customTzInput').value.trim();
    if (!input) return;
    // 尝试匹配城市
    var city = Core.CITY_COORDS[input] || Core.CITY_COORDS[Object.keys(Core.CITY_COORDS).find(function(k){return k.toLowerCase() === input.toLowerCase();})];
    var tz = input;
    // 常用时区映射
    var tzMap = {
      'UTC':'UTC','GMT':'UTC','EST':'America/New_York','CST':'America/Chicago',
      'MST':'America/Denver','PST':'America/Los_Angeles','JST':'Asia/Tokyo',
      'CET':'Europe/Paris','EET':'Europe/Helsinki','AEST':'Australia/Sydney',
      'KST':'Asia/Seoul','IST':'Asia/Kolkata','CST8':'Asia/Shanghai'
    };
    if (tzMap[input.toUpperCase()]) tz = tzMap[input.toUpperCase()];
    try {
      new Date().toLocaleTimeString('zh-CN', { timeZone: tz });
      customClocks.push({ name: input, tz: tz });
      localStorage.setItem('ham_custom_clocks', JSON.stringify(customClocks));
      Module.updateClocks();
      document.getElementById('customTzInput').value = '';
      if (global.HAM.EventBus) global.HAM.EventBus.emit('status', '时钟已添加: ' + input);
    } catch(e) {
      alert('无效时区，请输入 IANA 时区名（如 Asia/Tokyo）或常见缩写。');
    }
  };

  Module.clearCustomClocks = function() {
    customClocks = [];
    localStorage.removeItem('ham_custom_clocks');
    Module.updateClocks();
    if (global.HAM.EventBus) global.HAM.EventBus.emit('status', '自定义时钟已清除');
  };

  // 传播条件
  Module.propFetch = function() {
    document.getElementById('propStatus').textContent = '正在获取...';
    fetch('https://hamqsl.com/solar101vhfpic.php')
      .then(function(r) { return r.ok ? r.text() : Promise.reject('HTTP ' + r.status); })
      .then(function(html) {
        return fetch('https://hamqsl.com/solarn0nbh.php');
      })
      .then(function(r) { return r.ok ? r.text() : Promise.reject('HTTP ' + r.status); })
      .then(function(html) {
        document.getElementById('propResult').innerHTML = '<p>太阳传播数据已获取。</p><p>详细数据请访问: <a href="https://hamqsl.com/solar.html" target="_blank">hamqsl.com</a></p><img src="https://hamqsl.com/solarn0nbh.php" style="max-width:100%;border-radius:4px" alt="Solar Data">';
        document.getElementById('propStatus').textContent = '已更新';
      })
      .catch(function(err) {
        document.getElementById('propResult').textContent = '获取失败: ' + err + '\n\n请直接访问 https://hamqsl.com/solar.html 查看传播条件。';
        document.getElementById('propStatus').textContent = '获取失败';
      });
  };

  // RST 信号报告
  Module.rstQuery = function() {
    var input = document.getElementById('rstInput').value.trim();
    if (!input) { document.getElementById('rstResult').textContent = '请输入RST值。'; return; }
    var digits = input.replace(/[^0-9]/g, '');
    var lines = [];
    if (digits.length >= 2) {
      var r = parseInt(digits[0]), s = parseInt(digits[1]);
      lines.push('R (' + r + '): ' + (Core.R_READABILITY[r] || '未知'));
      lines.push('S (' + s + '): ' + (Core.S_STRENGTH[s] || '未知'));
      if (digits.length >= 3) {
        var t = parseInt(digits[2]);
        lines.push('T (' + t + '): ' + (Core.T_TONE[t] || '未知'));
      }
      lines.push('\n完整解读: ' + lines.join(' → ').replace(/\n/g,' → '));
    } else {
      lines.push('请输入2位(RS)或3位(RST)数字。');
    }
    document.getElementById('rstResult').textContent = lines.join('\n');
  };

  var clockInterval = null;

  Module.init = function() {
    Module.updateClocks();
    clockInterval = setInterval(Module.updateClocks, 1000);
  };

  Module.destroy = function() {
    if (clockInterval) { clearInterval(clockInterval); clockInterval = null; }
  };

  global.HAM.Utils = Module;

})(window);