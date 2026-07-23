/**
 * HAM Radio Toolbox - 应用入口 (ES Module)
 * 整合模块初始化、Tab切换、全局函数映射、动态导入、错误边界
 * @module app
 */
'use strict';

import { EventBus } from './event-bus.js';
import * as Freq from './ham-freq.js';
import * as RF from './ham-rf.js';
import * as Grid from './ham-grid.js';
import * as Ref from './ham-ref.js';
import * as CW from './ham-cw.js';
import * as Utils from './ham-utils.js';

// 动态导入非核心模块（按需加载）
let Log = null;
let Map = null;

// ============================================================
// 全局错误边界
// ============================================================
window.onerror = function(msg, url, line, col, error) {
  console.error('[HAM Error Boundary]', msg, url, line, col, error);
  const statusEl = document.getElementById('statusBar');
  if (statusEl) {
    const shortMsg = typeof msg === 'string' ? msg.substring(0, 80) : String(msg);
    statusEl.textContent = '⚠️ 错误: ' + shortMsg;
    statusEl.style.color = '#e74c3c';
    setTimeout(() => { statusEl.style.color = ''; }, 5000);
  }
  return true;
};

window.addEventListener('unhandledrejection', e => {
  console.error('[HAM Error Boundary] Unhandled Promise:', e.reason);
});

// ============================================================
// 状态栏
// ============================================================
function setStatus(msg) {
  const el = document.getElementById('statusBar');
  if (el) { el.textContent = msg; el.style.color = ''; }
}
EventBus.on('status', setStatus);

// ============================================================
// Tab 切换
// ============================================================
function initTabs() {
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
      btn.classList.add('active');
      const tabEl = document.getElementById('tab-' + btn.dataset.tab);
      if (tabEl) tabEl.classList.add('active');

      // 按需加载并初始化地图模块
      if (btn.dataset.tab === 'map') {
        if (!Map) {
          import('./ham-map.js').then(mod => {
            Map = mod;
            Map.init();
            mapMapFunctions();
            setTimeout(() => Map.mapRender(), 100);
          }).catch(err => console.error('[HAM] Map module load failed:', err));
        } else {
          setTimeout(() => Map.mapRender(), 100);
        }
      }

      // 按需加载日志模块
      if (btn.dataset.tab === 'log' && !Log) {
        import('./ham-log.js').then(mod => {
          Log = mod;
          Log.init();
          // 映射日志全局函数
          mapLogFunctions();
        }).catch(err => console.error('[HAM] Log module load failed:', err));
      }

      // 工具Tab时更新时钟
      if (btn.dataset.tab === 'utils') {
        Utils.updateClocks();
      }
    });
  });
}

// 子Tab切换
function switchSubTab(el, parent) {
  const container = el.closest('.tab-content') || el.closest('.card');
  container.querySelectorAll('.sub-tab').forEach(t => t.classList.remove('active'));
  container.querySelectorAll('.sub-content').forEach(c => c.classList.remove('active'));
  el.classList.add('active');
  const subEl = document.getElementById(parent + '-' + el.dataset.sub);
  if (subEl) subEl.classList.add('active');
}

// ============================================================
// 全局函数映射 - HTML onclick 需要调用的函数
// ============================================================
function mapGlobalFunctions() {
  // 频率查询
  window.onSearchModeChange = () => Freq.onSearchModeChange();
  window.freqQuery = () => Freq.freqQuery();
  window.freqClear = () => Freq.freqClear();

  // 射频计算
  window.antennaCalc = () => RF.antennaCalc();
  window.powerConvert = () => RF.powerConvert();
  window.swrFromPower = () => RF.swrFromPower();
  window.swrToReflect = () => RF.swrToReflect();
  window.coaxCalc = () => RF.coaxCalc();

  // 网格坐标
  window.llToGrid = () => Grid.llToGrid();
  window.gridToLl = () => Grid.gridToLl();
  window.gridDistance = () => Grid.gridDistance();

  // 参考查询
  window.abbrevLookup = (type) => Ref.abbrevLookup(type);

  // CW练习
  window.cwEncode = () => CW.cwEncode();
  window.cwPlayEncode = () => CW.cwPlayEncode();
  window.cwDecode = () => CW.cwDecode();
  window.cwStopPlay = () => CW.cwStopPlay();
  window.cwPracticeStart = () => CW.cwPracticeStart();
  window.cwPracticeReveal = () => CW.cwPracticeReveal();
  window.cwPracticeCheck = () => CW.cwPracticeCheck();

  // 工具
  window.updateClocks = () => Utils.updateClocks();
  window.addCustomClock = () => Utils.addCustomClock();
  window.clearCustomClocks = () => Utils.clearCustomClocks();
  window.filterClockOptions = () => Utils.filterClockOptions();
  window.hideClockOptions = () => Utils.hideClockOptions();
  window.propFetch = () => Utils.propFetch();
  window.rstQuery = () => Utils.rstQuery();

  // 子Tab切换
  window.switchSubTab = switchSubTab;
  window.setStatus = setStatus;
}

// 日志模块全局函数映射（延迟，因模块按需加载）
function mapLogFunctions() {
  if (!Log) return;
  window.logModeRstPreset = () => Log.logModeRstPreset();
  window.logAdd = () => Log.logAdd();
  window.logCancelEdit = () => Log.logCancelEdit();
  window.logClearForm = () => Log.logClearForm();
  window.logRefreshTable = () => Log.logRefreshTable();
  window.logEdit = (id) => Log.logEdit(id);
  window.logDelete = (id) => Log.logDelete(id);
  window.logExportAdi = () => Log.logExportAdi();
  window.logExportCabrillo = () => Log.logExportCabrillo();
  window.logExportCsv = () => Log.logExportCsv();
  window.logImportAdi = () => Log.logImportAdi();
  window.logImportAdiFile = (e) => Log.logImportAdiFile(e);
  window.logBackup = () => Log.logBackup();
  window.logRestore = () => Log.logRestore();
  window.logRestoreFile = (e) => Log.logRestoreFile(e);
}

// 地图模块全局函数映射（延迟）
function mapMapFunctions() {
  if (!Map) return;
  window.mapRender = () => Map.mapRender();
}

// ============================================================
// 模块安全初始化
// ============================================================
function safeInit(name, mod) {
  if (mod && typeof mod.init === 'function') {
    try {
      mod.init();
      console.log('[HAM] Module ' + name + ' initialized OK');
    } catch(e) {
      console.error('[HAM] Module ' + name + ' init FAILED:', e);
    }
  }
}

// ============================================================
// 应用启动
// ============================================================
function boot() {
  // 初始化核心模块
  safeInit('Freq', Freq);
  safeInit('RF', RF);
  safeInit('Grid', Grid);
  safeInit('Ref', Ref);
  safeInit('CW', CW);
  safeInit('Utils', Utils);

  // Tab切换
  initTabs();

  // 全局函数映射
  mapGlobalFunctions();

  // 如果日志Tab默认激活，立即加载
  const logTab = document.getElementById('tab-log');
  if (logTab && logTab.classList.contains('active')) {
    import('./ham-log.js').then(mod => {
      Log = mod;
      safeInit('Log', Log);
      mapLogFunctions();
    }).catch(err => console.error('[HAM] Log module load failed:', err));
  }

  // 如果地图Tab默认激活，立即加载
  const mapTab = document.getElementById('tab-map');
  if (mapTab && mapTab.classList.contains('active')) {
    import('./ham-map.js').then(mod => {
      Map = mod;
      safeInit('Map', Map);
      mapMapFunctions();
      setTimeout(() => Map.mapRender(), 100);
    }).catch(err => console.error('[HAM] Map module load failed:', err));
  }

  setStatus('HAM Radio Toolbox 就绪');
  console.log('[HAM] App booted (ES Modules)');
}

// DOM就绪后启动
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', boot);
} else {
  boot();
}