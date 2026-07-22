/**
 * HAM Radio Toolbox - 模块加载器
 * 包含: EventBus事件总线、Tab切换、全局错误边界、模块初始化
 * 依赖: 所有 HAM.* 模块已加载
 */
(function(global) {
  'use strict';

  // ============================================================
  // EventBus 事件总线 - 模块间解耦通信
  // ============================================================
  var EventBus = {
    _listeners: {},
    on: function(event, fn) {
      if (!this._listeners[event]) this._listeners[event] = [];
      this._listeners[event].push(fn);
    },
    off: function(event, fn) {
      if (!this._listeners[event]) return;
      if (!fn) { delete this._listeners[event]; return; }
      this._listeners[event] = this._listeners[event].filter(function(f) { return f !== fn; });
    },
    emit: function(event) {
      var args = Array.prototype.slice.call(arguments, 1);
      var fns = this._listeners[event];
      if (!fns) return;
      fns.forEach(function(fn) {
        try { fn.apply(null, args); }
        catch(e) { console.error('[EventBus] Error in handler for "' + event + '":', e); }
      });
    }
  };

  global.HAM = global.HAM || {};
  global.HAM.EventBus = EventBus;

  // ============================================================
  // 全局错误边界 - 防止单模块崩溃影响整体
  // ============================================================
  global.onerror = function(msg, url, line, col, error) {
    console.error('[HAM Error Boundary]', msg, url, line, col, error);
    var statusEl = document.getElementById('statusBar');
    if (statusEl) {
      var shortMsg = typeof msg === 'string' ? msg.substring(0, 80) : String(msg);
      statusEl.textContent = '⚠️ 错误: ' + shortMsg;
      statusEl.style.color = '#e74c3c';
      setTimeout(function() { statusEl.style.color = ''; }, 5000);
    }
    return true; // 阻止默认错误处理
  };

  global.addEventListener('unhandledrejection', function(e) {
    console.error('[HAM Error Boundary] Unhandled Promise:', e.reason);
  });

  // ============================================================
  // 状态栏
  // ============================================================
  function setStatus(msg) {
    var el = document.getElementById('statusBar');
    if (el) { el.textContent = msg; el.style.color = ''; }
  }

  EventBus.on('status', setStatus);

  // ============================================================
  // Tab 切换
  // ============================================================
  document.querySelectorAll('.tab-btn').forEach(function(btn) {
    btn.addEventListener('click', function() {
      document.querySelectorAll('.tab-btn').forEach(function(b) { b.classList.remove('active'); });
      document.querySelectorAll('.tab-content').forEach(function(c) { c.classList.remove('active'); });
      btn.classList.add('active');
      var tabEl = document.getElementById('tab-' + btn.dataset.tab);
      if (tabEl) tabEl.classList.add('active');
      // 按需初始化地图
      if (btn.dataset.tab === 'map' && global.HAM.Map) {
        setTimeout(function() { global.HAM.Map.mapRender(); }, 100);
      }
      // 工具Tab时更新时钟
      if (btn.dataset.tab === 'utils' && global.HAM.Utils) {
        global.HAM.Utils.updateClocks();
      }
    });
  });

  function switchSubTab(el, parent) {
    var container = el.closest('.tab-content') || el.closest('.card');
    container.querySelectorAll('.sub-tab').forEach(function(t) { t.classList.remove('active'); });
    container.querySelectorAll('.sub-content').forEach(function(c) { c.classList.remove('active'); });
    el.classList.add('active');
    var subEl = document.getElementById(parent + '-' + el.dataset.sub);
    if (subEl) subEl.classList.add('active');
  }

  // 暴露到全局（HTML onclick 需要调用）
  global.switchSubTab = switchSubTab;
  global.setStatus = setStatus;

  // ============================================================
  // 模块安全初始化 - 每个模块独立try-catch
  // ============================================================
  var modules = ['Freq', 'RF', 'Grid', 'Log', 'Map', 'Ref', 'CW', 'Utils'];
  var initErrors = [];

  modules.forEach(function(name) {
    var mod = global.HAM[name];
    if (mod && typeof mod.init === 'function') {
      try {
        mod.init();
        console.log('[HAM Loader] Module ' + name + ' initialized OK');
      } catch(e) {
        initErrors.push(name);
        console.error('[HAM Loader] Module ' + name + ' init FAILED:', e);
      }
    } else if (!mod) {
      console.warn('[HAM Loader] Module ' + name + ' not loaded (skipped)');
    }
  });

  // ============================================================
  // 全局函数映射 - HTML onclick 需要调用的函数
  // ============================================================
  // 频率/频段
  global.onSearchModeChange = function() { if (global.HAM.Freq) global.HAM.Freq.onSearchModeChange(); };
  global.freqQuery = function() { if (global.HAM.Freq) global.HAM.Freq.freqQuery(); };
  global.freqClear = function() { if (global.HAM.Freq) global.HAM.Freq.freqClear(); };

  // 射频工具
  global.antennaCalc = function() { if (global.HAM.RF) global.HAM.RF.antennaCalc(); };
  global.powerConvert = function() { if (global.HAM.RF) global.HAM.RF.powerConvert(); };
  global.swrFromPower = function() { if (global.HAM.RF) global.HAM.RF.swrFromPower(); };
  global.swrToReflect = function() { if (global.HAM.RF) global.HAM.RF.swrToReflect(); };
  global.coaxCalc = function() { if (global.HAM.RF) global.HAM.RF.coaxCalc(); };

  // 网格坐标
  global.llToGrid = function() { if (global.HAM.Grid) global.HAM.Grid.llToGrid(); };
  global.gridToLl = function() { if (global.HAM.Grid) global.HAM.Grid.gridToLl(); };
  global.gridDistance = function() { if (global.HAM.Grid) global.HAM.Grid.gridDistance(); };

  // 通联日志
  global.logModeRstPreset = function() { if (global.HAM.Log) global.HAM.Log.logModeRstPreset(); };
  global.logAdd = function() { if (global.HAM.Log) global.HAM.Log.logAdd(); };
  global.logClearForm = function() { if (global.HAM.Log) global.HAM.Log.logClearForm(); };
  global.logRefreshTable = function() { if (global.HAM.Log) global.HAM.Log.logRefreshTable(); };
  global.logExportAdi = function() { if (global.HAM.Log) global.HAM.Log.logExportAdi(); };
  global.logExportCabrillo = function() { if (global.HAM.Log) global.HAM.Log.logExportCabrillo(); };
  global.logExportCsv = function() { if (global.HAM.Log) global.HAM.Log.logExportCsv(); };
  global.logImportAdi = function() { if (global.HAM.Log) global.HAM.Log.logImportAdi(); };
  global.logImportAdiFile = function(e) { if (global.HAM.Log) global.HAM.Log.logImportAdiFile(e); };
  global.logBackup = function() { if (global.HAM.Log) global.HAM.Log.logBackup(); };
  global.logRestore = function() { if (global.HAM.Log) global.HAM.Log.logRestore(); };
  global.logRestoreFile = function(e) { if (global.HAM.Log) global.HAM.Log.logRestoreFile(e); };

  // 通联地图
  global.mapRender = function() { if (global.HAM.Map) global.HAM.Map.mapRender(); };

  // 参考数据
  global.abbrevLookup = function(type) { if (global.HAM.Ref) global.HAM.Ref.abbrevLookup(type); };

  // CW练习
  global.cwEncode = function() { if (global.HAM.CW) global.HAM.CW.cwEncode(); };
  global.cwPlayEncode = function() { if (global.HAM.CW) global.HAM.CW.cwPlayEncode(); };
  global.cwDecode = function() { if (global.HAM.CW) global.HAM.CW.cwDecode(); };
  global.cwStopPlay = function() { if (global.HAM.CW) global.HAM.CW.cwStopPlay(); };
  global.cwPracticeStart = function() { if (global.HAM.CW) global.HAM.CW.cwPracticeStart(); };
  global.cwPracticeReveal = function() { if (global.HAM.CW) global.HAM.CW.cwPracticeReveal(); };
  global.cwPracticeCheck = function() { if (global.HAM.CW) global.HAM.CW.cwPracticeCheck(); };

  // 工具
  global.updateClocks = function() { if (global.HAM.Utils) global.HAM.Utils.updateClocks(); };
  global.addCustomClock = function() { if (global.HAM.Utils) global.HAM.Utils.addCustomClock(); };
  global.clearCustomClocks = function() { if (global.HAM.Utils) global.HAM.Utils.clearCustomClocks(); };
  global.propFetch = function() { if (global.HAM.Utils) global.HAM.Utils.propFetch(); };
  global.rstQuery = function() { if (global.HAM.Utils) global.HAM.Utils.rstQuery(); };

  // ============================================================
  // 启动完成
  // ============================================================
  if (initErrors.length > 0) {
    setStatus('⚠️ HAM Radio Toolbox 部分模块加载异常: ' + initErrors.join(', '));
  } else {
    setStatus('HAM Radio Toolbox 就绪');
  }

  console.log('[HAM Loader] All modules loaded. Errors:', initErrors.length);

})(window);