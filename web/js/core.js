/**
 * HAM Radio Toolbox - 核心常量与数据模块
 * 包含频段数据、馈线数据、Q简语、缩略语、摩尔斯码等基础数据
 * 以及核心计算函数（频率转换、波长、网格坐标、功率、SWR等）
 */
(function(global) {
  'use strict';

  const Module = {};

  // ============================================================
  // 物理常量
  // ============================================================
  Module.C = 299792458;

  // ============================================================
  // 频段分类中文映射
  // ============================================================
  Module.CAT_CN = {
    "VLF": "甚低频", "LF": "低频", "MF": "中频", "HF": "高频",
    "VHF": "甚高频", "UHF": "特高频", "SHF": "超高频", "EHF": "极高频"
  };

  // ============================================================
  // 业余频段数据
  // ============================================================
  Module.BANDS = [
    {name:"2200m",f_low:0.1357,f_high:0.1378,cat:"LF",license:"C(≤1000W)",svc:"次要业务"},
    {name:"630m",f_low:0.472,f_high:0.479,cat:"MF",license:"C(≤1000W)",svc:"次要业务"},
    {name:"160m",f_low:1.8,f_high:2.0,cat:"MF",license:"C(≤1000W)",svc:"主要业务"},
    {name:"80m",f_low:3.5,f_high:3.9,cat:"HF",license:"B(<15W) / C(≤1000W)",svc:"共同主要业务"},
    {name:"60m",f_low:5.3515,f_high:5.3665,cat:"HF",license:"B(<15W) / C(≤1000W)",svc:"次要业务"},
    {name:"40m",f_low:7.0,f_high:7.2,cat:"HF",license:"B(<15W) / C(≤1000W)",svc:"主要业务"},
    {name:"30m",f_low:10.1,f_high:10.15,cat:"HF",license:"B(<15W) / C(≤1000W)",svc:"次要业务"},
    {name:"20m",f_low:14.0,f_high:14.35,cat:"HF",license:"B(<15W) / C(≤1000W)",svc:"主要业务"},
    {name:"17m",f_low:18.068,f_high:18.168,cat:"HF",license:"B(<15W) / C(≤1000W)",svc:"主要业务"},
    {name:"15m",f_low:21.0,f_high:21.45,cat:"HF",license:"B(<15W) / C(≤1000W)",svc:"主要业务"},
    {name:"12m",f_low:24.89,f_high:24.99,cat:"HF",license:"B(<15W) / C(≤1000W)",svc:"主要业务"},
    {name:"10m",f_low:28.0,f_high:29.7,cat:"HF",license:"B(<15W) / C(≤1000W)",svc:"主要业务"},
    {name:"6m",f_low:50.0,f_high:54.0,cat:"VHF",license:"A/B/C(≤25W)",svc:"共同主要业务"},
    {name:"2m",f_low:144.0,f_high:148.0,cat:"VHF",license:"A/B/C(≤25W)",svc:"主要业务"},
    {name:"1.25m",f_low:222.0,f_high:225.0,cat:"VHF",license:"A/B/C(≤25W)",svc:"主要业务"},
    {name:"70cm",f_low:430.0,f_high:440.0,cat:"UHF",license:"A/B/C(≤25W)",svc:"共同主要业务"},
    {name:"33cm",f_low:902.0,f_high:928.0,cat:"UHF",license:"A/B/C(≤25W)",svc:"主要业务"},
    {name:"23cm",f_low:1240.0,f_high:1300.0,cat:"UHF",license:"A/B/C(≤25W)",svc:"主要业务"},
    {name:"13cm",f_low:2300.0,f_high:2450.0,cat:"UHF",license:"A/B/C(≤25W)",svc:"共同主要业务"},
    {name:"9cm",f_low:3300.0,f_high:3500.0,cat:"SHF",license:"A/B/C(≤25W)",svc:"共同主要业务"},
    {name:"6cm",f_low:5650.0,f_high:5850.0,cat:"SHF",license:"A/B/C(≤25W)",svc:"主要业务"},
    {name:"3cm",f_low:10000.0,f_high:10500.0,cat:"SHF",license:"A/B/C(≤25W)",svc:"主要业务"},
    {name:"1.2cm",f_low:24000.0,f_high:24250.0,cat:"SHF",license:"A/B/C(≤25W)",svc:"主要业务"},
    {name:"6mm",f_low:47000.0,f_high:47200.0,cat:"EHF",license:"A/B/C(≤25W)",svc:"主要业务"},
  ];

  // ============================================================
  // 频段分类
  // ============================================================
  Module.SPECTRUM_CATS = [
    [0.003,0.03,"VLF"],[0.03,0.3,"LF"],[0.3,3,"MF"],[3,30,"HF"],
    [30,300,"VHF"],[300,3000,"UHF"],[3000,30000,"SHF"],[30000,300000,"EHF"]
  ];

  // ============================================================
  // 馈线类型
  // ============================================================
  Module.COAX_TYPES = {
    "RG174":{100:6.6,200:9.5,400:14.0,1000:23.0,2400:40.0},
    "RG58":{100:4.6,200:6.8,400:11.0,1000:20.0,2400:34.0},
    "RG213":{100:1.8,200:2.7,400:4.2,1000:7.5,2400:13.5},
    "RG8X":{100:2.9,200:4.2,400:6.5,1000:12.0,2400:22.0},
    "LMR240":{100:2.1,200:3.0,400:4.6,1000:8.0,2400:14.2},
    "LMR400":{100:1.2,200:1.7,400:2.7,1000:4.9,2400:8.9},
    "LMR600":{100:0.8,200:1.1,400:1.8,1000:3.3,2400:6.0}
  };

  // ============================================================
  // 通信模式
  // ============================================================
  Module.MODES = ["SSB","CW","FM","AM","DMR","C4FM","D-STAR","FT8","FT4","RTTY","PSK31","JT65","JT9","WSPR","SSTV","ATV","其他"];

  // ============================================================
  // Q简语
  // ============================================================
  Module.Q_CODES = [
    ["QRA","你台名称是什么？","我台名称是___。"],
    ["QRB","你离我多远？","我离你___km。"],
    ["QRC","你的频率是多少？","我的频率是___。"],
    ["QRD","你要到哪里去？","我要到___去。"],
    ["QRE","你何时到达？","我将于___到达。"],
    ["QRF","你要返回吗？","我要返回。"],
    ["QRG","我的确切频率是多少？","你的确切频率是___。"],
    ["QRH","我的频率变动吗？","你的频率在变动。"],
    ["QRI","我的音调如何？","你的音调___(1-3)。"],
    ["QRJ","你能收到我吗？","我不能收到你。"],
    ["QRK","我的信号可辨度如何？","你的信号可辨度___(1-5)。"],
    ["QRL","你忙吗？","我忙(或___忙)。"],
    ["QRM","你受到干扰吗？","我受到___级干扰。"],
    ["QRN","你受到天电干扰吗？","我受到___级天电干扰。"],
    ["QRO","要我增加功率吗？","增加功率。"],
    ["QRP","要我降低功率吗？","降低功率。"],
    ["QRQ","要我发快些吗？","发快些(___WPM)。"],
    ["QRS","要我发慢些吗？","发慢些。"],
    ["QRT","要我停止发送吗？","停止发送。"],
    ["QRU","你有什么给我吗？","我没有什么给你。"],
    ["QRV","你准备好了吗？","我准备好了。"],
    ["QRW","我应在___频率上呼叫吗？","在___频率上呼叫。"],
    ["QRX","你什么时候再呼叫我？","我将在___时/分再呼叫你。"],
    ["QRY","我应轮到第几？","你应轮到第___号。"],
    ["QRZ","谁在呼叫我？","你在被___呼叫。"],
    ["QSA","我的信号强度如何？","你的信号强度___(1-5)。"],
    ["QSB","我的信号衰落吗？","你的信号在衰落。"],
    ["QSC","你是低功率电台吗？","我是低功率电台。"],
    ["QSD","我的按键有毛病吗？","你的按键有毛病。"],
    ["QSL","你能确认收妥吗？","我确认收妥。"],
    ["QSO","你能与___直接联络吗？","我能与___直接联络。"],
    ["QSP","你能转发给___吗？","我可以转发给___。"],
    ["QSU","我应在___频率上发送吗？","在___频率上发送。"],
    ["QSV","要我在此频率上发送测试信号吗？","在此频率上发送___个测试信号。"],
    ["QSX","你能在___频率上收听吗？","我可以在___频率上收听。"],
    ["QSY","要我改到另一频率吗？","改到___频率。"],
    ["QSZ","要我每组发送两次吗？","每组发送两次。"]
  ];

  // ============================================================
  // 英文缩略语
  // ============================================================
  Module.ENG_ABBREV = [
    ["ABT","大约","About"],["AGN","再次","Again"],["ANT","天线","Antenna"],
    ["BK","打断/回复","Break"],["BN","之间","Between"],["CQ","普遍呼叫","Calling Any Station"],
    ["CW","等幅电报","Continuous Wave"],["DE","来自","From"],["DX","远距离","Distance"],
    ["ES","和","And"],["FB","好/优秀","Fine Business"],["HI","笑声","Laughter"],
    ["HW","怎么样","How Copy"],["K","请回答","Go Ahead"],["M","分钟","Minutes"],
    ["N","否/北","No/North"],["NW","现在","Now"],["OK","确认","Okay"],
    ["OM","老伙计","Old Man"],["OP","操作员","Operator"],["PSE","请","Please"],
    ["PWR","功率","Power"],["R","收到/确认","Roger"],["RCVR","接收机","Receiver"],
    ["RIG","电台设备","Radio Equipment"],["RX","接收","Receive"],
    ["SK","结束通信","End of Contact"],["TNX","谢谢","Thanks"],
    ["TU","谢谢你","Thank You"],["TX","发射","Transmit"],["U","你","You"],
    ["UR","你的","Your"],["VY","非常","Very"],["WX","天气","Weather"],
    ["XYL","妻子","Wife"],["YL","女士","Young Lady"],["Z","Zulu时间/UTC","Zulu Time/UTC"],
    ["73","最美好的祝愿","Best Regards"],["88","爱与亲吻","Love and Kisses"],
    ["BCNU","希望能见到你","Be Seeing You"],["B4","之前","Before"],
    ["CU","再见","See You"],["CUL","回头见","See You Later"],
    ["EFO","五","Five"],["FER","为了","For"],
    ["GA","下午好/继续","Good Afternoon/Go Ahead"],["GB","再见","Good Bye"],
    ["GE","晚上好","Good Evening"],["GM","早上好","Good Morning"],
    ["GN","晚安","Good Night"],["HR","这里","Here"],["HV","有","Have"],
    ["LD","长距离","Long Distance"],["LID","不熟练的操作者","Poor Operator"],
    ["NR","编号/号码","Number"],["RCVD","已收到","Received"],
    ["SASE","自回信封","Self-Addressed Stamped Envelope"],
    ["XMT","发射","Transmit"],["XTAL","晶体","Crystal"],
    ["YF","妻子","Wife"],["QRP","低功率","Low Power"],
    ["QRO","高功率","High Power"],["QSY","改频","Change Frequency"],
    ["QSL","确认收妥","Acknowledge Receipt"],["QTH","位置","Location"],
    ["QTR","时间","Time/Correct Time"],["QRM","人为干扰","Interference"],
    ["QRN","天电干扰","Static"],["QRZ","谁在呼叫","Who is Calling"],
    ["QRV","准备好了","Ready"],["QRU","无事","Nothing for You"],
    ["QRL","忙吗","Are You Busy"],["QRK","信号可辨度","Signal Readability"],
    ["QSB","信号衰落","Signal Fading"],["QSO","通联","Contact"],
    ["QRX","稍等","Standby"]
  ];

  // ============================================================
  // 数字缩略语
  // ============================================================
  Module.NUM_ABBREV = [
    ["1","等待","Wait"],["2","请重复","Repeat"],["3","紧急/求救","Emergency/SOS"],
    ["5","已收到/确认","Acknowledged"],["7","请改频","Change Frequency"],
    ["9","信号报告请求","Request Signal Report"],["10","收到完毕","Received Complete"],
    ["12","我已准备好","I Am Ready"],["13","我理解/同意","I Understand/Agree"],
    ["73","最美好的祝愿","Best Regards"],["88","爱与亲吻","Love and Kisses"]
  ];

  // ============================================================
  // 摩尔斯码
  // ============================================================
  Module.MORSE_CODE = {
    "A":"·-","B":"-···","C":"-·-·","D":"-··","E":"·","F":"··-·","G":"--·",
    "H":"····","I":"··","J":"·---","K":"-·-","L":"·-··","M":"--","N":"-·",
    "O":"---","P":"·--·","Q":"--·-","R":"·-·","S":"···","T":"-","U":"··-",
    "V":"···-","W":"·--","X":"-··-","Y":"-·--","Z":"--··",
    "1":"·----","2":"··---","3":"···--","4":"····-","5":"·····",
    "6":"-····","7":"--···","8":"---··","9":"----·","0":"-----",
    ".":"·-·-·-",",":"--··--","?":"··--··","'":"·----·","!":"-·-·--",
    "/":"-··-·","(":"-·--·",")":"-·--·-","&":"·-···",":":"---···",
    ";":"-·-·-·","=":"-···-","+":"·-·-","-":"-····-","_":"··--·-",
    "\"":"·-··-·","$":"···-··-","@":"·--·-·"
  };

  Module.MORSE_REVERSE = {};
  Object.entries(Module.MORSE_CODE).forEach(function(entry) {
    Module.MORSE_REVERSE[entry[1]] = entry[0];
  });

  // ============================================================
  // 城市坐标
  // ============================================================
  Module.CITY_COORDS = {
    "北京":[39.9042,116.4074],"上海":[31.2304,121.4737],"广州":[23.1291,113.2644],
    "深圳":[22.5431,114.0579],"成都":[30.5728,104.0668],"杭州":[30.2741,120.1551],
    "武汉":[30.5928,114.3055],"南京":[32.0603,118.7969],"重庆":[29.5630,106.5516],
    "西安":[34.3416,108.9398],"天津":[39.3434,117.3616],"苏州":[31.2990,120.5853],
    "长沙":[28.2282,112.9388],"沈阳":[41.8057,123.4315],"哈尔滨":[45.8038,126.5350],
    "大连":[38.9140,121.6147],"济南":[36.6512,117.1201],"青岛":[36.0671,120.3826],
    "郑州":[34.7466,113.6254],"昆明":[25.0389,102.7183],"福州":[26.0745,119.2965],
    "厦门":[24.4798,118.0894],"合肥":[31.8206,117.2272],"南昌":[28.6820,115.8579],
    "太原":[37.8706,112.5489],"贵阳":[26.6470,106.6302],"兰州":[36.0611,103.8343],
    "乌鲁木齐":[43.8256,87.6168],"拉萨":[29.6500,91.1000],"呼和浩特":[40.8424,111.7490],
    "南宁":[22.8170,108.3665],"海口":[20.0440,110.1999],"银川":[38.4872,106.2309],
    "西宁":[36.6171,101.7782],"石家庄":[38.0428,114.5149],"长春":[43.8171,125.3235],
    "台北":[25.0330,121.5654],"香港":[22.3193,114.1694],"澳门":[22.1987,113.5439],
    "东京":[35.6762,139.6503],"大阪":[34.6937,135.5023],"首尔":[37.5665,126.9780],
    "釜山":[35.1796,129.0756],"新加坡":[1.3521,103.8198],"曼谷":[13.7563,100.5018],
    "河内":[21.0278,105.8342],"雅加达":[-6.2088,106.8456],"马尼拉":[14.5995,120.9842],
    "吉隆坡":[3.1390,101.6869],"新德里":[28.6139,77.2090],"孟买":[19.0760,72.8777],
    "莫斯科":[55.7558,37.6173],"圣彼得堡":[59.9343,30.3351],"伦敦":[51.5074,-0.1278],
    "巴黎":[48.8566,2.3522],"柏林":[52.5200,13.4050],"罗马":[41.9028,12.4964],
    "马德里":[40.4168,-3.7038],"阿姆斯特丹":[52.3676,4.9041],"布鲁塞尔":[50.8503,4.3517],
    "维也纳":[48.2082,16.3738],"苏黎世":[47.3769,8.5417],"斯德哥尔摩":[59.3293,18.0686],
    "赫尔辛基":[60.1699,24.9384],"华沙":[52.2297,21.0122],"布拉格":[50.0755,14.4378],
    "布达佩斯":[47.4979,19.0402],"雅典":[37.9838,23.7275],"伊斯坦布尔":[41.0082,28.9784],
    "开罗":[30.0444,31.2357],"约翰内斯堡":[-26.2041,28.0473],"内罗毕":[-1.2921,36.8219],
    "纽约":[40.7128,-74.0060],"洛杉矶":[34.0522,-118.2437],"旧金山":[37.7749,-122.4194],
    "芝加哥":[41.8781,-87.6298],"华盛顿":[38.9072,-77.0369],"西雅图":[47.6062,-122.3321],
    "休斯顿":[29.7604,-95.3698],"迈阿密":[25.7617,-80.1918],"波士顿":[42.3601,-71.0589],
    "丹佛":[39.7392,-104.9903],"多伦多":[43.6532,-79.3832],"温哥华":[49.2827,-123.1207],
    "蒙特利尔":[45.5017,-73.5673],"墨西哥城":[19.4326,-99.1332],"圣保罗":[-23.5505,-46.6333],
    "布宜诺斯艾利斯":[-34.6037,-58.3816],"里约热内卢":[-22.9068,-43.1729],
    "利马":[-12.0464,-77.0428],"波哥大":[4.7110,-74.0721],"圣地亚哥":[-33.4489,-70.6693],
    "悉尼":[-33.8688,151.2093],"墨尔本":[-37.8136,144.9631],"奥克兰":[-36.8485,174.7633],
    "惠灵顿":[-41.2865,174.7762],"珀斯":[-31.9505,115.8605],"夏威夷":[21.3069,-157.8583],
    "安克雷奇":[61.2181,-149.9003],"费尔班克斯":[64.8378,-147.7164],
    "关岛":[13.4443,144.7937],"斐济":[-17.7134,178.0650]
  };

  // ============================================================
  // 通信模式参考
  // ============================================================
  Module.MODES_REF = [
    {cat:"模拟语音",modes:[
      {a:"SSB",n:"单边带",d:"最常用的HF语音模式，分为LSB(40m及以下)和USB(20m及以上)"},
      {a:"AM",n:"调幅",d:"传统调幅模式，带宽6kHz，音质较好但效率低"},
      {a:"FM",n:"调频",d:"VHF/UHF最常用模式，带宽12.5/25kHz，音质优良"}
    ]},
    {cat:"数字模式",modes:[
      {a:"CW",n:"等幅电报",d:"最古老的数字模式，效率最高，带宽仅150Hz"},
      {a:"RTTY",n:"无线电传",d:"FSK模式，170Hz频移，45.45波特"},
      {a:"PSK31",n:"相移键控31",d:"窄带数字模式，31.25波特，适合低功率通信"},
      {a:"FT8",n:"FT8",d:"WSJT-X弱信号数字模式，8秒周期，适合低功率DX"},
      {a:"FT4",n:"FT4",d:"WSJT-X快速数字模式，4秒周期，适合竞赛"},
      {a:"JT65",n:"JT65",d:"EME弱信号模式，60秒周期"},
      {a:"JT9",n:"JT9",d:"极弱信号HF模式，60秒周期"},
      {a:"WSPR",n:"WSPR",d:"弱信号传播报告，120秒周期，用于传播研究"}
    ]},
    {cat:"数字语音",modes:[
      {a:"DMR",n:"数字移动无线电",d:"时隙TDMA，12.5kHz带宽，支持双时隙"},
      {a:"C4FM",n:"连续4电平FM",d:"Yaesu System Fusion模式，VHF/UHF数字语音"},
      {a:"D-STAR",n:"D-STAR",d:"Icom数字模式，6.25kHz带宽，支持互联网网关"}
    ]},
    {cat:"其他",modes:[
      {a:"SSTV",n:"慢扫描电视",d:"图像传输模式，传输一幅图像需数分钟"},
      {a:"ATV",n:"业余电视",d:"快扫描电视，传输实时视频信号"}
    ]}
  ];

  // ============================================================
  // 默认时钟
  // ============================================================
  Module.DEFAULT_CLOCKS = [
    {name:"UTC",tz:"UTC"},{name:"北京",tz:"Asia/Shanghai"},
    {name:"东京",tz:"Asia/Tokyo"},{name:"悉尼",tz:"Australia/Sydney"},
    {name:"伦敦",tz:"Europe/London"},{name:"纽约",tz:"America/New_York"}
  ];

  // ============================================================
  // RST 信号报告
  // ============================================================
  Module.R_READABILITY = ['','不可辨','勉强可辨','可辨但困难','可辨，有困难','完美可辨'];
  Module.S_STRENGTH = ['','极微弱','很微弱','微弱','弱','较好','好','相当强','强','很强','极强'];
  Module.T_TONE = ['','粗糙直流','非常粗糙','粗糙低频交流','粗糙交流','带调制交流','调制好，有杂音','接近直流，轻微调制','好的直流，有轻微调制','极好的直流，低杂音','完美直流'];

  // ============================================================
  // 核心计算函数
  // ============================================================
  Module.freqToMHz = function(val, unit) {
    val = parseFloat(val);
    if (isNaN(val)) return NaN;
    if (unit === 'kHz') return val / 1000;
    if (unit === 'GHz') return val * 1000;
    return val;
  };

  Module.freqToBand = function(freqMHz) {
    for (var i = 0; i < Module.BANDS.length; i++) {
      var b = Module.BANDS[i];
      if (freqMHz >= b.f_low && freqMHz <= b.f_high) return b;
    }
    return null;
  };

  Module.getSpectrumCat = function(freqMHz) {
    for (var i = 0; i < Module.SPECTRUM_CATS.length; i++) {
      var cat = Module.SPECTRUM_CATS[i];
      if (freqMHz >= cat[0] && freqMHz < cat[1]) return cat[2];
    }
    return null;
  };

  Module.wavelength = function(freqMHz) {
    return Module.C / (freqMHz * 1e6);
  };

  Module.dipoleLength = function(freqMHz) {
    var wl = Module.wavelength(freqMHz);
    return { halfWave: wl / 2, eachLeg: wl / 4 * 0.95 };
  };

  Module.quarterWaveLength = function(freqMHz) {
    return Module.wavelength(freqMHz) / 4 * 0.95;
  };

  Module.gridToLatLon = function(grid) {
    grid = grid.toUpperCase().trim();
    if (grid.length < 4 || !/^[A-Z]{2}[0-9]{2}/.test(grid)) return null;
    var lon = (grid.charCodeAt(0) - 65) * 20 - 180;
    var lat = (grid.charCodeAt(1) - 65) * 10 - 90;
    var lonS = parseInt(grid[2]) * 2;
    var latS = parseInt(grid[3]) * 1;
    var lonR = 0, latR = 0;
    if (grid.length >= 6) {
      lonR = (grid.charCodeAt(4) - 65) * (5/60);
      latR = (grid.charCodeAt(5) - 65) * (2.5/60);
    }
    var lonC = lon + lonS + lonR + (grid.length >= 6 ? 5/120 : 1);
    var latC = lat + latS + latR + (grid.length >= 6 ? 2.5/120 : 0.5);
    return { lat: latC, lon: lonC };
  };

  Module.latLonToGrid = function(lat, lon) {
    if (lat < -90 || lat > 90 || lon < -180 || lon > 180) return null;
    var lonA = lon + 180;
    var latA = lat + 90;
    var g1 = Math.floor(lonA / 20);
    var g2 = Math.floor(latA / 10);
    var lonR = lonA - g1 * 20;
    var latR = latA - g2 * 10;
    var g3 = Math.floor(lonR / 2);
    var g4 = Math.floor(latR / 1);
    var lonR2 = lonR - g3 * 2;
    var latR2 = latR - g4;
    var g5 = Math.floor(lonR2 / (5/60));
    var g6 = Math.floor(latR2 / (2.5/60));
    var grid = String.fromCharCode(65 + g1) + String.fromCharCode(65 + g2) + g3 + g4;
    if (g5 >= 0 && g5 < 24 && g6 >= 0 && g6 < 24) {
      grid += String.fromCharCode(65 + g5) + String.fromCharCode(65 + g6);
    }
    return grid;
  };

  Module.distanceBearing = function(lat1, lon1, lat2, lon2) {
    var R = 6371;
    var dLat = (lat2 - lat1) * Math.PI / 180;
    var dLon = (lon2 - lon1) * Math.PI / 180;
    var a = Math.sin(dLat/2)**2 + Math.cos(lat1*Math.PI/180) * Math.cos(lat2*Math.PI/180) * Math.sin(dLon/2)**2;
    var c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    var dist = R * c;
    var brng = Math.atan2(Math.sin(dLon)*Math.cos(lat2*Math.PI/180), Math.cos(lat1*Math.PI/180)*Math.sin(lat2*Math.PI/180)-Math.sin(lat1*Math.PI/180)*Math.cos(lat2*Math.PI/180)*Math.cos(dLon));
    brng = (brng * 180 / Math.PI + 360) % 360;
    return { distance: dist, bearing: brng };
  };

  Module.dbmToWatts = function(dbm) { return Math.pow(10, dbm / 10) / 1000; };
  Module.wattsToDbm = function(w) { return 10 * Math.log10(w * 1000); };
  Module.wattsToDbw = function(w) { return 10 * Math.log10(w); };
  Module.dbwToWatts = function(dbw) { return Math.pow(10, dbw / 10); };
  Module.dbmToDbw = function(dbm) { return dbm - 30; };

  Module.swrFromPower = function(fw, rw) {
    if (fw <= 0 || rw < 0 || rw > fw) return null;
    var refl = Math.sqrt(rw / fw);
    return (1 + refl) / (1 - refl);
  };

  Module.swrToReflectPower = function(swr, fw) {
    if (swr <= 1 || fw <= 0) return null;
    var refl = (swr - 1) / (swr + 1);
    return fw * refl * refl;
  };

  Module.coaxAttenuation = function(type, freqMHz, lengthM) {
    var data = Module.COAX_TYPES[type];
    if (!data) return null;
    var freqs = Object.keys(data).map(Number).sort(function(a,b){return a-b;});
    if (freqMHz <= freqs[0]) return data[freqs[0]] / 100 * lengthM;
    if (freqMHz >= freqs[freqs.length-1]) return data[freqs[freqs.length-1]] / 100 * lengthM;
    var lo = freqs[0], hi = freqs[freqs.length-1];
    for (var i = 0; i < freqs.length-1; i++) {
      if (freqMHz >= freqs[i] && freqMHz <= freqs[i+1]) { lo = freqs[i]; hi = freqs[i+1]; break; }
    }
    var ratio = (freqMHz - lo) / (hi - lo);
    var atten100 = data[lo] + ratio * (data[hi] - data[lo]);
    return atten100 / 100 * lengthM;
  };

  Module.morseEncode = function(text) {
    text = text.replace(/[\uff00-\uffef]/g, function(c) { return String.fromCharCode(c.charCodeAt(0) - 0xFEE0); });
    var result = '';
    for (var i = 0; i < text.length; i++) {
      var ch = text[i].toUpperCase();
      if (ch === ' ') { result += '/ '; continue; }
      if (Module.MORSE_CODE[ch]) { result += Module.MORSE_CODE[ch] + ' '; }
      else { result += '# '; }
    }
    return result.trim();
  };

  Module.morseDecode = function(morse) {
    var parts = morse.trim().split(/\s+/);
    var result = '';
    for (var i = 0; i < parts.length; i++) {
      var p = parts[i];
      if (p === '/') { result += ' '; continue; }
      var ch = Module.MORSE_REVERSE[p.replace(/·/g,'.').replace(/-/g,'-')];
      result += ch || '?';
    }
    return result;
  };

  Module.parseQth = function(qth) {
    if (!qth) return null;
    qth = qth.trim();
    var gridMatch = qth.match(/^([A-Za-z]{2}\d{2}[A-Za-z]{0,2})$/);
    if (gridMatch) {
      var c = Module.gridToLatLon(gridMatch[1]);
      if (c) { c.source = 'grid'; c.grid = gridMatch[1].toUpperCase(); }
      return c || null;
    }
    var llMatch = qth.match(/^(-?\d+\.?\d*)\s*[,，\s]\s*(-?\d+\.?\d*)$/);
    if (llMatch) return { lat: parseFloat(llMatch[1]), lon: parseFloat(llMatch[2]), source: 'coords' };
    var city = Module.CITY_COORDS[qth] || Module.CITY_COORDS[Object.keys(Module.CITY_COORDS).find(function(k){return k.toLowerCase() === qth.toLowerCase();})];
    if (city) return { lat: city[0], lon: city[1], source: 'city', cityName: qth };
    return null;
  };

  // 暴露到全局
  global.HAM = global.HAM || {};
  global.HAM.Core = Module;

})(window);