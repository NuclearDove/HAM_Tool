/**
 * HAM Radio Toolbox - CW练习 Tab 模块
 * 包含摩尔斯码编解码、音频播放、模拟电键、随机练习
 * 依赖: HAM.Core
 */
(function(global) {
  'use strict';

  var Core = global.HAM && global.HAM.Core;
  if (!Core) { console.error('HAM.Core not loaded'); return; }

  var Module = {};

  // 音频状态
  var audioCtx = null;
  var cwPlaying = false;
  var cwPlayTimeout = null;

  function getAudioCtx() {
    if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    return audioCtx;
  }

  function cwPlayTone(startTime, duration) {
    var ctx = getAudioCtx();
    var osc = ctx.createOscillator();
    var gain = ctx.createGain();
    osc.type = 'sine';
    osc.frequency.value = 700;
    gain.gain.setValueAtTime(0, startTime);
    gain.gain.linearRampToValueAtTime(0.5, startTime + 0.005);
    gain.gain.setValueAtTime(0.5, startTime + duration - 0.005);
    gain.gain.linearRampToValueAtTime(0, startTime + duration);
    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.start(startTime);
    osc.stop(startTime + duration);
  }

  Module.cwPlayMorse = function(morseStr, wpm, callback) {
    Module.cwStopPlay();
    cwPlaying = true;
    var ctx = getAudioCtx();
    var dotDur = 1.2 / wpm;
    var dashDur = dotDur * 3;
    var symGap = dotDur;
    var charGap = dotDur * 3;
    var wordGap = dotDur * 7;
    var t = ctx.currentTime + 0.1;
    var chars = morseStr.split(' ');
    chars.forEach(function(c) {
      if (c === '/') { t += wordGap; return; }
      for (var i = 0; i < c.length; i++) {
        var ch = c[i];
        if (ch === '·' || ch === '.') { cwPlayTone(t, dotDur); t += dotDur; }
        else if (ch === '-' || ch === '–') { cwPlayTone(t, dashDur); t += dashDur; }
        if (i < c.length - 1) t += symGap;
      }
      t += charGap;
    });
    var totalMs = (t - ctx.currentTime) * 1000;
    cwPlayTimeout = setTimeout(function() { cwPlaying = false; if (callback) callback(); }, totalMs);
  };

  Module.cwStopPlay = function() {
    cwPlaying = false;
    if (cwPlayTimeout) { clearTimeout(cwPlayTimeout); cwPlayTimeout = null; }
    try { if (audioCtx) { audioCtx.close(); audioCtx = null; } } catch(e) {}
  };

  Module.cwEncode = function() {
    var text = document.getElementById('cwEncodeIn').value;
    if (!text) { document.getElementById('cwEncodeOut').textContent = ''; return; }
    document.getElementById('cwEncodeOut').textContent = Core.morseEncode(text);
    if (global.HAM.EventBus) global.HAM.EventBus.emit('status', '摩尔斯编码完成');
  };

  Module.cwPlayEncode = function() {
    var morse = document.getElementById('cwEncodeOut').textContent;
    if (!morse) { Module.cwEncode(); }
    var m = document.getElementById('cwEncodeOut').textContent;
    if (!m) return;
    var wpm = parseInt(document.getElementById('cwWpm').value);
    Module.cwPlayMorse(m, wpm);
    if (global.HAM.EventBus) global.HAM.EventBus.emit('status', '播放中...');
  };

  Module.cwDecode = function() {
    var morse = document.getElementById('cwDecodeIn').value;
    if (!morse) { document.getElementById('cwDecodeOut').textContent = ''; return; }
    document.getElementById('cwDecodeOut').textContent = Core.morseDecode(morse);
    if (global.HAM.EventBus) global.HAM.EventBus.emit('status', '摩尔斯解码完成');
  };

  // 模拟电键
  var keyDownTime = 0;
  var keyTimer = null;

  Module.initCwKey = function() {
    var cwKeyBtn = document.getElementById('cwKeyBtn');
    if (!cwKeyBtn) return;

    cwKeyBtn.addEventListener('mousedown', function(e) {
      e.preventDefault();
      keyDownTime = Date.now();
      cwKeyBtn.classList.add('pressed');
    });
    cwKeyBtn.addEventListener('mouseup', function(e) {
      e.preventDefault();
      cwKeyBtn.classList.remove('pressed');
      var dur = Date.now() - keyDownTime;
      var dotDur = 1.2 / parseInt(document.getElementById('cwWpm').value) * 1000;
      var sym = dur < dotDur * 2 ? '·' : '-';
      document.getElementById('cwDecodeIn').value += sym;
      if (keyTimer) clearTimeout(keyTimer);
      keyTimer = setTimeout(function() { document.getElementById('cwDecodeIn').value += ' '; }, dotDur * 4);
    });
    cwKeyBtn.addEventListener('touchstart', function(e) {
      e.preventDefault();
      keyDownTime = Date.now();
      cwKeyBtn.classList.add('pressed');
    });
    cwKeyBtn.addEventListener('touchend', function(e) {
      e.preventDefault();
      cwKeyBtn.classList.remove('pressed');
      var dur = Date.now() - keyDownTime;
      var dotDur = 1.2 / parseInt(document.getElementById('cwWpm').value) * 1000;
      var sym = dur < dotDur * 2 ? '·' : '-';
      document.getElementById('cwDecodeIn').value += sym;
      if (keyTimer) clearTimeout(keyTimer);
      keyTimer = setTimeout(function() { document.getElementById('cwDecodeIn').value += ' '; }, dotDur * 4);
    });
  };

  // CW 随机练习
  var practiceAnswer = '';
  var practiceGroupCount = 0;
  var practiceCurrentGroup = 0;

  Module.cwPracticeStart = function() {
    var alpha = document.getElementById('cwPracAlpha').checked;
    var num = document.getElementById('cwPracNum').checked;
    var punct = document.getElementById('cwPracPunct').checked;
    if (!alpha && !num && !punct) { alert('请至少选择一种字符集。'); return; }
    var chars = '';
    if (alpha) chars += 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
    if (num) chars += '0123456789';
    if (punct) chars += '.,?/()=+-:;';
    var len = parseInt(document.getElementById('cwPracLen').value);
    var count = parseInt(document.getElementById('cwPracCount').value);
    var groups = [];
    for (var i = 0; i < count; i++) {
      var g = '';
      for (var j = 0; j < len; j++) g += chars[Math.floor(Math.random() * chars.length)];
      groups.push(g);
    }
    practiceAnswer = groups.join(' ');
    practiceGroupCount = count;
    practiceCurrentGroup = 0;
    var morse = Core.morseEncode(practiceAnswer);
    document.getElementById('cwPracDisp').textContent = morse;
    document.getElementById('cwPracLog').textContent = '第 ' + (practiceCurrentGroup + 1) + '/' + count + ' 组，正在播放...';
    document.getElementById('cwPracUser').value = '';
    document.getElementById('cwPracScore').textContent = '';
    var wpm = parseInt(document.getElementById('cwWpm').value);
    Module.cwPlayMorse(morse, wpm, function() {
      document.getElementById('cwPracLog').textContent = '播放完毕，请输入抄收内容。';
    });
  };

  Module.cwPracticeReveal = function() {
    if (practiceAnswer) document.getElementById('cwPracLog').textContent = '答案: ' + practiceAnswer;
  };

  Module.cwPracticeCheck = function() {
    var user = document.getElementById('cwPracUser').value.toUpperCase().trim();
    var answer = practiceAnswer.toUpperCase();
    if (!user || !answer) return;
    var correct = 0, total = answer.replace(/\s/g,'').length;
    var uArr = user.replace(/\s/g,'').split('');
    var aArr = answer.replace(/\s/g,'').split('');
    for (var i = 0; i < Math.min(uArr.length, aArr.length); i++) {
      if (uArr[i] === aArr[i]) correct++;
    }
    var pct = total > 0 ? (correct / total * 100).toFixed(1) : 0;
    document.getElementById('cwPracScore').textContent = '正确率: ' + correct + '/' + total + ' = ' + pct + '%';
    if (global.HAM.EventBus) global.HAM.EventBus.emit('status', '练习评分完成');
  };

  Module.initMorseTable = function() {
    var tbody = document.querySelector('#morseTable tbody');
    if (!tbody) return;
    tbody.innerHTML = Object.entries(Core.MORSE_CODE).map(function(entry) {
      return '<tr><td style="font-weight:700;font-size:14px">' + entry[0] + '</td><td style="font-family:Consolas,monospace;font-size:16px;letter-spacing:2px">' + entry[1] + '</td></tr>';
    }).join('');
  };

  Module.init = function() {
    Module.initCwKey();
    Module.initMorseTable();
  };

  global.HAM.CW = Module;

})(window);