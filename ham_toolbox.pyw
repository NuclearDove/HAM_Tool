#!/usr/bin/env python3
"""
HAM Radio Toolbox - 业余无线电工具箱
A visual toolkit for amateur radio operators with GUI interface.
"""

import math
import re
import os
import json
import shutil
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from datetime import datetime, timezone
from PIL import Image, ImageTk
import tkintermapview
import requests


# ============================================================
# 核心计算函数
# ============================================================

C = 299_792_458

CAT_CN = {"VLF": "甚低频", "LF": "低频", "MF": "中频", "HF": "高频",
           "VHF": "甚高频", "UHF": "特高频", "SHF": "超高频", "EHF": "极高频"}

BANDS = [
    {"name": "2200m",  "f_low": 0.1357,  "f_high": 0.1378, "cat": "LF", 
     "license": "C(≤1000W)", "svc": "次要业务"},
    {"name": "630m",   "f_low": 0.472,   "f_high": 0.479,  "cat": "MF", 
     "license": "C(≤1000W)", "svc": "次要业务"},
    {"name": "160m",   "f_low": 1.8,     "f_high": 2.0,    "cat": "MF", 
     "license": "C(≤1000W)", "svc": "主要业务"},
    {"name": "80m",    "f_low": 3.5,     "f_high": 3.9,    "cat": "HF", 
     "license": "B(<15W) / C(≤1000W)", "svc": "共同主要业务"},
    {"name": "60m",    "f_low": 5.3515,  "f_high": 5.3665, "cat": "HF", 
     "license": "B(<15W) / C(≤1000W)", "svc": "次要业务"},
    {"name": "40m",    "f_low": 7.0,     "f_high": 7.2,    "cat": "HF", 
     "license": "B(<15W) / C(≤1000W)", "svc": "主要业务"},
    {"name": "30m",    "f_low": 10.1,    "f_high": 10.15,  "cat": "HF", 
     "license": "B(<15W) / C(≤1000W)", "svc": "次要业务"},
    {"name": "20m",    "f_low": 14.0,    "f_high": 14.35,  "cat": "HF", 
     "license": "B(<15W) / C(≤1000W)", "svc": "主要业务"},
    {"name": "17m",    "f_low": 18.068,  "f_high": 18.168, "cat": "HF", 
     "license": "B(<15W) / C(≤1000W)", "svc": "主要业务"},
    {"name": "15m",    "f_low": 21.0,    "f_high": 21.45,  "cat": "HF", 
     "license": "B(<15W) / C(≤1000W)", "svc": "主要业务"},
    {"name": "12m",    "f_low": 24.89,   "f_high": 24.99,  "cat": "HF", 
     "license": "B(<15W) / C(≤1000W)", "svc": "主要业务"},
    {"name": "10m",    "f_low": 28.0,    "f_high": 29.7,   "cat": "HF", 
     "license": "B(<15W) / C(≤1000W)", "svc": "主要业务"},
    {"name": "6m",     "f_low": 50.0,    "f_high": 54.0,   "cat": "VHF",
     "license": "A/B/C(≤25W)", "svc": "共同主要业务"},
    {"name": "2m",     "f_low": 144.0,   "f_high": 148.0,  "cat": "VHF",
     "license": "A/B/C(≤25W)", "svc": "主要业务"},
    {"name": "1.25m",  "f_low": 222.0,   "f_high": 225.0,  "cat": "VHF",
     "license": "A/B/C(≤25W)", "svc": "主要业务"},
    {"name": "70cm",   "f_low": 430.0,   "f_high": 440.0,  "cat": "UHF",
     "license": "A/B/C(≤25W)", "svc": "共同主要业务"},
    {"name": "33cm",   "f_low": 902.0,   "f_high": 928.0,  "cat": "UHF",
     "license": "A/B/C(≤25W)", "svc": "主要业务"},
    {"name": "23cm",   "f_low": 1240.0,  "f_high": 1300.0, "cat": "UHF",
     "license": "A/B/C(≤25W)", "svc": "主要业务"},
    {"name": "13cm",   "f_low": 2300.0,  "f_high": 2450.0, "cat": "UHF",
     "license": "A/B/C(≤25W)", "svc": "共同主要业务"},
    {"name": "9cm",    "f_low": 3300.0,  "f_high": 3500.0,   "cat": "SHF",
     "license": "A/B/C(≤25W)", "svc": "共同主要业务"},
    {"name": "6cm",    "f_low": 5650.0,  "f_high": 5850.0,   "cat": "SHF",
     "license": "A/B/C(≤25W)", "svc": "主要业务"},
    {"name": "3cm",   "f_low": 10000.0,  "f_high": 10500.0,  "cat": "SHF",
     "license": "A/B/C(≤25W)", "svc": "主要业务"},
    {"name": "1.2cm", "f_low": 24000.0,  "f_high": 24250.0,  "cat": "SHF",
     "license": "A/B/C(≤25W)", "svc": "主要业务"},
    {"name": "6mm",   "f_low": 47000.0,  "f_high": 47200.0,"cat": "EHF",
     "license": "A/B/C(≤25W)", "svc": "主要业务"},
]


def freq_to_band(freq_mhz):
    for b in BANDS:
        if b["f_low"] <= freq_mhz <= b["f_high"]:
            return {"name": b["name"], "cat": b["cat"],
                    "license": b["license"], "svc": b["svc"]}
    return None


SPECTRUM_CATS = [
    (0.003, 0.03,   "VLF"),
    (0.03,  0.3,    "LF"),
    (0.3,   3,      "MF"),
    (3,     30,     "HF"),
    (30,    300,    "VHF"),
    (300,   3000,   "UHF"),
    (3000,  30000,  "SHF"),
    (30000, 300000, "EHF"),
]


def freq_to_spectrum_cat(freq_mhz):
    for low, high, cat in SPECTRUM_CATS:
        if low <= freq_mhz < high:
            return f"{cat}{CAT_CN[cat]}"
    return "未知"


def wavelength(freq_mhz):
    return C / (freq_mhz * 1e6)


def dipole_length(freq_mhz):
    lam = wavelength(freq_mhz)
    return {"total_m": lam / 2, "total_ft": lam / 2 * 3.28084,
            "per_leg_m": lam / 4, "per_leg_ft": lam / 4 * 3.28084}


def quarter_wave_length(freq_mhz):
    lam = wavelength(freq_mhz)
    return {"total_m": lam / 4, "total_ft": lam / 4 * 3.28084}


def grid_to_latlon(grid):
    grid = grid.upper().strip()
    if not re.match(r'^[A-R]{2}[0-9]{2}([A-X]{2}([0-9]{2})?)?$', grid):
        raise ValueError(f"无效网格: {grid}")
    lon = (ord(grid[0]) - 65) * 20 - 180
    lat = (ord(grid[1]) - 65) * 10 - 90
    if len(grid) >= 4:
        lon += int(grid[2]) * 2
        lat += int(grid[3]) * 1
    if len(grid) >= 6:
        lon += (ord(grid[4]) - 65) * 5 / 60
        lat += (ord(grid[5]) - 65) * 2.5 / 60
    if len(grid) == 4:
        lon += 1; lat += 0.5
    elif len(grid) == 6:
        lon += 5 / 120; lat += 2.5 / 120
    return lat, lon


def latlon_to_grid(lat, lon, precision=4):
    if precision not in (4, 6):
        raise ValueError("精度需为4或6")
    lon += 180; lat += 90
    f_lon = chr(int(lon / 20) + 65)
    f_lat = chr(int(lat / 10) + 65)
    lon %= 20; lat %= 10
    s_lon = str(int(lon / 2))
    s_lat = str(int(lat / 1))
    lon %= 2; lat %= 1
    result = f_lon + f_lat + s_lon + s_lat
    if precision == 6:
        result += chr(int(lon * 60 / 5) + 65) + chr(int(lat * 60 / 2.5) + 65)
    return result


R_KM = 6371.0

def _r(d): return d * math.pi / 180

def distance_bearing(lat1, lon1, lat2, lon2):
    φ1, φ2 = _r(lat1), _r(lat2)
    Δλ = _r(lon2 - lon1)
    a = math.sin(Δλ) * math.cos(φ2)
    b = math.cos(φ1) * math.sin(φ2) - math.sin(φ1) * math.cos(φ2) * math.cos(Δλ)
    bearing = (math.degrees(math.atan2(a, b)) + 360) % 360
    Δφ = _r(lat2 - lat1)
    a_hv = math.sin(Δφ/2)**2 + math.cos(φ1) * math.cos(φ2) * math.sin(Δλ/2)**2
    c = 2 * math.atan2(math.sqrt(a_hv), math.sqrt(1 - a_hv))
    dist_km = R_KM * c
    return {"km": round(dist_km, 1), "mi": round(dist_km * 0.621371, 1),
            "nmi": round(dist_km * 0.539957, 1), "bearing": round(bearing, 1)}


def dbm_to_watts(dbm): return 10 ** ((dbm - 30) / 10)

def watts_to_dbm(w): return 10 * math.log10(w) + 30

def watts_to_dbw(w): return 10 * math.log10(w)

def dbw_to_watts(dbw): return 10 ** (dbw / 10)


def swr_from_power(fw, rw):
    if fw <= 0: raise ValueError("正向功率需 > 0")
    ratio = math.sqrt(rw / fw)
    if ratio >= 1: return float("inf")
    return (1 + ratio) / (1 - ratio)


def swr_to_return_loss(swr):
    if swr <= 1: return float("inf")
    return -20 * math.log10((swr - 1) / (swr + 1))


def swr_to_reflected_power(swr, fw):
    rho = (swr - 1) / (swr + 1)
    return fw * rho ** 2


COAX_TYPES = {
    "RG174":  {100: 6.6, 200: 9.5, 400: 14.0, 1000: 23.0, 2400: 40.0},
    "RG58":   {100: 4.6, 200: 6.8, 400: 11.0, 1000: 20.0, 2400: 34.0},
    "RG213":  {100: 1.8, 200: 2.7, 400: 4.2,  1000: 7.5,  2400: 13.5},
    "RG8X":   {100: 2.9, 200: 4.2, 400: 6.5,  1000: 12.0, 2400: 22.0},
    "LMR240": {100: 2.1, 200: 3.0, 400: 4.6,  1000: 8.0,  2400: 14.2},
    "LMR400": {100: 1.2, 200: 1.7, 400: 2.7,  1000: 4.9,  2400: 8.9},
    "LMR600": {100: 0.8, 200: 1.1, 400: 1.8,  1000: 3.3,  2400: 6.0},
}


def coax_attenuation(cable, freq_mhz, length_m):
    if cable not in COAX_TYPES:
        raise ValueError(f"未知馈线: {cable}")
    data = COAX_TYPES[cable]
    freqs = sorted(data.keys())
    if freq_mhz <= freqs[0]:
        att = data[freqs[0]]
    elif freq_mhz >= freqs[-1]:
        att = data[freqs[-1]]
    else:
        for i in range(len(freqs) - 1):
            if freqs[i] <= freq_mhz <= freqs[i + 1]:
                ratio = (freq_mhz - freqs[i]) / (freqs[i + 1] - freqs[i])
                att = data[freqs[i]] + ratio * (data[freqs[i + 1]] - data[freqs[i]])
                break
    total = att * length_m / 100
    loss_pct = 100 * (1 - 10 ** (-total / 10))
    return {"cable": cable, "attenuation_db": round(total, 2),
            "per_100m_db": round(att, 2), "power_loss_pct": round(loss_pct, 1)}


Q_CODES = {
    "QRA": ("你台的名称是什么？", "我台的名称是......"),
    "QRB": ("你台离我台多远？", "我们相距约为..."),
    "QRG": ("我的准确频率是多少？", "你的准确频率是..."),
    "QRH": ("我的频率稳定吗？", "你的频率不稳定。"),
    "QRI": ("我的音调如何？", "你的音调(1.好 2.可变 3.差)"),
    "QRJ": ("我的信号小吗？", "你的信号小。"),
    "QRK": ("我的信号可辩度是多少？", "你的信号可辩度(1.差..5.很好)"),
    "QRL": ("你忙吗？", "我很忙，请不要打扰。"),
    "QRM": ("你受到他台干扰吗？", "他台干扰(1.无 2.稍有 3.中等 4.严重 5.极端)"),
    "QRN": ("你受到天电干扰吗？", "天电干扰(1.无 2.稍有 3.中等 4.严重 5.极端)"),
    "QRO": ("要我增加发信功率吗？", "请增加发信功率。"),
    "QRP": ("要降低发信机功率吗？", "请减低发信机功率。"),
    "QRQ": ("要我发得快些吗？", "请发快些。"),
    "QRS": ("要我发得慢一些吗？", "请发得慢一些(每分钟X字)。"),
    "QRT": ("要我停止拍发吗？", "请停止拍发。"),
    "QRU": ("你有什么发给我吗？", "我没有什么发给你。"),
    "QRV": ("你准备好了吗？", "我准备好了。"),
    "QRW": ("需要我转告吗？", "请转告。"),
    "QRX": ("你什么时候再呼叫我？", "我将在X点钟(用..频率)再呼叫您。"),
    "QRZ": ("谁在呼叫我？", "XX正在(用..频率)呼叫你。"),
    "QSA": ("我的信号强度怎样？", "信号强度:1.几乎收不到 2.弱 3.还好 4.好 5.很好"),
    "QSB": ("我的信号有衰落吗？", "你的信号有衰落。"),
    "QSD": ("我的发报有缺陷吗？", "你的发报有缺陷。"),
    "QSL": ("你能确认联络吗？", "我现在确认联络。"),
    "QSO": ("你能与XX直接或接转通信吗？", "我能和XX直接或经接转通信。"),
    "QSP": ("你能中转到...吗？", "我能中转到...。"),
    "QSU": ("能在(这个)频率回复吗？", "我将在此频率(或某频率)回复。"),
    "QSV": ("要我在此频率发一串V字吗？", "请在此频率发一串V字。"),
    "QSW": ("你将在此频率发吗？", "我将在此频率(或某频率)发。"),
    "QSX": ("你将在某频率收听吗？", "我将某频率收听。"),
    "QSY": ("要我改用别的频率拍发吗？", "请改用别的频率(用..频率)拍发。"),
    "QSZ": ("要我每组发两遍吗？", "请每组发两遍。"),
    "QTB": ("要我查对组数吗？", "请查对组数。"),
    "QTC": ("你有几份报要发？", "我有...份报要发。"),
    "QTH": ("你的地理位置在...？", "我的地理位置在..."),
    "QTR": ("你的标准时间是？", "我的标准时间是..."),
}

ENG_ABBREV = {
    "ABT": ("关于，大约", "About"),
    "ADR": ("地址", "Address"),
    "AGN": ("再，再一次", "Again"),
    "AHR": ("其他，另外", "Another"),
    "ANT": ("天线", "Antenna"),
    "AS": ("亚洲 / 稍等", "Asia / As"),
    "BCN": ("信标", "Beacon"),
    "BCNU": ("再见", "Be seeing you"),
    "BK": ("插入，打断", "Break"),
    "BURO": ("管理局，(QSL)卡片局", "Bureau"),
    "C": ("是（CW缩略语）", "Yes (CW abbreviation)"),
    "CFM": ("确认", "Confirm"),
    "CL": ("关机 / 呼叫", "Close / Call"),
    "CQ": ("普遍呼叫", "Call any station"),
    "CUAGN": ("再见到你", "See you again"),
    "CUL": ("再会", "See you later"),
    "CW": ("等幅电报", "Continuous Wave"),
    "DE": ("从（呼号前使用）", "From"),
    "DR": ("亲爱的", "Dear"),
    "DX": ("远距离通信", "Long distance"),
    "EL, ELE": ("天线单元", "Element"),
    "ES": ("和", "And"),
    "FB": ("太好了，很好的", "Fine business / Excellent"),
    "FM": ("调频", "Frequency Modulation"),
    "FR, FER": ("为了", "For"),
    "FREQ": ("频率", "Frequency"),
    "FRM": ("从", "From"),
    "GA": ("下午好 / 请继续", "Good afternoon / Go ahead"),
    "GB": ("再见", "Good bye"),
    "GD": ("好", "Good"),
    "GE": ("晚上好", "Good evening"),
    "GL": ("好运，祝好运", "Good luck"),
    "GLD": ("高兴", "Glad"),
    "GM": ("早安", "Good morning"),
    "GN": ("晚安", "Good night"),
    "GND": ("地面/地网", "Ground"),
    "GUD": ("好", "Good"),
    "HI": ("笑声（CW中用）", "Laughter in CW"),
    "HPE": ("希望", "Hope"),
    "HPY, HPI": ("幸福", "Happy"),
    "HR": ("这里 / 听到", "Here / Hear"),
    "HW": ("怎么样，如何", "How"),
    "IARU": ("国际业余无线电联盟", "International Amateur Radio Union"),
    "IC": ("集成电路", "Integrated Circuit"),
    "IF": ("中频", "Intermediate Frequency"),
    "K": ("请回答，请继续", "Go ahead"),
    "KN": ("特定台请回答", "Go ahead (specific station)"),
    "LID": ("差劲的操作员", "Poor operator"),
    "LSN": ("收听", "Listen"),
    "M": ("分钟 / 米", "Minute / Meter"),
    "MNI, MNY": ("许多", "Many"),
    "MR": ("先生", "Mister"),
    "MRS": ("太太", "Mistress"),
    "MSG": ("消息", "Message"),
    "MY": ("我的", "My"),
    "N": ("不，否定", "No, negative"),
    "NCS": ("网络控制电台", "Net Control Station"),
    "NIL": ("无/没事", "Nothing"),
    "NR": ("数目，编号", "Number"),
    "NW": ("现在", "Now"),
    "OB": ("老兄", "Old boy"),
    "OC": ("老友", "Old chap"),
    "OM": ("老朋友，老火腿", "Old man"),
    "OP": ("操作员，报务员", "Operator"),
    "PSE": ("请", "Please"),
    "PWR": ("功率", "Power"),
    "R": ("收到了，明白", "Roger / Received"),
    "RFI": ("无线电干扰", "Radio Frequency Interference"),
    "RIG": ("电台设备", "Station equipment"),
    "RMKS": ("记事，备注", "Remarks"),
    "RPRT": ("报告", "Report"),
    "RST": ("信号可辩度/强度/音调", "Readability Strength Tone"),
    "RX": ("接收机", "Receiver"),
    "SIG": ("信号", "Signal"),
    "SK": ("结束联络", "End of contact / 再见"),
    "SOS": ("呼救信号", "Save Our Souls"),
    "SRI": ("抱歉，对不起", "Sorry"),
    "SSB": ("单边带", "Single Side Band"),
    "STN": ("电台", "Station"),
    "SWL": ("短波收听者", "Short Wave Listener"),
    "TEMP": ("温度", "Temperature"),
    "TNX, TKS": ("谢谢", "Thanks"),
    "TU": ("谢谢你", "Thank you"),
    "TX": ("发射机", "Transmitter"),
    "U": ("你", "You"),
    "UR, URS": ("你的 / 你是", "Your / You are"),
    "UTC": ("协调世界时", "Coordinated Universal Time"),
    "VIA": ("经，由", "Via"),
    "VFO": ("可变频率振荡器", "Variable Frequency Oscillator"),
    "VY": ("非常，很", "Very"),
    "WKD, WK": ("工作 / 联络过", "Work / Worked"),
    "WPM": ("每分钟字数", "Words Per Minute"),
    "WX": ("天气", "Weather"),
    "XYL": ("妻子", "Ex-Young Lady"),
    "YL": ("小姐，女士", "Young Lady"),
}

NUM_ABBREV = {
    "73": ("致以美好祝愿", "Best regards (源自电报代码)"),
    "88": ("爱与吻", "Love and kisses (源自电报代码)"),
    "55": ("祝好运/成功了", "Good luck / 顺利完成"),
    "99": ("走开/别烦我", "Go away / 不欢迎"),
    "33": ("诚挚问候（给女士）", "Warm regards (to ladies)"),
    "44": ("来自儿童的问候", "Regards from children"),
    "22": ("一切顺利", "Everything OK"),
    "66": ("愉快的旅程", "Happy travels"),
    "11": ("（数字编码演示）", "Numeric code demonstration"),
    "599": ("最强信号", "Perfect signal (RST 599)"),
}

# ============================================================
# ToolTip 悬停提示
# ============================================================

class ToolTip:
    """为任意 widget 绑定悬停释义提示。"""
    def __init__(self, widget, text, delay=400):
        self.widget = widget
        self.text = text
        self.delay = delay
        self.tip_window = None
        self._after_id = None
        widget.bind("<Enter>", self._enter)
        widget.bind("<Leave>", self._leave)

    def _enter(self, event):
        self._after_id = self.widget.after(self.delay, self._show)

    def _leave(self, event):
        if self._after_id:
            self.widget.after_cancel(self._after_id)
            self._after_id = None
        self._hide()

    def _get_bg_color(self):
        try:
            default_bg = self.widget.winfo_toplevel().cget("bg")
            if default_bg and default_bg not in ("system", "", "SystemButtonFace"):
                return default_bg
        except Exception:
            pass
        try:
            style = ttk.Style()
            default_bg = style.configure(".", "background")
            if default_bg and default_bg not in ("", "SystemButtonFace"):
                return default_bg
        except Exception:
            pass
        return "#f0f0f0"

    def _show(self):
        if self.tip_window:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 4
        self.tip_window = tk.Toplevel(self.widget)
        self.tip_window.wm_overrideredirect(True)
        self.tip_window.wm_geometry(f"+{x}+{y}")
        bg = self._get_bg_color()
        label = tk.Label(self.tip_window, text=self.text, justify="left",
                         background=bg, foreground="#333333", relief="solid",
                         borderwidth=1, padx=8, pady=4, font=("Segoe UI", 9),
                         wraplength=360, anchor="w")
        label.pack()

    def _hide(self):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None


def add_tooltip(widget, text):
    return ToolTip(widget, text)


# ============================================================
# 通联日志
# ============================================================

LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ham_logs")
LOG_FILE = os.path.join(LOG_DIR, "qso_log.json")


def ensure_log_dir():
    os.makedirs(LOG_DIR, exist_ok=True)


def load_qsos():
    ensure_log_dir()
    if not os.path.exists(LOG_FILE):
        return []
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_qsos(qsos):
    ensure_log_dir()
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(qsos, f, ensure_ascii=False, indent=2)


CITY_COORDS = {
    # 中国主要城市
    "北京": (39.9042, 116.4074), "PEKING": (39.9042, 116.4074), "BEIJING": (39.9042, 116.4074),
    "上海": (31.2304, 121.4737), "SHANGHAI": (31.2304, 121.4737),
    "广州": (23.1291, 113.2644), "GUANGZHOU": (23.1291, 113.2644), "CANTON": (23.1291, 113.2644),
    "深圳": (22.5431, 114.0579), "SHENZHEN": (22.5431, 114.0579),
    "天津": (39.3434, 117.3616), "TIANJIN": (39.3434, 117.3616),
    "重庆": (29.4316, 106.9123), "CHONGQING": (29.4316, 106.9123),
    "杭州": (30.2741, 120.1551), "HANGZHOU": (30.2741, 120.1551),
    "南京": (32.0603, 118.7969), "NANJING": (32.0603, 118.7969),
    "成都": (30.5728, 104.0668), "CHENGDU": (30.5728, 104.0668),
    "武汉": (30.5928, 114.3055), "WUHAN": (30.5928, 114.3055),
    "西安": (34.3416, 108.9398), "XI'AN": (34.3416, 108.9398), "XIAN": (34.3416, 108.9398),
    "长沙": (28.2282, 112.9388), "CHANGSHA": (28.2282, 112.9388),
    "青岛": (36.0671, 120.3826), "QINGDAO": (36.0671, 120.3826),
    "大连": (38.9140, 121.6147), "DALIAN": (38.9140, 121.6147),
    "厦门": (24.4798, 118.0894), "XIAMEN": (24.4798, 118.0894), "AMOY": (24.4798, 118.0894),
    "苏州": (31.2990, 120.5853), "SUZHOU": (31.2990, 120.5853),
    "昆明": (25.0389, 102.7183), "KUNMING": (25.0389, 102.7183),
    "哈尔滨": (45.8038, 126.5350), "HARBIN": (45.8038, 126.5350),
    "福州": (26.0745, 119.2965), "FUZHOU": (26.0745, 119.2965),
    "郑州": (34.7466, 113.6254), "ZHENGZHOU": (34.7466, 113.6254),
    "济南": (36.6512, 116.9972), "JINAN": (36.6512, 116.9972),
    "沈阳": (41.8057, 123.4315), "SHENYANG": (41.8057, 123.4315),
    "合肥": (31.8206, 117.2272), "HEFEI": (31.8206, 117.2272),
    "南宁": (22.8170, 108.3665), "NANNING": (22.8170, 108.3665),
    "贵阳": (26.6470, 106.6302), "GUIYANG": (26.6470, 106.6302),
    "太原": (37.8706, 112.5489), "TAIYUAN": (37.8706, 112.5489),
    "南昌": (28.6829, 115.8582), "NANCHANG": (28.6829, 115.8582),
    "兰州": (36.0611, 103.8343), "LANZHOU": (36.0611, 103.8343),
    "拉萨": (29.6500, 91.1000), "LHASA": (29.6500, 91.1000),
    "乌鲁木齐": (43.8256, 87.6168), "URUMQI": (43.8256, 87.6168),
    "呼和浩特": (40.8422, 111.7499), "HOHHOT": (40.8422, 111.7499),
    "银川": (38.4863, 106.2325), "YINCHUAN": (38.4863, 106.2325),
    "西宁": (36.6171, 101.7802), "XINING": (36.6171, 101.7802),
    "石家庄": (38.0428, 114.5149), "SHIJIAZHUANG": (38.0428, 114.5149),
    "海口": (20.0310, 110.3460), "HAIKOU": (20.0310, 110.3460),
    "台北": (25.0330, 121.5654), "TAIPEI": (25.0330, 121.5654),
    "香港": (22.3193, 114.1694), "HONG KONG": (22.3193, 114.1694), "HONGKONG": (22.3193, 114.1694),
    "澳门": (22.1987, 113.5439), "MACAO": (22.1987, 113.5439),
    # 国际主要城市
    "TOKYO": (35.6762, 139.6503), "东京": (35.6762, 139.6503),
    "SEOUL": (37.5665, 126.9780), "首尔": (37.5665, 126.9780),
    "BANGKOK": (13.7563, 100.5018), "曼谷": (13.7563, 100.5018),
    "SINGAPORE": (1.3521, 103.8198), "新加坡": (1.3521, 103.8198),
    "KUALA LUMPUR": (3.1390, 101.6869), "吉隆坡": (3.1390, 101.6869),
    "JAKARTA": (-6.2088, 106.8456), "雅加达": (-6.2088, 106.8456),
    "MANILA": (14.5995, 120.9842), "马尼拉": (14.5995, 120.9842),
    "NEW DELHI": (28.6139, 77.2090), "新德里": (28.6139, 77.2090),
    "MUMBAI": (19.0760, 72.8777), "孟买": (19.0760, 72.8777),
    "DUBAI": (25.2048, 55.2708), "迪拜": (25.2048, 55.2708),
    "LONDON": (51.5074, -0.1278), "伦敦": (51.5074, -0.1278),
    "PARIS": (48.8566, 2.3522), "巴黎": (48.8566, 2.3522),
    "BERLIN": (52.5200, 13.4050), "柏林": (52.5200, 13.4050),
    "ROME": (41.9028, 12.4964), "罗马": (41.9028, 12.4964),
    "MADRID": (40.4168, -3.7038), "马德里": (40.4168, -3.7038),
    "MOSCOW": (55.7558, 37.6173), "莫斯科": (55.7558, 37.6173),
    "STOCKHOLM": (59.3293, 18.0686), "斯德哥尔摩": (59.3293, 18.0686),
    "OSLO": (59.9139, 10.7522), "奥斯陆": (59.9139, 10.7522),
    "HELSINKI": (60.1699, 24.9384), "赫尔辛基": (60.1699, 24.9384),
    "COPENHAGEN": (55.6761, 12.5683), "哥本哈根": (55.6761, 12.5683),
    "ATHENS": (37.9838, 23.7275), "雅典": (37.9838, 23.7275),
    "WARSAW": (52.2297, 21.0122), "华沙": (52.2297, 21.0122),
    "PRAGUE": (50.0755, 14.4378), "布拉格": (50.0755, 14.4378),
    "VIENNA": (48.2082, 16.3738), "维也纳": (48.2082, 16.3738),
    "BUDAPEST": (47.4979, 19.0402), "布达佩斯": (47.4979, 19.0402),
    "NEW YORK": (40.7128, -74.0060), "纽约": (40.7128, -74.0060),
    "WASHINGTON": (38.9072, -77.0369), "华盛顿": (38.9072, -77.0369),
    "LOS ANGELES": (34.0522, -118.2437), "洛杉矶": (34.0522, -118.2437),
    "CHICAGO": (41.8781, -87.6298), "芝加哥": (41.8781, -87.6298),
    "SAN FRANCISCO": (37.7749, -122.4194), "旧金山": (37.7749, -122.4194),
    "TORONTO": (43.6532, -79.3832), "多伦多": (43.6532, -79.3832),
    "VANCOUVER": (49.2827, -123.1207), "温哥华": (49.2827, -123.1207),
    "MEXICO CITY": (19.4326, -99.1332), "墨西哥城": (19.4326, -99.1332),
    "SAO PAULO": (-23.5505, -46.6333), "圣保罗": (-23.5505, -46.6333),
    "BUENOS AIRES": (-34.6037, -58.3816), "布宜诺斯艾利斯": (-34.6037, -58.3816),
    "SYDNEY": (-33.8688, 151.2093), "悉尼": (-33.8688, 151.2093),
    "MELBOURNE": (-37.8136, 144.9631), "墨尔本": (-37.8136, 144.9631),
    "AUCKLAND": (-36.8485, 174.7633), "奥克兰": (-36.8485, 174.7633),
    "CAPE TOWN": (-33.9249, 18.4241), "开普敦": (-33.9249, 18.4241),
    "CAIRO": (30.0444, 31.2357), "开罗": (30.0444, 31.2357),
    "JOHANNESBURG": (-26.2041, 28.0473), "约翰内斯堡": (-26.2041, 28.0473),
    "ISTANBUL": (41.0082, 28.9784), "伊斯坦布尔": (41.0082, 28.9784),
    "ANCHORAGE": (61.2181, -149.9003),
    "HONOLULU": (21.3069, -157.8583), "火奴鲁鲁": (21.3069, -157.8583),
}


# ============================================================
# GUI 应用
# ============================================================

class HamToolboxGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("HAM Radio Toolbox - 业余无线电工具箱")
        self.root.geometry("920x680")
        self.root.minsize(860, 620)

        style = ttk.Style()
        style.theme_use("vista" if "vista" in style.theme_names() else "clam")

        main_frame = ttk.Frame(root, padding="8")
        main_frame.pack(fill="both", expand=True)

        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill="both", expand=True)

        self.build_freq_tab(notebook)
        self.build_rf_tab(notebook)
        self.build_grid_tab(notebook)
        self.build_log_tab(notebook)
        self.build_qcode_tab(notebook)
        self.build_cw_tab(notebook)
        self.build_utils_tab(notebook)

        status = ttk.Label(main_frame, text="就绪", relief="sunken", anchor="w")
        status.pack(fill="x", pady=(4, 0))
        self.status = status

        self.update_clock()

    def set_status(self, msg):
        self.status.config(text=msg)

    def _add_result_box(self, parent):
        text = scrolledtext.ScrolledText(parent, height=10, wrap="word",
                                          font=("Consolas", 10), bg="#f5f5f5")
        text.bind("<Key>", lambda e: "break")
        text.bind("<Button-3>", lambda e: "break")
        return text

    def _clear(self, w):
        w.delete("1.0", "end")

    def _bind_scrollwheel(self, canvas):
        """Bind mouse wheel scrolling to a canvas and all its children."""
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        def _bind(widget):
            widget.bind("<MouseWheel>", _on_mousewheel)
            for child in widget.winfo_children():
                _bind(child)
        canvas.bind("<Enter>", lambda e: _bind(canvas))
        canvas.bind("<Leave>", lambda e: canvas.unbind("<MouseWheel>"))

    # ============================================================
    # 1. 频率/频段
    # ============================================================

    def build_freq_tab(self, notebook):
        tab = ttk.Frame(notebook, padding="12")
        notebook.add(tab, text="频率/频段")

        search_frame = ttk.Frame(tab)
        search_frame.grid(row=0, column=0, sticky="w")

        self.search_mode = tk.StringVar(value="频率")
        mode_cb = ttk.Combobox(search_frame, textvariable=self.search_mode, values=["频率", "区间"],
                               state="readonly", width=5)
        mode_cb.grid(row=0, column=0, padx=(0, 4))
        mode_cb.bind("<<ComboboxSelected>>", self._on_search_mode_change)

        self.freq_entry = ttk.Entry(search_frame, width=12)
        self.freq_entry.grid(row=0, column=1, padx=(0, 4))
        self.freq_entry.bind("<Return>", lambda e: self.freq_query_or_range())
        add_tooltip(self.freq_entry, "输入无线电频率数值")

        ttk.Label(search_frame, text=" ~ ").grid(row=0, column=2)
        self.freq_entry2 = ttk.Entry(search_frame, width=12, state="disabled")
        self.freq_entry2.grid(row=0, column=3, padx=(0, 4))
        self.freq_entry2.bind("<Return>", lambda e: self.freq_query_or_range())
        add_tooltip(self.freq_entry2, "区间搜索上限频率 (选择\"区间\"模式后启用)")

        self.freq_unit = tk.StringVar(value="MHz")
        unit_cb = ttk.Combobox(search_frame, textvariable=self.freq_unit, values=["kHz", "MHz", "GHz"],
                               state="readonly", width=7)
        unit_cb.grid(row=0, column=4)

        btn_frame = ttk.Frame(tab)
        btn_frame.grid(row=0, column=2, padx=(8, 0))
        ttk.Button(btn_frame, text="查询", width=8, command=self.freq_query_or_range).pack(side="left", padx=2)
        ttk.Button(btn_frame, text="清空", width=8, command=self._freq_clear).pack(side="left", padx=2)

        self.freq_result = self._add_result_box(tab)
        self.freq_result.grid(row=2, column=0, columnspan=3, sticky="nsew", pady=(8, 0))
        tab.columnconfigure(1, weight=1)
        tab.rowconfigure(2, weight=1)

        ttk.Label(tab, text="频段分配表 (中国业余无线电执照要求):", font=("Segoe UI", 9, "bold")).grid(row=3, column=0, columnspan=3, sticky="w", pady=(8, 2))
        table_frame = ttk.Frame(tab)
        table_frame.grid(row=4, column=0, columnspan=3, sticky="nsew")
        tab.rowconfigure(4, weight=1)

        cols = ("band", "cat", "low", "high", "svc")
        tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=10)
        tree.heading("band", text="波段")
        tree.heading("cat", text="频段类型")
        tree.heading("low", text="下限 (MHz)")
        tree.heading("high", text="上限 (MHz)")
        tree.heading("svc", text="业余业务类型")
        tree.column("band", width=50, anchor="center")
        tree.column("cat", width=85, anchor="center")
        tree.column("low", width=80, anchor="center")
        tree.column("high", width=80, anchor="center")
        tree.column("svc", width=120, anchor="center")
        for b in BANDS:
            tree.insert("", "end", values=(b["name"], f"{b['cat']}{CAT_CN[b['cat']]}",
                        b["f_low"], b["f_high"], b["svc"]))

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        self.band_tree = tree

        def _on_band_select(event):
            sel = tree.selection()
            if not sel:
                return
            vals = tree.item(sel[0])["values"]
            low, high = float(vals[2]), float(vals[3])
            self.freq_entry.delete(0, "end")
            self.freq_entry.insert(0, f"{low}")
            self.freq_entry2.config(state="normal")
            self.freq_entry2.delete(0, "end")
            self.freq_entry2.insert(0, f"{high}")
            self.search_mode.set("区间")
            self.freq_unit.set("MHz")
            self.freq_range_search()
        tree.bind("<Double-1>", _on_band_select)

        license_summary = ttk.Label(tab,
            text="A类: 30-3000MHz ≤25W  |  B类: 30MHz以下 <15W (2024.3.1前取得证书 ≤100W), 30MHz以上 ≤25W  |  C类: 30MHz以下 ≤1000W, 30MHz以上 ≤25W",
            font=("Segoe UI", 9), foreground="#555")
        license_summary.grid(row=5, column=0, columnspan=3, sticky="w", pady=(4, 0))

        ttk.Separator(tab, orient="horizontal").grid(row=6, column=0, columnspan=3, sticky="ew", pady=8)
        ttk.Label(tab, text="通信模式参考", font=("Segoe UI", 10, "bold")).grid(row=7, column=0, columnspan=3, sticky="w", pady=(0, 4))

        canvas = tk.Canvas(tab, highlightthickness=0)
        modes_scrollbar = ttk.Scrollbar(tab, orient="vertical", command=canvas.yview)
        scroll_frame = ttk.Frame(canvas)
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=modes_scrollbar.set)
        canvas.grid(row=8, column=0, columnspan=3, sticky="nsew")
        modes_scrollbar.grid(row=8, column=3, sticky="ns")
        tab.rowconfigure(8, weight=1)

        self._bind_scrollwheel(canvas)

        modes_data = [
            ("模拟模式", [
                ("CW (Continuous Wave)", "等幅报/摩尔斯电码", "最古老的无线电通信方式，使用通断键发送摩尔斯电码。带宽极窄（约50Hz），通信效率高，适合弱信号通信。"),
                ("SSB (Single Sideband)", "单边带", "调幅的改进形式，只传输一个边带，抑制载波和另一边带。带宽约2.7kHz，是HF话音通信的主要模式。下边带(LSB)用于7MHz及以下，上边带(USB)用于10MHz及以上。"),
                ("AM (Amplitude Modulation)", "调幅", "传统的模拟调制方式，同时传输载波和两个边带。带宽约6kHz，音质较好但效率低，主要用于短波广播和老式设备。"),
                ("FM (Frequency Modulation)", "调频", "频率调制，抗干扰能力强，音质好。带宽约12.5kHz（窄带FM）或25kHz（宽带FM）。主要用于VHF/UHF simplex通信和中继台。"),
            ]),
            ("数字模式", [
                ("FT8", "弱信号数字模式", "由WSJT团队开发，极短的传输时间（15秒）和极高的灵敏度（-24dB SNR）。广泛用于DX通信和比赛，频率占用约50Hz。"),
                ("FT4", "快速数字模式", "FT8的改进版，传输时间缩短至7.5秒，适合比赛和快速交换。速率比FT8快一倍。"),
                ("PSK31", "相移键控", "带宽仅31.25Hz的窄带数字模式，适合实时键盘聊天。由Peter Martinez (G3LTF)开发。"),
                ("RTTY (Radio Teletype)", "无线电电传", "最早的数字模式之一，使用频移键控（FSK）。带宽约250Hz，广泛用于比赛和DX通信。"),
                ("JT65", "弱信号模式", "为EME（月面反射）通信设计，传输时间60秒。现已大部分被FT8取代。"),
                ("WSPR (Weak Signal Propagation Reporter)", "弱信号传播报告", "用于传播监测和信标，传输时间约2分钟。可自动报告接收信号到网络。"),
                ("MSK144", "最小频移键控", "用于流星散射通信的快速数字模式，传输时间约0.5秒。"),
                ("Olivia", "多频移键控", "抗多径和衰落能力强，适合困难传播条件。带宽可变（通常500Hz-2kHz）。"),
                ("Packet", "分组数据", "基于AX.25协议的分组数据通信，用于APRS和BBS等应用。"),
            ]),
            ("数字语音模式", [
                ("D-STAR", "数字语音", "由Icom开发的数字语音标准，支持语音和数据。使用AMBE+2声码器。"),
                ("DMR (Digital Mobile Radio)", "数字移动无线电", "ETSI标准的数字语音协议，支持双时隙TDMA。广泛用于业余无线电和商业通信。"),
                ("C4FM (Continuous 4-level FM)", "连续四电平调频", "Yaesu系统融合（System Fusion）使用的调制方式，支持语音和数据。"),
            ]),
            ("其他模式", [
                ("窄带 (Narrowband)", "窄带模式", "带宽≤500Hz的模式总称，包括CW、PSK31、FT8等。适合弱信号和频谱拥挤环境。"),
                ("话音 (Phone)", "语音通信", "使用话筒进行语音通信的模式总称，主要包括SSB、FM、AM等。"),
                ("信标 (Beacon)", "信标台", "自动发射识别信号的电台，用于传播研究和天线测试。通常位于频段边缘。"),
                ("卫星 (Satellite)", "业余卫星通信", "通过业余无线电卫星进行通信。卫星通常工作在V/U模式（VHF上行/UHF下行）或L/S模式。"),
                ("APRS (Automatic Packet Reporting System)", "自动位置报告系统", "基于分组数据的实时位置跟踪和消息系统，广泛使用144.390MHz（美洲）或144.800MHz（欧洲/亚洲）。"),
            ]),
        ]
        for category, modes in modes_data:
            ttk.Label(scroll_frame, text=category, font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(6, 2))
            for abbr, name, desc in modes:
                frame = ttk.Frame(scroll_frame)
                frame.pack(fill="x", pady=1)
                ttk.Label(frame, text=abbr, font=("Segoe UI", 9, "bold"), width=28, anchor="w").pack(side="left")
                ttk.Label(frame, text=name, width=16, anchor="w").pack(side="left")
                ttk.Label(frame, text=desc, wraplength=480, justify="left").pack(side="left", fill="x", expand=True)

    def freq_query(self):
        try:
            val = float(self.freq_entry.get())
        except ValueError:
            messagebox.showerror("错误", "请输入有效频率数值")
            return
        unit = self.freq_unit.get()
        unit_to_mhz = {"kHz": 0.001, "MHz": 1, "GHz": 1000}
        f_mhz = val * unit_to_mhz[unit]
        b = freq_to_band(f_mhz)
        cat = freq_to_spectrum_cat(f_mhz)
        wl = wavelength(f_mhz)
        self._clear(self.freq_result)
        if not b:
            self.freq_result.tag_configure("red", foreground="red")
            self.freq_result.insert("end", "⚠ 非业余业务频率\n", "red")
        self.freq_result.insert("end", f"频率: {val} {unit}\n")
        if b:
            self.freq_result.insert("end", f"频段: {b['name']} ({b['cat']}{CAT_CN[b['cat']]})\n")
            self.freq_result.insert("end", f"业余业务类型: {b['svc']}\n")
            self.freq_result.insert("end", f"可用执照: {b['license']}\n")
        else:
            self.freq_result.insert("end", f"频段: {cat}\n")
        if wl >= 1:
            self.freq_result.insert("end", f"波长: {wl:.2f} m\n")
        else:
            self.freq_result.insert("end", f"波长: {wl*100:.1f} cm\n")
        f_khz = f_mhz * 1000
        f_ghz = f_mhz / 1000
        self.freq_result.insert("end", f"\n等效频率: {f_mhz:.6f} MHz = {f_khz:.3f} kHz = {f_ghz:.6f} GHz")
        self.set_status(f"查询完成: {f_mhz} MHz -> {b['name'] if b else cat}")

    def freq_query_or_range(self):
        if self.search_mode.get() == "区间":
            self.freq_range_search()
        else:
            self.freq_query()

    def _freq_clear(self):
        self._clear(self.freq_result)
        self.freq_entry.delete(0, "end")
        self.freq_entry2.delete(0, "end")
        self.freq_entry2.config(state="disabled")
        self.search_mode.set("频率")

    def _on_search_mode_change(self, event=None):
        if self.search_mode.get() == "区间":
            self.freq_entry2.config(state="normal")
        else:
            self.freq_entry2.delete(0, "end")
            self.freq_entry2.config(state="disabled")

    def freq_range_search(self):
        try:
            low = float(self.freq_entry.get())
            high = float(self.freq_entry2.get())
        except ValueError:
            messagebox.showerror("错误", "请输入有效频率数值")
            return
        unit = self.freq_unit.get()
        unit_to_mhz = {"kHz": 0.001, "MHz": 1, "GHz": 1000}
        low_mhz = low * unit_to_mhz[unit]
        high_mhz = high * unit_to_mhz[unit]
        if low_mhz > high_mhz:
            low_mhz, high_mhz = high_mhz, low_mhz
        unit_label = {"kHz": "kHz", "MHz": "MHz", "GHz": "GHz"}
        self._clear(self.freq_result)
        self.freq_result.insert("end", f"区间: {low} {unit_label[unit]} ~ {high} {unit_label[unit]}\n")
        self.freq_result.insert("end", f"      ({low_mhz:.6f} MHz ~ {high_mhz:.6f} MHz)\n\n")
        found = False
        for b in BANDS:
            if b["f_low"] <= high_mhz and b["f_high"] >= low_mhz:
                found = True
                self.freq_result.insert("end", f"=== {b['name']} ({b['cat']}{CAT_CN[b['cat']]}) ===\n")
                self.freq_result.insert("end", f"频率范围: {b['f_low']} ~ {b['f_high']} MHz\n")
                self.freq_result.insert("end", f"业余业务类型: {b['svc']}\n")
                self.freq_result.insert("end", f"可用执照: {b['license']}\n")
                wl_low = wavelength(b["f_high"])
                wl_high = wavelength(b["f_low"])
                if wl_low >= 1:
                    self.freq_result.insert("end", f"波长范围: {wl_high:.2f} ~ {wl_low:.2f} m\n")
                else:
                    self.freq_result.insert("end", f"波长范围: {wl_high*100:.1f} ~ {wl_low*100:.1f} cm\n")
                low_khz = b["f_low"] * 1000
                high_khz = b["f_high"] * 1000
                low_ghz = b["f_low"] / 1000
                high_ghz = b["f_high"] / 1000
                self.freq_result.insert("end", f"等效: {b['f_low']} ~ {b['f_high']} MHz = {low_khz:.3f} ~ {high_khz:.3f} kHz = {low_ghz:.6f} ~ {high_ghz:.6f} GHz\n")
                self.freq_result.insert("end", "\n")
        if not found:
            self.freq_result.insert("end", "该区间未覆盖任何业余频段\n")
        self.set_status(f"区间搜索完成: {low_mhz} ~ {high_mhz} MHz")

    # ============================================================
    # 2. 射频工具
    # ============================================================

    def build_rf_tab(self, notebook):
        outer = ttk.Frame(notebook, padding="12")
        notebook.add(outer, text="射频工具")
        outer.columnconfigure(0, weight=1)
        outer.rowconfigure(0, weight=1)

        canvas = tk.Canvas(outer, highlightthickness=0, borderwidth=0)
        scrollbar = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        inner = ttk.Frame(canvas)
        inner.columnconfigure(0, weight=1)
        canvas.create_window((0, 0), window=inner, anchor="nw", tags="inner")

        def _on_rf_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        inner.bind("<Configure>", _on_rf_configure)
        canvas.bind("<Configure>", lambda e: canvas.itemconfig("inner", width=e.width))

        self._bind_scrollwheel(canvas)

        row = 0

        # ----- 天线计算 -----
        ttk.Label(inner, text="天线计算", font=("Segoe UI", 11, "bold")).grid(row=row, column=0, sticky="w", pady=(0, 4))
        row += 1
        ant_f = ttk.Frame(inner)
        ant_f.grid(row=row, column=0, sticky="ew", pady=2)
        row += 1
        ttk.Label(ant_f, text="频率 (MHz):").pack(side="left")
        self.ant_freq = ttk.Entry(ant_f, width=12)
        self.ant_freq.pack(side="left", padx=4)
        self.ant_freq.bind("<Return>", lambda e: self.antenna_calc())
        add_tooltip(self.ant_freq, "天线中心频率，单位 MHz\n例: 14.150 (20m 段), 7.050 (40m 段)")
        ttk.Button(ant_f, text="计算", width=6, command=self.antenna_calc).pack(side="left", padx=2)
        ttk.Button(ant_f, text="清空", width=6, command=lambda: self._clear(self.ant_result)).pack(side="left", padx=2)
        self.ant_result = self._add_result_box(inner)
        self.ant_result.configure(height=4)
        self.ant_result.grid(row=row, column=0, sticky="ew", pady=2)
        row += 1

        ttk.Separator(inner, orient="horizontal").grid(row=row, column=0, sticky="ew", pady=8)
        row += 1

        # ----- 功率转换 -----
        ttk.Label(inner, text="功率转换", font=("Segoe UI", 11, "bold")).grid(row=row, column=0, sticky="w", pady=(0, 4))
        row += 1
        pow_f = ttk.Frame(inner)
        pow_f.grid(row=row, column=0, sticky="ew", pady=2)
        row += 1
        ttk.Label(pow_f, text="数值:").pack(side="left")
        self.pow_val = ttk.Entry(pow_f, width=12)
        self.pow_val.pack(side="left", padx=4)
        self.pow_val.bind("<Return>", lambda e: self.power_convert())
        add_tooltip(self.pow_val, "输入功率数值\n根据所选单位进行转换")
        ttk.Button(pow_f, text="转换", width=6, command=self.power_convert).pack(side="left", padx=2)
        self.pow_unit = tk.StringVar(value="W")
        radio_f = ttk.Frame(inner)
        radio_f.grid(row=row, column=0, sticky="w", pady=2)
        row += 1
        ttk.Radiobutton(radio_f, text="W → dBm/dBW", variable=self.pow_unit, value="W").pack(side="left", padx=2)
        ttk.Radiobutton(radio_f, text="dBm → W", variable=self.pow_unit, value="dBm").pack(side="left", padx=2)
        ttk.Radiobutton(radio_f, text="dBW → W", variable=self.pow_unit, value="dBW").pack(side="left", padx=2)
        self.pow_result = self._add_result_box(inner)
        self.pow_result.configure(height=3)
        self.pow_result.grid(row=row, column=0, sticky="ew", pady=2)
        row += 1

        ttk.Separator(inner, orient="horizontal").grid(row=row, column=0, sticky="ew", pady=8)
        row += 1

        # ----- SWR 计算 -----
        ttk.Label(inner, text="SWR 计算", font=("Segoe UI", 11, "bold")).grid(row=row, column=0, sticky="w", pady=(0, 4))
        row += 1
        swr_f1 = ttk.Frame(inner)
        swr_f1.grid(row=row, column=0, sticky="ew", pady=2)
        row += 1
        ttk.Label(swr_f1, text="正向功率 (W):").pack(side="left")
        self.swr_fw = ttk.Entry(swr_f1, width=10)
        self.swr_fw.pack(side="left", padx=4)
        add_tooltip(self.swr_fw, "发射机输出到天线端的正向功率 (瓦)")
        ttk.Label(swr_f1, text="反射功率 (W):").pack(side="left")
        self.swr_rw = ttk.Entry(swr_f1, width=10)
        self.swr_rw.pack(side="left", padx=4)
        add_tooltip(self.swr_rw, "天线反射回发射机的功率 (瓦)")
        ttk.Button(swr_f1, text="由功率→SWR", width=12, command=self.swr_from_power).pack(side="left", padx=4)

        swr_f2 = ttk.Frame(inner)
        swr_f2.grid(row=row, column=0, sticky="ew", pady=2)
        row += 1
        ttk.Label(swr_f2, text="SWR:").pack(side="left")
        self.swr_val = ttk.Entry(swr_f2, width=8)
        self.swr_val.pack(side="left", padx=4)
        add_tooltip(self.swr_val, "驻波比，范围 ≥ 1\n1.0 为理想匹配")
        ttk.Label(swr_f2, text="正向功率 (W):").pack(side="left")
        self.swr_fw2 = ttk.Entry(swr_f2, width=10)
        self.swr_fw2.pack(side="left", padx=4)
        add_tooltip(self.swr_fw2, "发射机输出功率 (瓦)")
        ttk.Button(swr_f2, text="由SWR→反射功率", width=14, command=self.swr_to_reflect).pack(side="left", padx=4)

        self.swr_result = self._add_result_box(inner)
        self.swr_result.configure(height=3)
        self.swr_result.grid(row=row, column=0, sticky="ew", pady=2)
        row += 1

        ttk.Separator(inner, orient="horizontal").grid(row=row, column=0, sticky="ew", pady=8)
        row += 1

        # ----- 馈线损耗 -----
        ttk.Label(inner, text="馈线损耗", font=("Segoe UI", 11, "bold")).grid(row=row, column=0, sticky="w", pady=(0, 4))
        row += 1
        coax_f = ttk.Frame(inner)
        coax_f.grid(row=row, column=0, sticky="ew", pady=2)
        row += 1
        ttk.Label(coax_f, text="型号:").pack(side="left")
        self.coax_type = ttk.Combobox(coax_f, values=list(COAX_TYPES.keys()), state="readonly", width=10)
        self.coax_type.set("LMR400")
        self.coax_type.pack(side="left", padx=4)
        add_tooltip(self.coax_type, "同轴电缆型号\n不同型号衰减特性不同")
        ttk.Label(coax_f, text="频率 (MHz):").pack(side="left")
        self.coax_freq = ttk.Entry(coax_f, width=10)
        self.coax_freq.pack(side="left", padx=4)
        add_tooltip(self.coax_freq, "工作频率，单位 MHz\n频率越高衰减越大")
        ttk.Label(coax_f, text="长度 (m):").pack(side="left")
        self.coax_len = ttk.Entry(coax_f, width=8)
        self.coax_len.pack(side="left", padx=4)
        add_tooltip(self.coax_len, "馈线实际长度 (米)")
        ttk.Button(coax_f, text="计算", width=6, command=self.coax_calc).pack(side="left", padx=2)

        ttk.Label(inner, text="常见馈线衰减参考 (dB/100m):", font=("Segoe UI", 9, "bold")).grid(row=row, column=0, sticky="w", pady=(8, 2))
        row += 1
        cols = ("cable", "f100", "f400", "f1000")
        coax_tree = ttk.Treeview(inner, columns=cols, show="headings", height=5)
        coax_tree.heading("cable", text="型号")
        coax_tree.heading("f100", text="100 MHz")
        coax_tree.heading("f400", text="400 MHz")
        coax_tree.heading("f1000", text="1000 MHz")
        coax_tree.column("cable", width=80, anchor="center")
        coax_tree.column("f100", width=80, anchor="center")
        coax_tree.column("f400", width=80, anchor="center")
        coax_tree.column("f1000", width=80, anchor="center")
        for name, data in COAX_TYPES.items():
            coax_tree.insert("", "end", values=(name, data.get(100, "-"), data.get(400, "-"), data.get(1000, "-")))
        coax_tree.grid(row=row, column=0, sticky="ew", pady=2)
        row += 1

        self.coax_result = self._add_result_box(inner)
        self.coax_result.configure(height=3)
        self.coax_result.grid(row=row, column=0, sticky="ew", pady=2)
        row += 1

        inner.rowconfigure(1, weight=1)

    def antenna_calc(self):
        try:
            f = float(self.ant_freq.get())
        except ValueError:
            messagebox.showerror("错误", "请输入有效频率数值")
            return
        dip = dipole_length(f)
        qw = quarter_wave_length(f)
        self._clear(self.ant_result)
        self.ant_result.insert("end", f"频率: {f} MHz\n\n")
        self.ant_result.insert("end", "--- 半波偶极天线 ---\n")
        self.ant_result.insert("end", f"总长度 : {dip['total_m']:.2f} m  ({dip['total_ft']:.2f} ft)\n")
        self.ant_result.insert("end", f"每臂长 : {dip['per_leg_m']:.2f} m  ({dip['per_leg_ft']:.2f} ft)\n\n")
        self.ant_result.insert("end", "--- 四分之一波长垂直 ---\n")
        self.ant_result.insert("end", f"总长度 : {qw['total_m']:.2f} m  ({qw['total_ft']:.2f} ft)\n")
        self.set_status(f"天线计算完成: {f} MHz")

    def power_convert(self):
        try:
            v = float(self.pow_val.get())
        except ValueError:
            messagebox.showerror("错误", "请输入有效数值")
            return
        self._clear(self.pow_result)
        u = self.pow_unit.get()
        if u == "W":
            self.pow_result.insert("end", f"{v} W\n")
            self.pow_result.insert("end", f"= {watts_to_dbm(v):.2f} dBm\n")
            self.pow_result.insert("end", f"= {watts_to_dbw(v):.2f} dBW\n")
        elif u == "dBm":
            self.pow_result.insert("end", f"{v} dBm\n= {dbm_to_watts(v):.6f} W\n")
        else:
            self.pow_result.insert("end", f"{v} dBW\n= {dbw_to_watts(v):.6f} W\n")
        self.set_status(f"功率转换完成")

    def swr_from_power(self):
        try:
            fw, rw = float(self.swr_fw.get()), float(self.swr_rw.get())
        except ValueError:
            messagebox.showerror("错误", "请输入有效数值")
            return
        swr = swr_from_power(fw, rw)
        rl = swr_to_return_loss(swr)
        self._clear(self.swr_result)
        self.swr_result.insert("end", f"正向功率: {fw} W\n")
        self.swr_result.insert("end", f"反射功率: {rw} W\n")
        self.swr_result.insert("end", f"SWR = {swr:.2f}:1\n")
        self.swr_result.insert("end", f"回波损耗 = {rl:.1f} dB\n")
        self.set_status(f"SWR = {swr:.2f}:1")

    def swr_to_reflect(self):
        try:
            swr, fw = float(self.swr_val.get()), float(self.swr_fw2.get())
        except ValueError:
            messagebox.showerror("错误", "请输入有效数值")
            return
        rw = swr_to_reflected_power(swr, fw)
        rl = swr_to_return_loss(swr)
        self._clear(self.swr_result)
        self.swr_result.insert("end", f"SWR = {swr}:1\n")
        self.swr_result.insert("end", f"正向功率: {fw} W\n")
        self.swr_result.insert("end", f"反射功率: {rw:.2f} W\n")
        self.swr_result.insert("end", f"回波损耗 = {rl:.1f} dB\n")
        self.set_status(f"反射功率 = {rw:.2f} W")

    def coax_calc(self):
        cable = self.coax_type.get()
        try:
            freq, length = float(self.coax_freq.get()), float(self.coax_len.get())
        except ValueError:
            messagebox.showerror("错误", "请输入有效频率和长度数值")
            return
        try:
            r = coax_attenuation(cable, freq, length)
        except ValueError as e:
            messagebox.showerror("错误", str(e))
            return
        self._clear(self.coax_result)
        self.coax_result.insert("end", f"馈线: {r['cable']}\n")
        self.coax_result.insert("end", f"频率: {freq} MHz\n")
        self.coax_result.insert("end", f"长度: {length} m\n")
        self.coax_result.insert("end", f"总衰减: {r['attenuation_db']} dB\n")
        self.coax_result.insert("end", f"每100m: {r['per_100m_db']} dB\n")
        self.coax_result.insert("end", f"功率损耗: ~{r['power_loss_pct']}%\n")
        self.set_status(f"馈线损耗计算完成")

    # ============================================================
    # 3. 网格坐标
    # ============================================================

    def build_grid_tab(self, notebook):
        tab = ttk.Frame(notebook, padding="12")
        notebook.add(tab, text="区域")

        ttk.Label(tab, text="经纬度 → 网格", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, columnspan=3, sticky="w")
        ttk.Label(tab, text="纬度:").grid(row=1, column=0, sticky="w")
        self.lat_in = ttk.Entry(tab, width=16)
        self.lat_in.grid(row=1, column=1, sticky="w")
        add_tooltip(self.lat_in, "十进制纬度，北正南负\n例: 39.9042 (北京)")
        ttk.Label(tab, text="经度:").grid(row=2, column=0, sticky="w")
        self.lon_in = ttk.Entry(tab, width=16)
        self.lon_in.grid(row=2, column=1, sticky="w")
        add_tooltip(self.lon_in, "十进制经度，东正西负\n例: 116.4074 (北京)")
        btn_frame_ll = ttk.Frame(tab)
        btn_frame_ll.grid(row=1, column=2, rowspan=2, padx=(8, 0))
        ttk.Button(btn_frame_ll, text="转换", width=8, command=self.ll_to_grid).pack(side="top", pady=1)

        ttk.Label(tab, text="网格 → 经纬度", font=("Segoe UI", 9, "bold")).grid(row=3, column=0, columnspan=3, sticky="w", pady=(10, 2))
        ttk.Label(tab, text="网格 (如 OM89):").grid(row=4, column=0, sticky="w", padx=(0, 8))
        self.grid_in = ttk.Entry(tab, width=16)
        self.grid_in.grid(row=4, column=1, sticky="w")
        self.grid_in.bind("<Return>", lambda e: self.grid_to_ll())
        add_tooltip(self.grid_in, "Maidenhead 网格定位符\n支持 4 位 (如 OM89) 或 6 位 (如 OM89MM)")
        ttk.Button(tab, text="转换", width=8, command=self.grid_to_ll).grid(row=4, column=2, padx=(8, 0))

        ttk.Label(tab, text="网格间距离/方位", font=("Segoe UI", 9, "bold")).grid(row=5, column=0, columnspan=3, sticky="w", pady=(10, 2))
        ttk.Label(tab, text="网格1:").grid(row=6, column=0, sticky="w")
        self.dist_g1 = ttk.Entry(tab, width=12)
        self.dist_g1.grid(row=6, column=1, sticky="w")
        self.dist_g1.bind("<Return>", lambda e: self.grid_distance())
        add_tooltip(self.dist_g1, "起始 Maidenhead 网格\n如 OM89")
        ttk.Label(tab, text="网格2:").grid(row=7, column=0, sticky="w")
        self.dist_g2 = ttk.Entry(tab, width=12)
        self.dist_g2.grid(row=7, column=1, sticky="w")
        self.dist_g2.bind("<Return>", lambda e: self.grid_distance())
        add_tooltip(self.dist_g2, "目标 Maidenhead 网格\n如 FN30")
        ttk.Button(tab, text="计算", width=8, command=self.grid_distance).grid(row=6, column=2, rowspan=2, padx=(8, 0))

        self.grid_result = self._add_result_box(tab)
        self.grid_result.grid(row=8, column=0, columnspan=3, sticky="ew", pady=(4, 0))
        self.grid_result.configure(height=3)

        img_outer = ttk.Frame(tab)
        img_outer.grid(row=9, column=0, columnspan=3, sticky="nsew", pady=(8, 0))
        tab.columnconfigure(1, weight=1)
        tab.rowconfigure(9, weight=1)

        img_canvas = tk.Canvas(img_outer, highlightthickness=0)
        img_scrollbar = ttk.Scrollbar(img_outer, orient="vertical", command=img_canvas.yview)
        img_canvas.configure(yscrollcommand=img_scrollbar.set)
        img_canvas.pack(side="left", fill="both", expand=True)
        img_scrollbar.pack(side="right", fill="y")

        img_frame = ttk.Frame(img_canvas)
        img_frame.columnconfigure(0, weight=1)
        img_canvas.create_window((0, 0), window=img_frame, anchor="nw")

        self._bind_scrollwheel(img_canvas)

        self._grid_img_paths = [
            r"C:\Users\games\Downloads\wxd\2013_ITU_CQ_WorldMaps-1.jpg",
            r"C:\Users\games\Downloads\wxd\2013_ITU_CQ_WorldMaps-2.jpg",
        ]
        self._grid_img_orig = []
        self._grid_img_labels = []
        self._grid_img_photos = []

        titles = ["CQ全球分区图", "ITU全球分区图"]
        for i, path in enumerate(self._grid_img_paths):
            ttk.Label(img_frame, text=titles[i], font=("Segoe UI", 9, "bold"), anchor="w").grid(row=i*2, column=0, sticky="w", pady=(4, 0))
            try:
                orig = Image.open(path)
                self._grid_img_orig.append(orig)
                label = ttk.Label(img_frame, cursor="hand2")
                label.grid(row=i*2+1, column=0, sticky="ew", pady=(0, 6))
                label.bind("<Button-1>", lambda e, p=path: self._show_full_image(p))
                self._grid_img_labels.append(label)
                self._grid_img_photos.append(None)
            except Exception as e:
                ttk.Label(img_frame, text=f"加载图片失败:\n{path}\n{e}").grid(row=i*2+1, column=0, sticky="ew")
                self._grid_img_orig.append(None)
                self._grid_img_labels.append(None)
                self._grid_img_photos.append(None)

        def _resize_grid_images(event):
            w = event.width
            if w < 50:
                return
            for i, orig in enumerate(self._grid_img_orig):
                if orig is None or self._grid_img_labels[i] is None:
                    continue
                iw, ih = orig.size
                ratio = w / iw
                new_w = int(iw * ratio)
                new_h = int(ih * ratio)
                resized = orig.resize((new_w, new_h), Image.LANCZOS)
                photo = ImageTk.PhotoImage(resized)
                self._grid_img_photos[i] = photo
                self._grid_img_labels[i].configure(image=photo)
            img_canvas.configure(scrollregion=img_canvas.bbox("all"))

        img_canvas.bind("<Configure>", _resize_grid_images)

        def _on_img_frame_configure(event):
            img_canvas.configure(scrollregion=img_canvas.bbox("all"))
        img_frame.bind("<Configure>", _on_img_frame_configure)

    def _show_full_image(self, path):
        try:
            os.startfile(path)
        except Exception as e:
            messagebox.showerror("错误", f"无法打开图片:\n{e}")

    def grid_to_ll(self):
        try:
            lat, lon = grid_to_latlon(self.grid_in.get())
        except ValueError as e:
            messagebox.showerror("错误", str(e))
            return
        self.lat_in.delete(0, "end")
        self.lat_in.insert(0, f"{lat:.4f}")
        self.lon_in.delete(0, "end")
        self.lon_in.insert(0, f"{lon:.4f}")
        self.set_status(f"网格转换完成")

    def ll_to_grid(self):
        try:
            lat, lon = float(self.lat_in.get()), float(self.lon_in.get())
        except ValueError:
            messagebox.showerror("错误", "请输入有效数值")
            return
        g4 = latlon_to_grid(lat, lon, 4)
        g6 = latlon_to_grid(lat, lon, 6)
        self.grid_in.delete(0, "end")
        self.grid_in.insert(0, g4)
        self.set_status(f"经纬度→网格转换完成")

    def grid_distance(self):
        g1, g2 = self.dist_g1.get().strip(), self.dist_g2.get().strip()
        if not g1 or not g2:
            messagebox.showerror("错误", "请填写两个网格")
            return
        try:
            r = distance_bearing(*grid_to_latlon(g1), *grid_to_latlon(g2))
        except ValueError as e:
            messagebox.showerror("错误", str(e))
            return
        self._clear(self.grid_result)
        self.grid_result.insert("end", f"网格1: {g1.upper()}  网格2: {g2.upper()}\n\n")
        self.grid_result.insert("end", f"距离: {r['km']} km  ({r['mi']} mi)  ({r['nmi']} nmi)\n")
        self.grid_result.insert("end", f"方位角: {r['bearing']}° (从网格1到网格2)\n")
        self.set_status(f"距离计算完成: {r['km']} km")

    # ============================================================
    # 4. 通联地图
    # ============================================================

    def build_map_tab(self, notebook):
        tab = ttk.Frame(notebook, padding="8")
        notebook.add(tab, text="通联地图")
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(1, weight=1)

        top_f = ttk.Frame(tab)
        top_f.grid(row=0, column=0, sticky="ew")
        ttk.Label(top_f, text="通联地图", font=("Segoe UI", 11, "bold")).pack(anchor="w", side="left")
        self.map_count_var = tk.StringVar(value="")
        ttk.Label(top_f, textvariable=self.map_count_var, font=("Segoe UI", 9), foreground="gray").pack(side="left", padx=(16, 0))
        ttk.Button(top_f, text="刷新地图", command=self.map_render).pack(side="right", padx=2)

        self.map_widget = tkintermapview.TkinterMapView(tab, width=800, height=450, corner_radius=0)
        self.map_widget.grid(row=1, column=0, sticky="nsew", pady=(4, 0))
        self.map_widget.set_tile_server("https://basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png", max_zoom=19)
        self.map_widget.set_position(30, 0)
        self.map_widget.set_zoom(2)

        self.root.after(300, self.map_render)
        notebook.bind("<<NotebookTabChanged>>", self._map_on_tab_change)

    def _map_on_tab_change(self, event=None):
        tab_text = event.widget.tab(event.widget.select(), "text") if event and hasattr(event, 'widget') else ""
        if tab_text == "通联":
            self.root.after(100, self.map_render)

    def map_get_coords(self, q):
        """Try to get lat/lon from a QSO record. Returns (lat, lon) or None."""
        qth = q.get("qth", "").strip()
        if not qth:
            return None
        tokens = qth.replace(",", " ").split()
        for token in tokens:
            upper = token.upper()
            if re.match(r'^[A-R]{2}[0-9]{2}([A-X]{2}([0-9]{2})?)?$', upper):
                try:
                    return grid_to_latlon(upper)
                except ValueError:
                    pass
            try:
                lat, lon = map(float, token.split("/"))
                return lat, lon
            except (ValueError, IndexError):
                pass
        for token in tokens:
            upper = token.upper()
            if upper in CITY_COORDS:
                return CITY_COORDS[upper]
        full = qth.upper().strip()
        if full in CITY_COORDS:
            return CITY_COORDS[full]
        return None

    def map_render(self):
        """Add QSO markers to the tkintermapview widget."""
        try:
            mw = self.map_widget
            if mw.winfo_width() < 50:
                self.root.after(500, self.map_render)
                return
            mw.delete_all_marker()
            count = 0
            for q in self.qsos:
                coords = self.map_get_coords(q)
                if coords is None:
                    continue
                lat, lon = coords
                call = q.get("call", "")
                mw.set_marker(lat, lon, text=call)
                count += 1
            self.map_count_var.set(f"已标记 {count} 个")
        except Exception as e:
            self.set_status(f"地图渲染错误: {e}")
            import traceback
            traceback.print_exc()

    # ============================================================
    # 5. Q简语
    # ============================================================

    def build_qcode_tab(self, notebook):
        tab = ttk.Frame(notebook, padding="12")
        notebook.add(tab, text="参考")
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(0, weight=1)

        book = ttk.Notebook(tab)
        book.grid(row=0, column=0, sticky="nsew")

        self._build_abbrev_subtab(book, "Q简语", Q_CODES, "Q 代码 (如 QTH)",
                                  col1="问句含义", col2="答句含义",
                                  lbl1="问", lbl2="答")
        self._build_abbrev_subtab(book, "英文缩略语", ENG_ABBREV, "英文缩略语 (如 CQ)",
                                  col1="中文含义", col2="英文说明",
                                  lbl1="中文", lbl2="英文")
        self._build_abbrev_subtab(book, "数字缩略语", NUM_ABBREV, "数字缩略语 (如 73)",
                                  col1="中文含义", col2="英文说明",
                                  lbl1="中文", lbl2="英文")

    def _build_abbrev_subtab(self, notebook, label, data, hint,
                              col1="中文含义", col2="英文说明",
                              lbl1="中文", lbl2="英文"):
        tab = ttk.Frame(notebook, padding="8")
        notebook.add(tab, text=label)
        tab.columnconfigure(1, weight=1)
        tab.rowconfigure(1, weight=1)

        entry = ttk.Entry(tab, width=16)
        entry.grid(row=0, column=0, sticky="w")
        entry.bind("<Return>", lambda e: self._abbrev_lookup(data, entry, result, lbl1, lbl2))
        add_tooltip(entry, f"输入{hint}，查询含义")
        ttk.Button(tab, text="查询", width=6,
                   command=lambda: self._abbrev_lookup(data, entry, result, lbl1, lbl2)).grid(row=0, column=1, padx=(4, 0))

        result = self._add_result_box(tab)
        result.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=4)

        ttk.Label(tab, text=f"{label}参考表:", font=("Segoe UI", 9, "bold")).grid(row=2, column=0, columnspan=2, sticky="w", pady=(4, 2))

        cols = ("code", "c1", "c2")
        tree = ttk.Treeview(tab, columns=cols, show="headings", height=14)
        tree.heading("code", text="代码")
        tree.heading("c1", text=col1)
        tree.heading("c2", text=col2)
        tree.column("code", width=70, anchor="center")
        tree.column("c1", width=220, anchor="w")
        tree.column("c2", width=280, anchor="w")
        for code, (a, b) in sorted(data.items(), key=lambda x: x[0].split(",")[0].strip()):
            tree.insert("", "end", values=(code, a, b))
        tree.grid(row=3, column=0, columnspan=2, sticky="nsew")
        tab.rowconfigure(3, weight=1)

    def _abbrev_lookup(self, data, entry_widget, result_widget, lbl1="中文", lbl2="英文"):
        q = entry_widget.get().strip().upper()
        if not q:
            return
        m = data.get(q)
        if m is None:
            for key, val in data.items():
                if q in [x.strip() for x in key.split(",")]:
                    m = val
                    break
        self._clear(result_widget)
        if m:
            a, b = m
            result_widget.insert("end", f"{q}\n")
            result_widget.insert("end", f"{lbl1}: {a}\n")
            result_widget.insert("end", f"{lbl2}: {b}\n")
        else:
            result_widget.insert("end", f"未找到: {q}\n")
        self.set_status(f"查询: {q}")

    # ============================================================
    # 8. 通联日志
    # ============================================================

    MODES = ["SSB", "CW", "FM", "AM", "DMR", "C4FM", "D-STAR", "FT8", "FT4",
             "RTTY", "PSK31", "JT65", "JT9", "WSPR", "SSTV", "ATV", "其他"]

    def build_log_tab(self, notebook):
        tab = ttk.Frame(notebook, padding="12")
        notebook.add(tab, text="通联")

        canvas = tk.Canvas(tab, highlightthickness=0)
        vsb_outer = ttk.Scrollbar(tab, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb_outer.set)
        canvas.pack(side="left", fill="both", expand=True)
        vsb_outer.pack(side="right", fill="y")

        scroll_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw", tags="inner")

        def _on_log_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        scroll_frame.bind("<Configure>", _on_log_configure)
        canvas.bind("<Configure>", lambda e: canvas.itemconfig("inner", width=e.width))

        self._bind_scrollwheel(canvas)

        input_f = ttk.LabelFrame(scroll_frame, text="新通联记录", padding="8")
        input_f.pack(fill="x")

        ttk.Label(input_f, text="* 日期 (UTC):").grid(row=0, column=0, sticky="w")
        self.log_date = ttk.Entry(input_f, width=14)
        self.log_date.grid(row=0, column=1, padx=4)
        add_tooltip(self.log_date, "通联日期 (UTC)\n格式: YYYY-MM-DD\n例: 2026-07-20")

        ttk.Label(input_f, text="* 时间 (UTC):").grid(row=0, column=2, sticky="w", padx=(12, 0))
        self.log_time = ttk.Entry(input_f, width=10)
        self.log_time.grid(row=0, column=3, padx=4)
        add_tooltip(self.log_time, "通联时间 (UTC)\n格式: HHMM\n例: 1030")

        ttk.Label(input_f, text="* 呼号:").grid(row=0, column=4, sticky="w", padx=(12, 0))
        self.log_call = ttk.Entry(input_f, width=14)
        self.log_call.grid(row=0, column=5, padx=4)
        add_tooltip(self.log_call, "对方电台呼号 (必填)\n例: BG1XXX, W1AW, JA1ABC")

        ttk.Label(input_f, text="* 频率 (MHz):").grid(row=0, column=6, sticky="w", padx=(12, 0))
        self.log_freq = ttk.Entry(input_f, width=10)
        self.log_freq.grid(row=0, column=7, padx=4)
        add_tooltip(self.log_freq, "通联频率，单位 MHz\n例: 14.200, 145.000")

        ttk.Label(input_f, text="* 模式:").grid(row=1, column=0, sticky="w", pady=4)
        self.log_mode = ttk.Combobox(input_f, values=self.MODES, state="readonly", width=12)
        self.log_mode.set("SSB")
        self.log_mode.grid(row=1, column=1, padx=4, pady=4)
        self.log_mode.bind("<<ComboboxSelected>>", self.log_mode_rst_preset)
        add_tooltip(self.log_mode, "通联模式\nSSB: 单边带\nCW: 等幅电报\nFM: 调频\nDMR: 数字语音\nFT8/FT4: 数字弱信号")

        ttk.Label(input_f, text="RST 发送:").grid(row=1, column=2, sticky="w", padx=(12, 0))
        self.log_rst_s = ttk.Entry(input_f, width=10)
        self.log_rst_s.grid(row=1, column=3, padx=4, pady=4)
        add_tooltip(self.log_rst_s, "您发给对方的信号报告\nSSB/FM 用 RS (如 59)\nCW 用 RST (如 599)")

        ttk.Label(input_f, text="RST 接收:").grid(row=1, column=4, sticky="w", padx=(12, 0))
        self.log_rst_r = ttk.Entry(input_f, width=10)
        self.log_rst_r.grid(row=1, column=5, padx=4, pady=4)
        add_tooltip(self.log_rst_r, "对方给您的信号报告\n格式同 RST 发送")

        ttk.Label(input_f, text="对方姓名:").grid(row=1, column=6, sticky="w", padx=(12, 0))
        self.log_name = ttk.Entry(input_f, width=14)
        self.log_name.grid(row=1, column=7, padx=4, pady=4)
        add_tooltip(self.log_name, "对方操作员姓名 (选填)")

        ttk.Label(input_f, text="QTH/网格:").grid(row=2, column=0, sticky="w")
        self.log_qth = ttk.Entry(input_f, width=20)
        self.log_qth.grid(row=2, column=1, columnspan=3, sticky="w", padx=4)
        add_tooltip(self.log_qth, "对方电台位置 (选填)\n城市、Maidenhead网格坐标等\n例: Beijing 或 OM89MM")

        ttk.Label(input_f, text="备注:").grid(row=2, column=4, sticky="w", padx=(12, 0))
        self.log_note = ttk.Entry(input_f, width=30)
        self.log_note.grid(row=2, column=5, columnspan=3, sticky="w", padx=4)
        add_tooltip(self.log_note, "备注信息 (选填)\n如设备型号、天气等")

        btn_f = ttk.Frame(input_f)
        btn_f.grid(row=4, column=0, columnspan=8, pady=(8, 0))
        ttk.Button(btn_f, text="填充时间", command=self.log_fill_time).pack(side="left", padx=4)
        ttk.Button(btn_f, text="保存记录", command=self.log_save).pack(side="left", padx=4)
        ttk.Button(btn_f, text="清空输入", command=self.log_clear_input).pack(side="left", padx=4)
        self.log_edit_btn = ttk.Button(btn_f, text="编辑选中", command=self.log_edit_selected)
        self.log_edit_btn.pack(side="left", padx=4)
        self.log_cancel_btn = ttk.Button(btn_f, text="取消编辑", command=self.log_cancel_edit)
        self.log_count_label = ttk.Label(btn_f, text="")
        self.log_count_label.pack(side="left", padx=(20, 0))

        search_f = ttk.Frame(scroll_frame)
        search_f.pack(fill="x", pady=(6, 0))
        ttk.Label(search_f, text="搜索:").pack(side="left")
        self.log_search_var = tk.StringVar()
        self.log_search_var.trace_add("write", lambda *a: self.log_refresh_table())
        log_search_entry = ttk.Entry(search_f, textvariable=self.log_search_var, width=28)
        log_search_entry.pack(side="left", padx=4)
        add_tooltip(log_search_entry, "按呼号/日期/频率/姓名/QTH/备注筛选")
        ttk.Label(search_f, text="(实时筛选)", font=("Segoe UI", 9), foreground="gray").pack(side="left")

        table_f = ttk.LabelFrame(scroll_frame, text="通联记录", padding="4")
        table_f.pack(fill="both", expand=True, pady=(8, 0))

        cols = ("idx", "date", "time", "call", "freq", "mode", "rst_s", "rst_r", "name", "qth", "note")
        self.log_tree = ttk.Treeview(table_f, columns=cols, show="headings", height=10)
        self.log_tree.heading("idx", text="#")
        self.log_tree.heading("date", text="日期")
        self.log_tree.heading("time", text="时间")
        self.log_tree.heading("call", text="呼号")
        self.log_tree.heading("freq", text="频率")
        self.log_tree.heading("mode", text="模式")
        self.log_tree.heading("rst_s", text="RST发")
        self.log_tree.heading("rst_r", text="RST收")
        self.log_tree.heading("name", text="姓名")
        self.log_tree.heading("qth", text="QTH")
        self.log_tree.heading("note", text="备注")

        self.log_tree.column("idx", width=35, anchor="center")
        self.log_tree.column("date", width=80, anchor="center")
        self.log_tree.column("time", width=60, anchor="center")
        self.log_tree.column("call", width=90, anchor="center")
        self.log_tree.column("freq", width=70, anchor="center")
        self.log_tree.column("mode", width=60, anchor="center")
        self.log_tree.column("rst_s", width=55, anchor="center")
        self.log_tree.column("rst_r", width=55, anchor="center")
        self.log_tree.column("name", width=80)
        self.log_tree.column("qth", width=100)
        self.log_tree.column("note", width=120)

        self.log_tree.bind("<Delete>", lambda e: self.log_delete_selected())
        self.log_tree.bind("<Double-1>", lambda e: self.log_edit_selected())

        log_btn_f = ttk.Frame(table_f)
        log_btn_f.pack(fill="x", pady=(4, 0))
        ttk.Button(log_btn_f, text="删除选中", command=self.log_delete_selected).pack(side="left", padx=2)
        ttk.Button(log_btn_f, text="导出 Excel", command=self.log_export_excel).pack(side="left", padx=2)
        ttk.Button(log_btn_f, text="导出 ADI", command=self.log_export_adi).pack(side="left", padx=2)
        ttk.Button(log_btn_f, text="导入 ADI", command=self.log_import_adi).pack(side="left", padx=2)
        ttk.Button(log_btn_f, text="导出 Cabrillo", command=self.log_export_cabrillo).pack(side="left", padx=2)
        ttk.Button(log_btn_f, text="备份", command=self.log_backup).pack(side="left", padx=2)
        ttk.Button(log_btn_f, text="恢复", command=self.log_restore).pack(side="left", padx=2)
        ttk.Button(log_btn_f, text="清空全部", command=self.log_clear_all).pack(side="left", padx=2)
        self.log_count2 = ttk.Label(log_btn_f, text="")
        self.log_count2.pack(side="right", padx=4)

        vsb = ttk.Scrollbar(table_f, orient="vertical", command=self.log_tree.yview)
        self.log_tree.configure(yscrollcommand=vsb.set)
        self.log_tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        self.qsos = load_qsos()
        self.log_edit_idx = None
        self.log_refresh_table()
        self.log_fill_time()

        ttk.Separator(scroll_frame, orient="horizontal").pack(fill="x", pady=8)
        ttk.Label(scroll_frame, text="通联地图", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        map_f = ttk.Frame(scroll_frame)
        map_f.pack(fill="both", expand=True)
        self.map_widget = tkintermapview.TkinterMapView(map_f, width=800, height=520, corner_radius=0)
        self.map_widget.configure(cursor="hand2")
        self.map_widget.pack(fill="both", expand=True)
        self.map_widget.set_tile_server("https://basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png", max_zoom=19)
        self.map_widget.set_position(30, 0)
        self.map_widget.set_zoom(2)
        self.root.after(300, self.map_render)

    def log_fill_time(self):
        now = datetime.now(timezone.utc)
        self.log_date.delete(0, "end")
        self.log_date.insert(0, now.strftime("%Y-%m-%d"))
        self.log_time.delete(0, "end")
        self.log_time.insert(0, now.strftime("%H%M"))

    def log_mode_rst_preset(self, event=None):
        mode = self.log_mode.get()
        if mode in ("SSB", "AM", "FM"):
            rst = "59"
        elif mode == "CW":
            rst = "599"
        elif mode in ("DMR", "C4FM", "D-STAR", "FT8", "FT4", "RTTY", "PSK31", "JT65", "JT9", "WSPR", "SSTV", "ATV"):
            rst = "59"
        else:
            return
        if not self.log_rst_s.get().strip():
            self.log_rst_s.delete(0, "end"); self.log_rst_s.insert(0, rst)
        if not self.log_rst_r.get().strip():
            self.log_rst_r.delete(0, "end"); self.log_rst_r.insert(0, rst)

    def log_save(self):
        date = self.log_date.get().strip()
        time = self.log_time.get().strip()
        call = self.log_call.get().strip().upper()
        freq = self.log_freq.get().strip()
        mode = self.log_mode.get()
        rst_s = self.log_rst_s.get().strip()
        rst_r = self.log_rst_r.get().strip()
        name = self.log_name.get().strip()
        qth = self.log_qth.get().strip()
        note = self.log_note.get().strip()

        if not call:
            messagebox.showerror("错误", "呼号不能为空")
            return
        if not date:
            date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        if not time:
            time = datetime.now(timezone.utc).strftime("%H%M")

        entry = {
            "date": date, "time": time, "call": call, "freq": freq,
            "mode": mode, "rst_s": rst_s, "rst_r": rst_r,
            "name": name, "qth": qth, "note": note,
        }

        if self.log_edit_idx is not None:
            self.qsos[self.log_edit_idx] = entry
            save_qsos(self.qsos)
            self.log_refresh_table()
            self.log_clear_input()
            self.set_status(f"已更新通联记录: {call}")
        else:
            self.qsos.append(entry)
            save_qsos(self.qsos)
            self.log_refresh_table()
            self.log_clear_input()
            self.set_status(f"已保存通联记录: {call}")

    def log_edit_selected(self):
        sel = self.log_tree.selection()
        if not sel:
            messagebox.showinfo("提示", "请先选中要编辑的记录")
            return
        idx = self.log_tree.index(sel[0])
        q = self.qsos[idx]
        self.log_edit_idx = idx
        self.log_date.delete(0, "end"); self.log_date.insert(0, q.get("date", ""))
        self.log_time.delete(0, "end"); self.log_time.insert(0, q.get("time", ""))
        self.log_call.delete(0, "end"); self.log_call.insert(0, q.get("call", ""))
        self.log_freq.delete(0, "end"); self.log_freq.insert(0, q.get("freq", ""))
        self.log_mode.set(q.get("mode", "SSB"))
        self.log_rst_s.delete(0, "end"); self.log_rst_s.insert(0, q.get("rst_s", ""))
        self.log_rst_r.delete(0, "end"); self.log_rst_r.insert(0, q.get("rst_r", ""))
        self.log_name.delete(0, "end"); self.log_name.insert(0, q.get("name", ""))
        self.log_qth.delete(0, "end"); self.log_qth.insert(0, q.get("qth", ""))
        self.log_note.delete(0, "end"); self.log_note.insert(0, q.get("note", ""))
        self.log_cancel_btn.pack(side="left", padx=4)
        self.log_date.focus()
        self.set_status(f"正在编辑第 {idx + 1} 条记录，保存后生效")

    def log_cancel_edit(self):
        self.log_edit_idx = None
        self.log_clear_input()
        self.log_cancel_btn.pack_forget()
        self.set_status("已取消编辑")

    def log_clear_input(self):
        self.log_edit_idx = None
        self.log_cancel_btn.pack_forget()
        self.log_date.delete(0, "end")
        self.log_time.delete(0, "end")
        self.log_call.delete(0, "end")
        self.log_freq.delete(0, "end")
        self.log_mode.set("SSB")
        self.log_rst_s.delete(0, "end")
        self.log_rst_r.delete(0, "end")
        self.log_name.delete(0, "end")
        self.log_qth.delete(0, "end")
        self.log_note.delete(0, "end")
        self.log_fill_time()

    def log_refresh_table(self):
        kw = self.log_search_var.get().strip().lower()
        for row in self.log_tree.get_children():
            self.log_tree.delete(row)
        filtered = self.qsos
        if kw:
            filtered = [q for q in self.qsos if
                        kw in q.get("call", "").lower() or
                        kw in q.get("date", "").lower() or
                        kw in q.get("freq", "").lower() or
                        kw in q.get("name", "").lower() or
                        kw in q.get("qth", "").lower() or
                        kw in q.get("note", "").lower() or
                        kw in q.get("mode", "").lower()]
        for i, q in enumerate(filtered, 1):
            self.log_tree.insert("", "end", values=(
                i, q.get("date", ""), q.get("time", ""), q.get("call", ""),
                q.get("freq", ""), q.get("mode", ""), q.get("rst_s", ""),
                q.get("rst_r", ""), q.get("name", ""), q.get("qth", ""), q.get("note", ""),
            ))
        cnt = len(self.qsos)
        shown = len(filtered)
        text = f"共 {cnt} 条记录" if not kw else f"筛选 {shown}/{cnt} 条"
        self.log_count_label.config(text=text)
        self.log_count2.config(text=text)

    def log_delete_selected(self):
        sel = self.log_tree.selection()
        if not sel:
            messagebox.showinfo("提示", "请先选中要删除的记录")
            return
        indices = sorted([self.log_tree.index(s) for s in sel], reverse=True)
        for idx in indices:
            del self.qsos[idx]
        save_qsos(self.qsos)
        self.log_refresh_table()
        self.set_status("已删除选中记录")

    def log_clear_all(self):
        if not self.qsos:
            return
        if not messagebox.askyesno("确认", "确定要清空所有通联记录吗？"):
            return
        self.qsos.clear()
        save_qsos(self.qsos)
        self.log_refresh_table()
        self.set_status("已清空所有通联记录")

    def log_export_excel(self):
        if not self.qsos:
            messagebox.showinfo("提示", "没有记录可导出")
            return
        now_str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        xls_path = os.path.join(LOG_DIR, f"qso_export_{now_str}.xls")
        lines = ['<html><head><meta charset="UTF-8"></head><body><table border="1">']
        lines.append("<tr><th>#</th><th>日期</th><th>时间</th><th>呼号</th><th>频率(MHz)</th><th>模式</th><th>RST发</th><th>RST收</th><th>姓名</th><th>QTH</th><th>备注</th></tr>")
        for i, q in enumerate(self.qsos, 1):
            lines.append(f"<tr><td>{i}</td><td>{q.get('date', '')}</td><td>{q.get('time', '')}</td>"
                         f"<td>{q.get('call', '')}</td><td>{q.get('freq', '')}</td><td>{q.get('mode', '')}</td>"
                         f"<td>{q.get('rst_s', '')}</td><td>{q.get('rst_r', '')}</td><td>{q.get('name', '')}</td>"
                         f"<td>{q.get('qth', '')}</td><td>{q.get('note', '')}</td></tr>")
        lines.append("</table></body></html>")
        with open(xls_path, "w", encoding="utf-8") as f:
            f.writelines(lines)
        self.set_status(f"已导出到 {xls_path}")

    def log_export_adi(self):
        if not self.qsos:
            messagebox.showinfo("提示", "没有记录可导出")
            return
        now_str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        path = os.path.join(LOG_DIR, f"qso_export_{now_str}.adi")
        lines = ["ADIF_VER:3.1.0\n", "PROGRAMID:HamToolbox\n", "PROGRAMVERSION:1.0\n", "<EOH>\n"]
        for q in self.qsos:
            date = q.get("date", "").replace("-", "")
            time = q.get("time", "")
            call = q.get("call", "")
            freq = q.get("freq", "")
            mode = q.get("mode", "SSB")
            rst_s = q.get("rst_s", "")
            rst_r = q.get("rst_r", "")
            name = q.get("name", "")
            qth = q.get("qth", "")
            note = q.get("note", "")
            line = f"<QSO_DATE:{len(date)}>{date}<TIME_ON:{len(time)}>{time}<CALL:{len(call)}>{call}"
            line += f"<FREQ:{len(freq)}>{freq}<MODE:{len(mode)}>{mode}"
            line += f"<RST_SENT:{len(rst_s)}>{rst_s}<RST_RCVD:{len(rst_r)}>{rst_r}"
            if name:
                line += f"<NAME:{len(name)}>{name}"
            if qth:
                line += f"<QTH:{len(qth)}>{qth}"
            if note:
                line += f"<COMMENT:{len(note)}>{note}"
            line += "<EOR>\n"
            lines.append(line)
        with open(path, "w", encoding="utf-8") as f:
            f.writelines(lines)
        self.set_status(f"已导出 ADI 到 {path}")

    def log_import_adi(self):
        path = filedialog.askopenfilename(title="选择 ADI 文件",
                                          filetypes=[("ADI 文件", "*.adi *.ADI"), ("所有文件", "*.*")])
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            messagebox.showerror("错误", f"无法读取文件:\n{e}")
            return
        imported = 0
        for record in re.finditer(r"<EOR>", content, re.IGNORECASE):
            block = content[:record.start()]
            content = content[record.end():]
            def get_tag(tag, text=block):
                m = re.search(rf"<{tag}:(\d+)>([^<]+)", text, re.IGNORECASE)
                if m:
                    return m.group(2).strip()
                m2 = re.search(rf"<{tag}:(\d+)[^>]*>", text, re.IGNORECASE)
                if m2:
                    start = m2.end()
                    length = int(m2.group(1))
                    return text[start:start+length].strip()
                return ""
            date = get_tag("QSO_DATE").replace("-", "")
            if len(date) == 8:
                date = f"{date[:4]}-{date[4:6]}-{date[6:]}"
            time = get_tag("TIME_ON")
            call = get_tag("CALL").upper()
            freq = get_tag("FREQ")
            mode = get_tag("MODE")
            rst_s = get_tag("RST_SENT")
            rst_r = get_tag("RST_RCVD")
            name = get_tag("NAME")
            qth = get_tag("QTH")
            note = get_tag("COMMENT")
            if not call:
                continue
            self.qsos.append({
                "date": date, "time": time, "call": call, "freq": freq,
                "mode": mode, "rst_s": rst_s, "rst_r": rst_r,
                "name": name, "qth": qth, "note": note,
            })
            imported += 1
        if imported:
            save_qsos(self.qsos)
            self.log_refresh_table()
            self.set_status(f"已导入 {imported} 条 ADI 记录")
        else:
            messagebox.showinfo("提示", "未找到有效的 ADI 记录")

    def log_export_cabrillo(self):
        if not self.qsos:
            messagebox.showinfo("提示", "没有记录可导出")
            return
        now_str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        path = os.path.join(LOG_DIR, f"qso_export_{now_str}.log")
        lines = [
            "START-OF-LOG: 3.0\n",
            "CALLSIGN: HAMTOOLBOX\n",
            "CONTEST: NA\n",
            "CATEGORY-OPERATOR: SINGLE-OP\n",
            "CATEGORY-BAND: ALL\n",
            "CATEGORY-MODE: MIXED\n",
            "CATEGORY-POWER: HIGH\n",
            "CLAIMED-SCORE: 0\n",
            "LOCATION: DX\n",
            "OPERATORS: HAMTOOLBOX\n",
            "NAME: Ham Radio Toolbox\n",
            "ADDRESS: China\n",
            "SOAPBOX: Exported from Ham Toolbox\n",
            "\n",
        ]
        for q in self.qsos:
            freq_khz = ""
            try:
                freq_khz = str(int(float(q.get("freq", 0)) * 1000))
            except (ValueError, TypeError):
                freq_khz = "    "
            freq_khz = freq_khz.rjust(5)
            date = q.get("date", "").replace("-", "")
            time = q.get("time", "").ljust(4)
            call = q.get("call", "").ljust(13)
            mode_code = {"SSB": "PH", "CW": "CW", "FM": "FM", "AM": "AM",
                         "FT8": "DG", "FT4": "DG", "RTTY": "RY", "PSK31": "DG",
                         "JT65": "DG", "JT9": "DG"}.get(q.get("mode", ""), "PH")
            rst_s = q.get("rst_s", "59").ljust(3)
            rst_r = q.get("rst_r", "59").ljust(3)
            line = f"QSO: {freq_khz} {mode_code} {date} {time} HAMTOOLBOX  {rst_s} {call} {rst_r} 0\n"
            lines.append(line)
        with open(path, "w", encoding="utf-8") as f:
            f.writelines(lines)
        self.set_status(f"已导出 Cabrillo 到 {path}")

    def log_backup(self):
        if not self.qsos:
            messagebox.showinfo("提示", "没有记录可备份")
            return
        backup_dir = os.path.join(LOG_DIR, "backups")
        os.makedirs(backup_dir, exist_ok=True)
        now_str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        dst = os.path.join(backup_dir, f"qso_backup_{now_str}.json")
        shutil.copy(LOG_FILE, dst)
        self.set_status(f"已备份到 {dst}")

    def log_restore(self):
        backup_dir = os.path.join(LOG_DIR, "backups")
        if not os.path.isdir(backup_dir):
            messagebox.showinfo("提示", "没有找到备份目录")
            return
        path = filedialog.askopenfilename(title="选择备份文件",
                                          initialdir=backup_dir,
                                          filetypes=[("JSON 备份", "*.json"), ("所有文件", "*.*")])
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            messagebox.showerror("错误", f"无法读取备份文件:\n{e}")
            return
        if not isinstance(data, list):
            messagebox.showerror("错误", "备份文件格式无效")
            return
        if not messagebox.askyesno("确认", f"将用 {len(data)} 条备份记录替换当前 {len(self.qsos)} 条记录，确定吗？"):
            return
        self.qsos = data
        save_qsos(self.qsos)
        self.log_refresh_table()
        self.set_status(f"已恢复 {len(self.qsos)} 条备份记录")

    # ============================================================
    # 9. CW 练习
    # ============================================================

    MORSE_CODE = {
        'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.',
        'F': '..-.', 'G': '--.', 'H': '....', 'I': '..', 'J': '.---',
        'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.', 'O': '---',
        'P': '.--.', 'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-',
        'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-', 'Y': '-.--',
        'Z': '--..',
        '0': '-----', '1': '.----', '2': '..---', '3': '...--', '4': '....-',
        '5': '.....', '6': '-....', '7': '--...', '8': '---..', '9': '----.',
        '.': '.-.-.-', ',': '--..--', '?': '..--..', "'": '.----.', '!': '-.-.--',
        '/': '-..-.', '(': '-.--.', ')': '-.--.-', '&': '.-...', ':': '---...',
        ';': '-.-.-.', '=': '-...-', '+': '.-.-.', '-': '-....-', '_': '..--.-',
        '"': '.-..-.', '@': '.--.-.',
    }
    MORSE_REV = {v: k for k, v in MORSE_CODE.items()}

    def build_cw_tab(self, notebook):
        import threading as _th
        import winsound as _ws
        import random as _rnd
        import time as _time
        self._cw_thread = _th
        self._ws = _ws
        self._rnd = _rnd
        self._time = _time
        self.cw_stop = False

        tab = ttk.Frame(notebook, padding="12")
        notebook.add(tab, text="CW练习")
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(1, weight=1)

        # Speed control
        speed_f = ttk.Frame(tab)
        speed_f.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        ttk.Label(speed_f, text="速度 (WPM):").pack(side="left")
        self.cw_wpm = tk.IntVar(value=20)
        scale = ttk.Scale(speed_f, from_=5, to_=40, variable=self.cw_wpm, orient="horizontal", length=200)
        scale.pack(side="left", padx=8)
        self.cw_wpm_label = ttk.Label(speed_f, text="20 WPM", width=8)
        self.cw_wpm_label.pack(side="left")
        scale.configure(command=lambda v: self.cw_wpm_label.config(text=f"{int(float(v))} WPM"))

        # Sub notebook
        cw_book = ttk.Notebook(tab)
        cw_book.grid(row=1, column=0, sticky="nsew")

        # ---- Encode tab ----
        enc = ttk.Frame(cw_book, padding="8")
        cw_book.add(enc, text="文本→摩尔斯")
        enc.columnconfigure(1, weight=1)
        enc.rowconfigure(1, weight=1)
        ttk.Label(enc, text="输入文本 (全角自动转半角; 中文不支持, 以 # 标记):").grid(row=0, column=0, sticky="w")
        self.cw_encode_in = scrolledtext.ScrolledText(enc, height=4, wrap="word", font=("Consolas", 11))
        self.cw_encode_in.grid(row=1, column=0, columnspan=3, sticky="nsew", pady=4)
        btn_f = ttk.Frame(enc)
        btn_f.grid(row=2, column=0, columnspan=3, pady=4)
        ttk.Button(btn_f, text="转换为摩尔斯", command=self.cw_encode).pack(side="left", padx=4)
        ttk.Button(btn_f, text="播放", command=self.cw_play_encode).pack(side="left", padx=4)
        ttk.Button(btn_f, text="停止", command=self.cw_stop_play).pack(side="left", padx=4)
        self.cw_encode_out = scrolledtext.ScrolledText(enc, height=6, wrap="word", font=("Consolas", 14, "bold"),
                                                        bg="#f0f8f0", state="disabled")
        self.cw_encode_out.grid(row=3, column=0, columnspan=3, sticky="nsew", pady=4)
        enc.rowconfigure(3, weight=1)

        # ---- Decode tab ----
        dec = ttk.Frame(cw_book, padding="8")
        cw_book.add(dec, text="摩尔斯→文字")
        dec.columnconfigure(0, weight=1)
        dec.rowconfigure(1, weight=1)
        ttk.Label(dec, text="输入摩尔斯码 (空格分隔字母, / 分隔单词):").grid(row=0, column=0, sticky="w")
        self.cw_decode_in = scrolledtext.ScrolledText(dec, height=6, wrap="word", font=("Consolas", 14, "bold"))
        self.cw_decode_in.grid(row=1, column=0, sticky="nsew", pady=4)
        btn_f3 = ttk.Frame(dec)
        btn_f3.grid(row=2, column=0, sticky="ew", pady=4)
        ttk.Button(btn_f3, text="转换为文字", command=self.cw_decode).pack(side="left", padx=4)
        ttk.Button(btn_f3, text="清空", command=lambda: self.cw_decode_in.delete("1.0", "end")).pack(side="left", padx=4)
        # Straight key simulator
        self.cw_key_timer_id = None
        self.cw_key_press_time = None
        key_f = ttk.LabelFrame(btn_f3, text="模拟电键")
        key_f.pack(side="right", padx=4)
        ttk.Label(key_f, text="短按=点(·)  长按=划(-)", font=("Segoe UI", 9)).pack()
        self.cw_key_btn = tk.Frame(key_f, bg="#e0e0e0", bd=3, relief="raised",
                                   width=200, height=50, cursor="hand2")
        self.cw_key_btn.pack_propagate(False)
        self.cw_key_btn.pack(pady=2)
        lbl = tk.Label(self.cw_key_btn, text="电键", bg="#e0e0e0",
                       font=("Segoe UI", 16, "bold"))
        lbl.place(relx=0.5, rely=0.5, anchor="center")
        self.cw_key_label = lbl
        self.cw_key_btn.bind("<ButtonPress-1>", self._cw_key_down)
        self.cw_key_btn.bind("<ButtonRelease-1>", self._cw_key_up)
        lbl.bind("<ButtonPress-1>", self._cw_key_down)
        lbl.bind("<ButtonRelease-1>", self._cw_key_up)
        self.cw_decode_out = scrolledtext.ScrolledText(dec, height=6, wrap="word", font=("Consolas", 11),
                                                        bg="#f5f5f5", state="disabled")
        self.cw_decode_out.grid(row=3, column=0, sticky="nsew", pady=4)
        dec.rowconfigure(3, weight=1)

        # ---- Practice tab ----
        prac = ttk.Frame(cw_book, padding="8")
        cw_book.add(prac, text="随机练习")
        prac.columnconfigure(1, weight=1)
        ttk.Label(prac, text="练习字符集:").grid(row=0, column=0, sticky="w")
        chars_f = ttk.Frame(prac)
        chars_f.grid(row=0, column=1, sticky="w", pady=4)
        self.cw_prac_alpha = tk.BooleanVar(value=True)
        self.cw_prac_num = tk.BooleanVar(value=True)
        self.cw_prac_punct = tk.BooleanVar(value=False)
        ttk.Checkbutton(chars_f, text="字母 A-Z", variable=self.cw_prac_alpha).pack(side="left", padx=4)
        ttk.Checkbutton(chars_f, text="数字 0-9", variable=self.cw_prac_num).pack(side="left", padx=4)
        ttk.Checkbutton(chars_f, text="标点符号", variable=self.cw_prac_punct).pack(side="left", padx=4)
        ttk.Label(prac, text="每组字符数:").grid(row=1, column=0, sticky="w")
        self.cw_prac_len = ttk.Combobox(prac, values=["1", "2", "3", "4", "5", "6", "7", "8"], width=5, state="readonly")
        self.cw_prac_len.set("3")
        self.cw_prac_len.grid(row=1, column=1, sticky="w")
        ttk.Label(prac, text="重复次数:").grid(row=2, column=0, sticky="w")
        self.cw_prac_count = ttk.Combobox(prac, values=["1", "2", "3", "5", "10"], width=5, state="readonly")
        self.cw_prac_count.set("3")
        self.cw_prac_count.grid(row=2, column=1, sticky="w")
        btn_f2 = ttk.Frame(prac)
        btn_f2.grid(row=3, column=0, columnspan=2, pady=8)
        self.cw_prac_btn = ttk.Button(btn_f2, text="开始练习", command=self.cw_practice_start)
        self.cw_prac_btn.pack(side="left", padx=4)
        ttk.Button(btn_f2, text="停止", command=self.cw_stop_play).pack(side="left", padx=4)
        ttk.Button(btn_f2, text="显示答案", command=self.cw_practice_reveal).pack(side="left", padx=4)
        self.cw_prac_disp = scrolledtext.ScrolledText(prac, height=4, wrap="word", font=("Consolas", 18, "bold"),
                                                       bg="#fffde7", state="disabled")
        self.cw_prac_disp.grid(row=4, column=0, columnspan=2, sticky="nsew", pady=4)
        self.cw_prac_log = scrolledtext.ScrolledText(prac, height=6, wrap="word", font=("Consolas", 11),
                                                      bg="#f5f5f5", state="disabled")
        self.cw_prac_log.grid(row=5, column=0, columnspan=2, sticky="nsew")

        score_f = ttk.Frame(prac)
        score_f.grid(row=6, column=0, columnspan=2, sticky="ew", pady=(4, 0))
        ttk.Label(score_f, text="你的抄收:").pack(side="left")
        self.cw_prac_user = ttk.Entry(score_f, width=30, font=("Consolas", 12))
        self.cw_prac_user.pack(side="left", padx=4)
        self.cw_prac_user.bind("<Return>", lambda e: self.cw_practice_check())
        ttk.Button(score_f, text="检查结果", command=self.cw_practice_check).pack(side="left", padx=4)
        self.cw_prac_score_var = tk.StringVar(value="")
        ttk.Label(score_f, textvariable=self.cw_prac_score_var, font=("Segoe UI", 10, "bold"),
                  foreground="green").pack(side="left", padx=(8, 0))

        prac.rowconfigure(5, weight=1)
        self.cw_prac_answer = ""

        # ---- Chart tab ----
        chart = ttk.Frame(cw_book, padding="8")
        cw_book.add(chart, text="码表")
        cols = ("char", "morse")
        tree = ttk.Treeview(chart, columns=cols, show="headings", height=24)
        tree.heading("char", text="字符")
        tree.heading("morse", text="摩尔斯码")
        tree.column("char", width=80, anchor="center")
        tree.column("morse", width=200, anchor="center")
        for ch, code in sorted(self.MORSE_CODE.items(), key=lambda x: (len(x[1]), x[1])):
            tree.insert("", "end", values=(ch, code))
        tree.pack(fill="both", expand=True)

    def _normalize_text(self, text):
        result = []
        for ch in text:
            code = ord(ch)
            if 0xFF01 <= code <= 0xFF5E:
                result.append(chr(code - 0xFEE0))
            elif code == 0x3000:
                result.append(" ")
            else:
                result.append(ch)
        return "".join(result)

    def text_to_morse(self, text):
        text = self._normalize_text(text)
        result = []
        for ch in text.upper():
            if ch in self.MORSE_CODE:
                result.append(self.MORSE_CODE[ch])
            elif ch == " ":
                result.append("/")
            else:
                result.append("#")
        return " ".join(result)

    def cw_encode(self):
        text = self.cw_encode_in.get("1.0", "end-1c").strip()
        if not text:
            return
        has_cjk = any("\u4e00" <= ch <= "\u9fff" for ch in text)
        has_full = any(0xFF01 <= ord(ch) <= 0xFF5E for ch in text)
        morse = self.text_to_morse(text)
        self.cw_encode_out.config(state="normal")
        self.cw_encode_out.delete("1.0", "end")
        self.cw_encode_out.insert("1.0", morse)
        self.cw_encode_out.config(state="disabled")
        if has_cjk or has_full:
            parts = []
            if has_full:
                parts.append("全角字符已自动转为半角")
            if has_cjk:
                parts.append("中文不支持摩尔斯码, 以 # 标记")
            self.set_status("; ".join(parts))

    def morse_to_text(self, morse):
        words = morse.strip().split("/")
        result = []
        for word in words:
            letters = word.strip().split()
            decoded = []
            for l in letters:
                if l in self.MORSE_REV:
                    decoded.append(self.MORSE_REV[l])
                elif l == "#":
                    decoded.append("?")
                else:
                    decoded.append("?")
            result.append("".join(decoded))
        return " ".join(result)

    def _cw_key_down(self, event):
        self.cw_key_press_time = self._time.time()
        self.cw_key_btn.config(bg="#ff9999", relief="sunken")
        self.cw_key_label.config(bg="#ff9999")
        if self.cw_key_timer_id:
            self.root.after_cancel(self.cw_key_timer_id)
            self.cw_key_timer_id = None

    def _cw_key_up(self, event):
        if self.cw_key_press_time is None:
            return
        elapsed = (self._time.time() - self.cw_key_press_time) * 1000
        self.cw_key_press_time = None
        self.cw_key_btn.config(bg="#e0e0e0", relief="raised")
        self.cw_key_label.config(bg="#e0e0e0")
        if elapsed < 300:
            self.cw_decode_in.insert("end", ".")
        else:
            self.cw_decode_in.insert("end", "-")
        self.cw_decode_in.see("end")
        self.cw_key_timer_id = self.root.after(700, self._cw_key_space)

    def _cw_key_space(self):
        self.cw_key_timer_id = None
        content = self.cw_decode_in.get("1.0", "end-1c").strip()
        if content and content[-1] not in (".", "-"):
            return
        self.cw_decode_in.insert("end", " ")
        self.cw_decode_in.see("end")

    def _cw_generate_wav(self, morse_str, dot_ms, freq):
        import wave, struct, math as _math, tempfile, os
        sample_rate = 22050
        amp = 8000
        dot_samp = int(sample_rate * dot_ms / 1000)
        gap_samp = dot_samp
        letter_gap = dot_samp * 2
        word_gap = dot_samp * 6
        samples = []
        for ch in morse_str:
            if ch == ".":
                n = dot_samp
            elif ch == "-":
                n = dot_samp * 3
            else:
                n = 0
            if n > 0:
                for i in range(n):
                    t = i / sample_rate
                    val = int(amp * _math.sin(2 * _math.pi * freq * t))
                    samples.append(struct.pack("<h", val))
                for i in range(gap_samp):
                    samples.append(struct.pack("<h", 0))
            elif ch == " ":
                for i in range(letter_gap):
                    samples.append(struct.pack("<h", 0))
            elif ch == "/":
                for i in range(word_gap):
                    samples.append(struct.pack("<h", 0))
            elif ch == "#":
                for i in range(letter_gap):
                    samples.append(struct.pack("<h", 0))
        path = os.path.join(tempfile.gettempdir(), "_ham_cw_temp.wav")
        data = b"".join(samples)
        with wave.open(path, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(data)
        total_ms = int(len(data) / 2 / sample_rate * 1000)
        return path, total_ms

    def _cw_beep_seq(self, morse_str, callback=None):
        wpm = self.cw_wpm.get()
        dot_ms = max(50, int(1200 / wpm))
        freq = 700
        self.cw_stop = False
        try:
            wav_path, total_ms = self._cw_generate_wav(morse_str, dot_ms, freq)
            self._ws.PlaySound(wav_path, self._ws.SND_ASYNC)
            remaining = total_ms / 1000.0
            interval = 0.1
            while remaining > 0 and not self.cw_stop:
                self._time.sleep(min(interval, remaining))
                remaining -= interval
        except Exception as e:
            self.root.after(0, lambda e=e: messagebox.showerror("播放错误", str(e)))
        finally:
            self._ws.PlaySound(None, 0)
            if callback:
                self.root.after(0, callback)

    def cw_play_encode(self):
        morse = self.cw_encode_out.get("1.0", "end-1c").strip()
        if not morse:
            return
        self.cw_stop = False
        if "#" in morse:
            text = self.cw_encode_in.get("1.0", "end-1c").strip()
            has_cjk = any("\u4e00" <= ch <= "\u9fff" for ch in text)
            if has_cjk:
                self.set_status("注意: 中文不支持摩尔斯码, 请删除 # 标记后播放")
                return
        self._cw_thread.Thread(target=self._cw_beep_seq, args=(morse,), daemon=True).start()

    def cw_stop_play(self):
        self.cw_stop = True
        try:
            self._ws.PlaySound(None, 0)
        except Exception:
            pass

    def cw_decode(self):
        morse = self.cw_decode_in.get("1.0", "end-1c").strip()
        text = self.morse_to_text(morse)
        self.cw_decode_out.config(state="normal")
        self.cw_decode_out.delete("1.0", "end")
        self.cw_decode_out.insert("1.0", text)
        self.cw_decode_out.config(state="disabled")

    def cw_practice_start(self):
        chars = ""
        if self.cw_prac_alpha.get():
            chars += "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        if self.cw_prac_num.get():
            chars += "0123456789"
        if self.cw_prac_punct.get():
            chars += ".,?!/()&:;=+-@"
        if not chars:
            messagebox.showerror("错误", "请至少选择一个字符类型")
            return
        length = int(self.cw_prac_len.get())
        count = int(self.cw_prac_count.get())
        self.cw_prac_answer = ""
        all_morse = []
        for _ in range(count):
            group = "".join(self._rnd.choices(chars, k=length))
            self.cw_prac_answer += group + " "
            all_morse.append(self.text_to_morse(group))
        self.cw_prac_disp.config(state="normal")
        self.cw_prac_disp.delete("1.0", "end")
        self.cw_prac_disp.insert("1.0", "播放中...")
        self.cw_prac_disp.config(state="disabled")
        self.cw_prac_log.config(state="normal")
        self.cw_prac_log.delete("1.0", "end")
        self.cw_prac_log.insert("1.0", "\n".join(all_morse))
        self.cw_prac_log.config(state="disabled")
        full_morse = "  ".join(all_morse).replace(" / ", "   ")
        self._cw_thread.Thread(target=self._cw_beep_seq,
                               args=(full_morse, self.cw_practice_done),
                               daemon=True).start()

    def cw_practice_done(self):
        if self.cw_prac_disp.get("1.0", "end-1c").strip() == "播放中...":
            self.cw_prac_disp.config(state="normal")
            self.cw_prac_disp.delete("1.0", "end")
            self.cw_prac_disp.insert("1.0", "(播放完毕)")
            self.cw_prac_disp.config(state="disabled")

    def cw_practice_reveal(self):
        self.cw_prac_disp.config(state="normal")
        self.cw_prac_disp.delete("1.0", "end")
        self.cw_prac_disp.insert("1.0", self.cw_prac_answer.strip())
        self.cw_prac_disp.config(state="disabled")

    def cw_practice_check(self):
        user_input = self.cw_prac_user.get().strip().upper()
        if not user_input:
            return
        answer = self.cw_prac_answer.strip().upper()
        if not answer:
            self.cw_prac_score_var.set("请先生成练习")
            return
        correct = sum(1 for a, b in zip(user_input, answer) if a == b)
        total = max(len(answer), len(user_input))
        pct = int(correct / total * 100) if total else 0
        self.cw_prac_score_var.set(f"正确 {correct}/{total} ({pct}%)")
        if pct == 100:
            self.cw_prac_score_var.set(f"正确 {correct}/{total} ({pct}%) ✓ 完美!")
        self.set_status(f"CW抄收结果: {correct}/{total} ({pct}%)")

    # ============================================================
    # 10. 工具
    # ============================================================

    def build_utils_tab(self, notebook):
        tab = ttk.Frame(notebook, padding="12")
        notebook.add(tab, text="工具")

        ttk.Label(tab, text="世界时钟", font=("Segoe UI", 11, "bold")).pack(anchor="w")
        clock_f = ttk.Frame(tab)
        clock_f.pack(fill="x", pady=4)
        self._clock_frame = clock_f
        self.clock_vars = {}
        self.custom_clocks = []
        tz_list = [
            ("UTC", "UTC"),
            ("BJT (北京)", "Asia/Shanghai"),
            ("JST (东京)", "Asia/Tokyo"),
            ("EST (纽约)", "America/New_York"),
            ("PST (洛杉矶)", "America/Los_Angeles"),
            ("BST (伦敦)", "Europe/London"),
        ]
        for i, (label, tz_name) in enumerate(tz_list):
            r, c = divmod(i, 3)
            f = ttk.LabelFrame(clock_f, text=label, padding=4)
            f.grid(row=r, column=c, padx=4, pady=2, sticky="nsew")
            var = tk.StringVar(value="--:--:--")
            self.clock_vars[label] = var
            ttk.Label(f, textvariable=var, font=("Consolas", 12, "bold")).pack()

        add_f = ttk.Frame(tab)
        add_f.pack(fill="x", pady=(8, 4))
        ttk.Label(add_f, text="自定义时钟:", font=("Segoe UI", 9, "bold")).pack(side="left")
        self.custom_tz_entry = ttk.Entry(add_f, width=24)
        self.custom_tz_entry.pack(side="left", padx=4)
        self.custom_tz_entry.insert(0, "输入城市名(中文/英文)或时区名")
        self.custom_tz_entry.bind("<FocusIn>", lambda e: self.custom_tz_entry.delete(0, "end") if self.custom_tz_entry.get().startswith("输入") else None)
        ttk.Button(add_f, text="添加", command=self._add_custom_clock).pack(side="left", padx=2)
        ttk.Button(add_f, text="清除自定义", command=self._clear_custom_clocks).pack(side="left", padx=2)

        ttk.Separator(tab, orient="horizontal").pack(fill="x", pady=8)

        ttk.Label(tab, text="传播条件参考", font=("Segoe UI", 11, "bold")).pack(anchor="w")
        prop_btn_f = ttk.Frame(tab)
        prop_btn_f.pack(fill="x", pady=4)
        ttk.Button(prop_btn_f, text="刷新实时数据", command=self.prop_fetch).pack(side="left")
        self.prop_status_var = tk.StringVar(value="")
        ttk.Label(prop_btn_f, textvariable=self.prop_status_var, font=("Segoe UI", 9), foreground="gray").pack(side="left", padx=(12, 0))

        self.prop_result = scrolledtext.ScrolledText(tab, height=10, wrap="word",
                                                      font=("Consolas", 10), bg="#f5f5f5")
        self.prop_result.pack(fill="both", expand=True, pady=4)

        ttk.Separator(tab, orient="horizontal").pack(fill="x", pady=4)

        ttk.Label(tab, text="RST 信号报告", font=("Segoe UI", 11, "bold")).pack(anchor="w")
        rst_f = ttk.Frame(tab)
        rst_f.pack(fill="x", pady=4)
        ttk.Label(rst_f, text="RST (如 599):").pack(side="left")
        self.rst_entry = ttk.Entry(rst_f, width=12)
        self.rst_entry.pack(side="left", padx=8)
        self.rst_entry.bind("<Return>", lambda e: self.rst_query())
        add_tooltip(self.rst_entry, "RST 信号报告：三位数字\nR=可辨度 (1-5)\nS=信号强度 (1-9)\nT=音质 (1-9)\n例: 59=可辨度5, 强度9; 599=CW 59+音质9")
        ttk.Button(rst_f, text="查询", command=self.rst_query).pack(side="left")

        self.rst_result = scrolledtext.ScrolledText(tab, height=5, wrap="word",
                                                      font=("Consolas", 10), bg="#f5f5f5")
        self.rst_result.pack(fill="both", expand=True, pady=4)

    def _add_custom_clock(self):
        query = self.custom_tz_entry.get().strip()
        if not query or query.startswith("输入"):
            return
        from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

        CITY_TZ = {
            "北京": "Asia/Shanghai", "上海": "Asia/Shanghai", "广州": "Asia/Shanghai",
            "深圳": "Asia/Shanghai", "成都": "Asia/Shanghai", "重庆": "Asia/Shanghai",
            "武汉": "Asia/Shanghai", "杭州": "Asia/Shanghai", "南京": "Asia/Shanghai",
            "天津": "Asia/Shanghai", "西安": "Asia/Shanghai", "长沙": "Asia/Shanghai",
            "沈阳": "Asia/Shanghai", "哈尔滨": "Asia/Shanghai", "大连": "Asia/Shanghai",
            "济南": "Asia/Shanghai", "青岛": "Asia/Shanghai", "厦门": "Asia/Shanghai",
            "昆明": "Asia/Shanghai", "贵阳": "Asia/Shanghai", "兰州": "Asia/Shanghai",
            "乌鲁木齐": "Asia/Urumqi", "拉萨": "Asia/Urumqi", "香港": "Asia/Hong_Kong",
            "澳门": "Asia/Macau", "台北": "Asia/Taipei", "高雄": "Asia/Taipei",
            "东京": "Asia/Tokyo", "大阪": "Asia/Tokyo", "京都": "Asia/Tokyo",
            "名古屋": "Asia/Tokyo", "福冈": "Asia/Tokyo", "札幌": "Asia/Tokyo",
            "横滨": "Asia/Tokyo", "神户": "Asia/Tokyo", "仙台": "Asia/Tokyo",
            "首尔": "Asia/Seoul", "釜山": "Asia/Seoul", "仁川": "Asia/Seoul",
            "新加坡": "Asia/Singapore", "吉隆坡": "Asia/Kuala_Lumpur",
            "曼谷": "Asia/Bangkok", "河内": "Asia/Ho_Chi_Minh", "胡志明市": "Asia/Ho_Chi_Minh",
            "雅加达": "Asia/Jakarta", "马尼拉": "Asia/Manila", "金边": "Asia/Phnom_Penh",
            "仰光": "Asia/Yangon", "加德满都": "Asia/Kathmandu", "科伦坡": "Asia/Colombo",
            "孟买": "Asia/Kolkata", "新德里": "Asia/Kolkata", "班加罗尔": "Asia/Kolkata",
            "迪拜": "Asia/Dubai", "利雅得": "Asia/Riyadh", "德黑兰": "Asia/Tehran",
            "伊斯坦布尔": "Europe/Istanbul", "莫斯科": "Europe/Moscow",
            "悉尼": "Australia/Sydney", "墨尔本": "Australia/Melbourne",
            "布里斯班": "Australia/Brisbane", "珀斯": "Australia/Perth",
            "奥克兰": "Pacific/Auckland", "惠灵顿": "Pacific/Auckland",
            "伦敦": "Europe/London", "巴黎": "Europe/Paris", "柏林": "Europe/Berlin",
            "罗马": "Europe/Rome", "马德里": "Europe/Madrid", "阿姆斯特丹": "Europe/Amsterdam",
            "布鲁塞尔": "Europe/Brussels", "维也纳": "Europe/Vienna",
            "苏黎世": "Europe/Zurich", "斯德哥尔摩": "Europe/Stockholm",
            "华沙": "Europe/Warsaw", "布拉格": "Europe/Prague", "布达佩斯": "Europe/Budapest",
            "雅典": "Europe/Athens", "赫尔辛基": "Europe/Helsinki",
            "里斯本": "Europe/Lisbon", "都柏林": "Europe/Dublin",
            "纽约": "America/New_York", "华盛顿": "America/New_York",
            "波士顿": "America/New_York", "费城": "America/New_York",
            "芝加哥": "America/Chicago", "休斯顿": "America/Chicago",
            "达拉斯": "America/Chicago", "迈阿密": "America/New_York",
            "亚特兰大": "America/New_York", "底特律": "America/New_York",
            "洛杉矶": "America/Los_Angeles", "旧金山": "America/Los_Angeles",
            "西雅图": "America/Los_Angeles", "圣地亚哥": "America/Los_Angeles",
            "拉斯维加斯": "America/Los_Angeles", "凤凰城": "America/Phoenix",
            "丹佛": "America/Denver", "温哥华": "America/Vancouver",
            "多伦多": "America/Toronto", "蒙特利尔": "America/Toronto",
            "渥太华": "America/Toronto", "卡尔加里": "America/Edmonton",
            "墨西哥城": "America/Mexico_City", "圣保罗": "America/Sao_Paulo",
            "里约热内卢": "America/Sao_Paulo", "布宜诺斯艾利斯": "America/Argentina/Buenos_Aires",
            "利马": "America/Lima", "波哥大": "America/Bogota",
            "开罗": "Africa/Cairo", "约翰内斯堡": "Africa/Johannesburg",
            "内罗毕": "Africa/Nairobi", "拉各斯": "Africa/Lagos",
            "卡萨布兰卡": "Africa/Casablanca",
            "米兰": "Europe/Rome", "慕尼黑": "Europe/Berlin", "汉堡": "Europe/Berlin",
            "法兰克福": "Europe/Berlin", "巴塞罗那": "Europe/Madrid",
            "里斯本": "Europe/Lisbon", "哥本哈根": "Europe/Copenhagen",
            "奥斯陆": "Europe/Oslo", "赫尔辛基": "Europe/Helsinki",
            "基辅": "Europe/Kiev", "布加勒斯特": "Europe/Bucharest",
            "贝尔格莱德": "Europe/Belgrade", "萨格勒布": "Europe/Zagreb",
            "华沙": "Europe/Warsaw", "克拉科夫": "Europe/Warsaw",
            "里昂": "Europe/Paris", "马赛": "Europe/Paris", "尼斯": "Europe/Paris",
            "迪拜": "Asia/Dubai", "阿布扎比": "Asia/Dubai",
            "多哈": "Asia/Qatar", "科威特": "Asia/Kuwait",
            "曼谷": "Asia/Bangkok", "清迈": "Asia/Bangkok",
            "河内": "Asia/Ho_Chi_Minh", "胡志明市": "Asia/Ho_Chi_Minh",
            "雅加达": "Asia/Jakarta", "巴厘岛": "Asia/Makassar",
        }

        resolved_tz = None
        display_label = query

        if query in CITY_TZ:
            resolved_tz = CITY_TZ[query]
            display_label = query
        else:
            try:
                ZoneInfo(query)
                resolved_tz = query
                display_label = query.split("/")[-1].replace("_", " ")
            except (ZoneInfoNotFoundError, KeyError):
                pass

        if not resolved_tz:
            for city, tz in CITY_TZ.items():
                if query in city or city in query:
                    resolved_tz = tz
                    display_label = city
                    break

        if not resolved_tz:
            self.set_status(f"正在搜索 {query} ...")
            self.root.update_idletasks()

            def _lookup():
                nonlocal resolved_tz, display_label
                try:
                    r = requests.get(
                        "https://geocoding-api.open-meteo.com/v1/search",
                        params={"name": query, "count": 1, "language": "zh"},
                        timeout=8
                    )
                    data = r.json()
                    if data.get("results"):
                        res = data["results"][0]
                        tz = res.get("timezone", "")
                        name = res.get("name", query)
                        country = res.get("country", "")
                        if tz:
                            resolved_tz = tz
                            display_label = f"{name} ({country})" if country else name
                except Exception:
                    pass
                self.root.after(0, _finish_add)

            def _finish_add():
                if not resolved_tz:
                    self.set_status(f"未找到: {query}")
                    return
                if display_label in self.clock_vars:
                    self.set_status(f"时钟已存在: {display_label}")
                    return
                row_idx = len(self.custom_clocks)
                r = row_idx // 3
                c = 3 + row_idx % 3
                outer = ttk.Frame(self._clock_frame)
                outer.grid(row=r, column=c, padx=4, pady=2, sticky="nsew")
                f = ttk.LabelFrame(outer, text=display_label, padding=4)
                f.pack(fill="both", expand=True)
                var = tk.StringVar(value="--:--:--")
                self.clock_vars[display_label] = var
                ttk.Label(f, textvariable=var, font=("Consolas", 11, "bold")).pack()
                ttk.Label(f, text=resolved_tz, font=("Segoe UI", 8), foreground="gray").pack()
                del_btn = ttk.Button(outer, text="×", width=2,
                                     command=lambda lbl=display_label: self._remove_custom_clock(lbl))
                del_btn.place(relx=1.0, rely=0.0, x=-2, y=2, anchor="ne")
                self.custom_clocks.append((display_label, resolved_tz, outer))
                self.custom_tz_entry.delete(0, "end")
                self.set_status(f"已添加: {display_label} ({resolved_tz})")

            import threading
            threading.Thread(target=_lookup, daemon=True).start()
            return

        if display_label in self.clock_vars:
            self.set_status(f"时钟已存在: {display_label}")
            return
        row_idx = len(self.custom_clocks)
        r = row_idx // 3
        c = 3 + row_idx % 3
        outer = ttk.Frame(self._clock_frame)
        outer.grid(row=r, column=c, padx=4, pady=2, sticky="nsew")
        f = ttk.LabelFrame(outer, text=display_label, padding=4)
        f.pack(fill="both", expand=True)
        var = tk.StringVar(value="--:--:--")
        self.clock_vars[display_label] = var
        ttk.Label(f, textvariable=var, font=("Consolas", 11, "bold")).pack()
        ttk.Label(f, text=resolved_tz, font=("Segoe UI", 8), foreground="gray").pack()
        del_btn = ttk.Button(outer, text="×", width=2,
                             command=lambda lbl=display_label: self._remove_custom_clock(lbl))
        del_btn.place(relx=1.0, rely=0.0, x=-2, y=2, anchor="ne")
        self.custom_clocks.append((display_label, resolved_tz, outer))
        self.custom_tz_entry.delete(0, "end")
        self.set_status(f"已添加: {display_label} ({resolved_tz})")

    def _remove_custom_clock(self, label):
        for i, (lbl, tz, frame) in enumerate(self.custom_clocks):
            if lbl == label:
                frame.destroy()
                self.clock_vars.pop(label, None)
                self.custom_clocks.pop(i)
                break
        self.set_status(f"已删除: {label}")

    def _clear_custom_clocks(self):
        for label, tz_name, frame in self.custom_clocks:
            frame.destroy()
            self.clock_vars.pop(label, None)
        self.custom_clocks.clear()
        self.set_status("自定义时钟已清除")

    def update_clock(self):
        from zoneinfo import ZoneInfo
        now_utc = datetime.now(timezone.utc)
        tz_zones = {
            "UTC": "UTC",
            "BJT (北京)": "Asia/Shanghai",
            "JST (东京)": "Asia/Tokyo",
            "EST (纽约)": "America/New_York",
            "PST (洛杉矶)": "America/Los_Angeles",
            "BST (伦敦)": "Europe/London",
        }
        for label, tz_name in tz_zones.items():
            if label in self.clock_vars:
                t = now_utc.astimezone(ZoneInfo(tz_name))
                self.clock_vars[label].set(t.strftime("%H:%M:%S"))
        for label, tz_name, _ in self.custom_clocks:
            if label in self.clock_vars:
                t = now_utc.astimezone(ZoneInfo(tz_name))
                self.clock_vars[label].set(t.strftime("%H:%M:%S"))
        self.root.after(1000, self.update_clock)

    def prop_fetch(self):
        """Fetch real-time propagation data from HamQSL + NOAA."""
        self._clear(self.prop_result)
        self.prop_result.insert("end", "正在获取实时传播数据...\n")
        self.prop_status_var.set("正在连接 hamqsl.com ...")
        self.root.update_idletasks()

        def _do_fetch():
            try:
                import xml.etree.ElementTree as ET
                import threading
                from datetime import datetime, timezone

                r = requests.get("https://www.hamqsl.com/solarxml.php", timeout=10)
                root_xml = ET.fromstring(r.text)
                data = root_xml.find("solardata")

                updated = (data.findtext("updated") or "").strip()
                sfi = (data.findtext("solarflux") or "?").strip()
                kindex = (data.findtext("kindex") or "?").strip()
                xray = (data.findtext("xray") or "?").strip()
                sunspots = (data.findtext("sunspots") or "?").strip()
                aindex = (data.findtext("aindex") or "?").strip()
                geomag = (data.findtext("geomagfield") or "?").strip()
                sn = (data.findtext("signalnoise") or "?").strip()
                solar_wind = (data.findtext("solarwind") or "?").strip()
                proton = (data.findtext("protonflux") or "?").strip()
                helium = (data.findtext("heliumline") or "?").strip()
                electron = (data.findtext("electonflux") or "?").strip()
                aurora = (data.findtext("aurora") or "?").strip()

                sfi_val = int(sfi) if sfi.isdigit() else 0
                kp_val = float(kindex) if kindex.replace(".", "").isdigit() else 0

                utc_now = datetime.now(timezone.utc)
                local_hour = (utc_now.hour + 8) % 24

                self._clear(self.prop_result)
                self.prop_result.insert("end", f"数据来源: hamqsl.com (N0NBH)  更新: {updated}\n")
                self.prop_result.insert("end", "=" * 52 + "\n")
                self.prop_result.insert("end", f"  太阳通量 (SFI): {sfi}    Kp 指数: {kindex}\n")
                self.prop_result.insert("end", f"  X 射线: {xray}    黑子数: {sunspots}\n")
                self.prop_result.insert("end", f"  A 指数: {aindex}    地磁状态: {geomag}\n")
                self.prop_result.insert("end", f"  太阳风速: {solar_wind} km/s  质子通量: {proton} pfu\n")
                self.prop_result.insert("end", f"  He I 10830: {helium}    电子通量: {electron} pfu\n")
                self.prop_result.insert("end", f"  极光活动: {aurora}    信号噪声: {sn}\n")

                self.prop_result.insert("end", "\n" + "=" * 52 + "\n")
                self.prop_result.insert("end", "【太阳/地磁评估】\n")
                if sfi_val > 0:
                    if sfi_val >= 180:
                        sfi_eval = "极高 — HF 全波段极佳，6m 可能开通跨洲"
                    elif sfi_val >= 150:
                        sfi_eval = "高 — 10-15m 波段开阔，全球通联良机"
                    elif sfi_val >= 120:
                        sfi_eval = "中高 — 14-28MHz 传播良好"
                    elif sfi_val >= 90:
                        sfi_eval = "中等 — 20m/17m 可用"
                    elif sfi_val >= 70:
                        sfi_eval = "低 — 仅 40m/80m 可靠"
                    else:
                        sfi_eval = "极低 — 仅 80m/160m 可能通联"
                    self.prop_result.insert("end", f"  SFI {sfi}: {sfi_eval}\n")

                if kp_val >= 0:
                    if kp_val <= 1:
                        kp_eval = "宁静 — 地磁平静，传播稳定"
                    elif kp_val <= 3:
                        kp_eval = "正常 — 一般条件可用"
                    elif kp_val <= 5:
                        kp_eval = "不稳定 — 高纬度路径受影响"
                    elif kp_val <= 7:
                        kp_eval = "磁暴 — 短波信号大幅衰减"
                    else:
                        kp_eval = "严重磁暴 — HF 传播极差"
                    self.prop_result.insert("end", f"  Kp {kindex}: {kp_eval}\n")

                if xray and xray not in ("?", "No Report"):
                    xr = xray.upper()
                    if "X" in xr:
                        self.prop_result.insert("end", f"  X 射线 {xray}: 强烈耀斑，D 层吸收增强，LF/MF 可能增强\n")
                    elif "M" in xr:
                        self.prop_result.insert("end", f"  X 射线 {xray}: 中等耀斑，短时 D 层吸收增加\n")
                    elif "C" in xr:
                        self.prop_result.insert("end", f"  X 射线 {xray}: 小耀斑，对传播影响轻微\n")

                self.prop_result.insert("end", "\n" + "=" * 52 + "\n")
                self.prop_result.insert("end", "【频段传播状况】 (hamqsl.com 全球评估)\n")

                bands_xml = data.find("calculatedconditions")
                if bands_xml is not None:
                    for band in bands_xml.findall("band"):
                        name = band.get("name", "")
                        time = band.get("time", "")
                        status = (band.text or "").strip()
                        label = "白天" if time == "day" else "夜晚"
                        icon = {"Good": "●", "Fair": "◐", "Poor": "○", "Not Open": "✕"}.get(status, "?")
                        self.prop_result.insert("end", f"  {name:>12s} {label}: {icon} {status}\n")

                self.prop_result.insert("end", "\n" + "=" * 52 + "\n")
                self.prop_result.insert("end", "【频段/模式建议】\n")
                if sfi_val >= 120 and kp_val <= 3:
                    self.prop_result.insert("end", "  HF 全波段条件优良，适合远距离通联\n")
                    self.prop_result.insert("end", "  推荐: 10m/15m SSB, 20m FT8, 6m MS/FME\n")
                elif sfi_val >= 90 and kp_val <= 4:
                    self.prop_result.insert("end", "  20m/15m 可用，黄昏留意低波段\n")
                    self.prop_result.insert("end", "  推荐: 20m FT8/SSB, 40m CW\n")
                elif kp_val >= 5:
                    self.prop_result.insert("end", "  磁暴期间建议使用低波段 CW/FT8\n")
                    self.prop_result.insert("end", "  推荐: 80m/40m CW, FT8, 避免高波段\n")
                else:
                    self.prop_result.insert("end", "  40m/80m 较可靠，高波段视情况而定\n")
                    self.prop_result.insert("end", "  推荐: 40m CW/FT8, 80m 夜间\n")

                self.prop_status_var.set(f"更新: {updated} (UTC+8: {local_hour:02d}:{utc_now.minute:02d})")
                self.set_status("传播数据已更新")
            except Exception as e:
                self._clear(self.prop_result)
                self.prop_result.insert("end", f"获取数据失败: {e}\n")
                self.prop_result.insert("end", "请检查网络连接后重试\n")
                self.prop_status_var.set("获取失败")

        import threading
        threading.Thread(target=_do_fetch, daemon=True).start()

    def rst_query(self):
        try:
            rst = int(self.rst_entry.get())
        except ValueError:
            messagebox.showerror("错误", "请输入RST数值（如 599）")
            return
        s = str(rst).zfill(3)
        r, sig, t = int(s[0]), int(s[1]), int(s[2])
        r_desc = ["无法阅读", "偶尔可辨单词", "阅读困难", "阅读无大碍", "完全清晰"][r - 1] if 1 <= r <= 5 else "?"
        s_desc = [
            "极弱，勉强可闻", "很弱", "弱", "尚可", "较好",
            "良好", "较强", "强", "极强", "S9+ 超强"
        ][sig - 1] if 1 <= sig <= 10 else "?"
        t_desc = [
            "严重的交流声", "粗糙交流音", "粗糙音带乐感", "略带滤波", "有乐感带交流声",
            "滤波音带纹波", "近纯直流", "完美直流无交流声", "完美但有频移", "完美的音调"
        ][t - 1] if 1 <= t <= 10 else "?"

        self._clear(self.rst_result)
        self.rst_result.insert("end", f"RST {rst}\n\n")
        self.rst_result.insert("end", f"R={r} 可辨度: {r_desc}\n")
        self.rst_result.insert("end", f"S={sig} 信号强度: {s_desc}\n")
        self.rst_result.insert("end", f"T={t} 音质: {t_desc}\n")
        self.set_status(f"RST {rst} 查询完成")


def main():
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass
    root = tk.Tk()
    app = HamToolboxGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
