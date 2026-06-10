from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

app = FastAPI()
clients = []

html = """
<!DOCTYPE html>
<html>
<head>
<title>INVERNADERO PRO</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Segoe UI', Arial; background: #0f1b2e; color: white; padding: 15px; }
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
h1 { color: #4CAF50; font-size: 1.5em; }
.time-temp { text-align: right; font-size: 0.9em; }
.grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; max-width: 800px; margin: auto; }
.card { background: #1e2a3a; border-radius: 12px; padding: 15px; border: 2px solid #2a3f5f; }
.card h3 { color: #64b5f6; margin-bottom: 10px; font-size: 1.1em; }
.status { font-size: 0.85em; margin-bottom: 8px; }
.status.on { color: #4CAF50; }
.status.off { color: #f44336; }
.switch { display: flex; gap: 8px; margin: 10px 0; }
.switch button { flex: 1; padding: 12px; border: none; border-radius: 8px; font-weight: bold; cursor: pointer; }
.btn-on { background: #4CAF50; color: white; }
.btn-off { background: #555; color: #ccc; }
.timer { background: #162032; padding: 10px; border-radius: 8px; text-align: center; font-size: 1.8em; font-family: monospace; margin: 10px 0; }
.timer-btns { display: flex; gap: 8px; }
.timer-btns button { flex: 1; padding: 8px; border: none; border-radius: 6px; background: #2196F3; color: white; cursor: pointer; }
.timer-set { display: flex; gap: 5px; margin-top: 8px; }
.timer-set input { flex: 1; padding: 8px; border-radius: 6px; border: none; background: #0f1b2e; color: white; text-align: center; }
.timer-set button { padding: 8px 15px; background: #4CAF50; border: none; border-radius: 6px; color: white; cursor: pointer; }
.prog { margin-top: 12px; padding-top: 12px; border-top: 1px solid #2a3f5f; }
.prog input { width: 60px; padding: 6px; margin: 0 3px; background: #0f1b2e; border: 1px solid #3a4f6f; color: white; border-radius: 5px; text-align: center; }
.prog button { padding: 6px 12px; background: #FF9800; border: none; border-radius: 5px; color: white; cursor: pointer; margin-top: 5px; }
.temp-control { margin-top: 12px; }
.temp-control input { width: 70px; padding: 6px; background: #0f1b2e; border: 1px solid #3a4f6f; color: white; border-radius: 5px; }
#status { text-align: center; padding: 12px; border-radius: 8px; margin-top: 20px; font-weight: bold; }
.connected { background: #2e7d32; }
.disconnected { background: #c62828; }
@media (max-width: 600px) {.grid { grid-template-columns: 1fr; } }
</style>
</head>
<body>
<div class="header">
  <h1>🌱 INVERNADERO PRO</h1>
  <div class="time-temp">
    <div id="time">--:--</div>
    <div>🌡️ <span id="temp">--</span>°C 💧 <span id="hum">--</span>%</div>
  </div>
</div>

<div class="grid">
  <!-- RELÉ 1 -->
  <div class="card">
    <h3>Bomba 1</h3>
    <div class="status" id="s1">Estado: APAGADO</div>
    <div class="switch">
      <button class="btn-on" onclick="send(0,'toggle',1)">ENCENDER</button>
      <button class="btn-off" onclick="send(0,'toggle',0)">APAGADO</button>
    </div>
    <div class="timer" id="t1">00:00:00</div>
    <div class="timer-btns">
      <button onclick="send(0,'timer',1)">START</button>
      <button onclick="send(0,'toggle',0)">STOP</button>
    </div>
    <div class="timer-set">
      <input type="number" id="m1" placeholder="Min" min="0">
      <input type="number" id="s1in" placeholder="Seg" min="0" max="59">
      <button onclick="setTimer(0)">Set</button>
    </div>
    <div class="prog">
      <b>PROGRAMADO DIARIO</b><br>
      H: <input type="number" id="h1" min="0" max="23"> M: <input type="number" id="min1" min="0" max="59">
      <button onclick="setProg(0)">Programar</button>
    </div>
    <div class="temp-control">
      <b>CONTROL TEMPERATURA</b><br>
      MIN: <input type="number" id="tmin1" step="0.1"> MAX: <input type="number" id="tmax1" step="0.1">
      <button onclick="setTemp(0)">Set</button>
    </div>
  </div>

  <!-- RELÉ 2 -->
  <div class="card">
    <h3>Ventilador</h3>
    <div class="status" id="s2">Estado: APAGADO</div>
    <div class="switch">
      <button class="btn-on" onclick="send(1,'toggle',1)">ENCENDER</button>
      <button class="btn-off" onclick="send(1,'toggle',0)">APAGADO</button>
    </div>
    <div class="timer" id="t2">00:00:00</div>
    <div class="timer-btns">
      <button onclick="send(1,'timer',1)">START</button>
      <button onclick="send(1,'toggle',0)">STOP</button>
    </div>
    <div class="timer-set">
      <input type="number" id="m2" placeholder="Min" min="0">
      <input type="number" id="s2in" placeholder="Seg" min="0" max="59">
      <button onclick="setTimer(1)">Set</button>
    </div>
    <div class="prog">
      <b>PROGRAMADO DIARIO</b><br>
      H: <input type="number" id="h2" min="0" max="23"> M: <input type="number" id="min2" min="0" max="59">
      <button onclick="setProg(1)">Programar</button>
    </div>
  </div>

  <!-- RELÉ 3 -->
  <div class="card">
    <h3>Luz LED</h3>
    <div class="status" id="s3">Estado: APAGADO</div>
    <div class="switch">
      <button class="btn-on" onclick="send(2,'toggle',1)">ENCENDER</button>
      <button class="btn-off" onclick="send(2,'toggle',0)">APAGADO</button>
    </div>
    <div class="timer" id="t3">00:00:00</div>
    <div class="timer-btns">
      <button onclick="send(2,'timer',1)">START</button>
      <button onclick="send(2,'toggle',0)">STOP</button>
    </div>
    <div class="timer-set">
      <input type="number" id="m3" placeholder="Min" min="0">
      <input type="number" id="s3in" placeholder="Seg" min="0" max="59">
      <button onclick="setTimer(2)">Set</button>
    </div>
  </div>

  <!-- RELÉ 4 -->
  <div class="card">
    <h3>Bomba 2</h3>
    <div class="status" id="s4">Estado: APAGADO</div>
    <div class="switch">
      <button class="btn-on" onclick="send(3,'toggle',1)">ENCENDER</button>
      <button class="btn-off" onclick="send(3,'toggle',0)">APAGADO</button>
    </div>
    <div class="timer" id="t4">00:00:00</div>
    <div class="timer-btns">
      <button onclick="send(3,'timer',1)">START</button>
      <button onclick="send(3,'toggle',0)">STOP</button>
    </div>
    <div class="timer-set">
      <input type="number" id="m4" placeholder="Min" min="0">
      <input type="number" id="s4in" placeholder="Seg" min="0" max="59">
      <button onclick="setTimer(3)">Set</button>
    </div>
  </div>
</div>

<div id="status" class="disconnected">Estado WS: Desconectado ❌</div>

<script>
let ws;
function connect() {
  ws = new WebSocket("wss://invernadero-render.onrender.com/ws");
  ws.onopen = () => {
    document.getElementById("status").className = "connected";
    document.getElementById("status").innerHTML = "Estado WS: Conectado ✅";
  };
  ws.onmessage = (event) => {
    let d = JSON.parse(event.data);
    document.getElementById("temp").innerHTML = d.temp.toFixed(1);
    document.getElementById("hum").innerHTML = d.hum.toFixed(0);
    document.getElementById("time").innerHTML = d.time || "--:--";

    for(let i=0; i<4; i++) {
      let st = d["r"+(i+1)+"State"];
      document.getElementById("s"+(i+1)).className = "status " + (st?"on":"off");
      document.getElementById("s"+(i+1)).innerHTML = "Estado: " + (st?"ENCENDIDO":"APAGADO");

      let sec = d["r"+(i+1)+"Timer"];
      if(sec < 0) sec = 0;
      let h = Math.floor(sec/3600);
      let m = Math.floor((sec%3600)/60);
      let s = sec%60;
      document.getElementById("t"+(i+1)).innerHTML =
        String(h).padStart(2,'0')+":"+String(m).padStart(2,'0')+":"+String(s).padStart(2,'0');
    }
  };
  ws.onclose = () => {
    document.getElementById("status").className = "disconnected";
    document.getElementById("status").innerHTML = "Estado WS: Desconectado ❌";
    setTimeout(connect, 3000);
  };
}

function send(relay, cmd, val) {
  if(ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({relay: relay, cmd: cmd, state: val, sec: val}));
  }
}

function setTimer(r) {
  let m = parseInt(document.getElementById("m"+(r+1)).value) || 0;
  let s = parseInt(document.getElementById("s"+(r+1)+"in").value) || 0;
  let total = m*60 + s;
  send(r, 'timer', total);
}

function setProg(r) {
  let h = parseInt(document.getElementById("h"+(r+1)).value);
  let m = parseInt(document.getElementById("min"+(r+1)).value);
  if(ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({relay: r, cmd: 'program', h: h, m: m}));
  }
}

function setTemp(r) {
  let min = parseFloat(document.getElementById("tmin"+(r+1)).value);
  let max = parseFloat(document.getElementById("tmax"+(r+1)).value);
  if(ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({relay: r, cmd: 'tempControl', min: min, max: max}));
  }
}

connect();
</script>
</body>
</html>
"""

@app.get("/")
async def get():
    return HTMLResponse(html)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            for client in clients:
                await client.send_text(data)
    except WebSocketDisconnect:
        clients.remove(websocket)
