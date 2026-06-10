from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI()

# Estados de los 4 relés
reles = {"r1":0, "r2":0, "r3":0, "r4":0}
timers = {"r1":0, "r2":0, "r3":0, "r4":0}
timer_start = {"r1":0, "r2":0, "r3":0, "r4":0}
temp = 25.0
hum = 60.0
import time

html = """
<!DOCTYPE html>
<html>
<head>
<title>INVERNADERO PRO HTTP</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Segoe UI', Arial; background: #0f1b2e; color: white; padding: 15px; }
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
h1 { color: #4CAF50; font-size: 1.5em; }
.time-temp { text-align: right; font-size: 0.9em; }
.grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; max-width: 800px; margin: auto; }
.card { background: #1e2a3a; border-radius: 12px; padding: 15px; border: 2px solid #2a3f5f; }
.card h3 { color: #64b5f6; margin-bottom: 10px; }
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
#status { text-align: center; padding: 12px; border-radius: 8px; margin-top: 20px; font-weight: bold; background: #2e7d32; }
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
  <div class="card">
    <h3>Bomba 1</h3>
    <div class="status" id="s1">Estado: APAGADO</div>
    <div class="switch">
      <button class="btn-on" onclick="send(1,1)">ENCENDER</button>
      <button class="btn-off" onclick="send(1,0)">APAGADO</button>
    </div>
    <div class="timer" id="t1">00:00:00</div>
    <div class="timer-btns">
      <button onclick="startTimer(1)">START</button>
      <button onclick="send(1,0)">STOP</button>
    </div>
    <div class="timer-set">
      <input type="number" id="m1" placeholder="Min" min="0">
      <input type="number" id="s1in" placeholder="Seg" min="0" max="59">
      <button onclick="setTimer(1)">Set</button>
    </div>
  </div>

  <div class="card">
    <h3>Ventilador</h3>
    <div class="status" id="s2">Estado: APAGADO</div>
    <div class="switch">
      <button class="btn-on" onclick="send(2,1)">ENCENDER</button>
      <button class="btn-off" onclick="send(2,0)">APAGADO</button>
    </div>
    <div class="timer" id="t2">00:00:00</div>
    <div class="timer-btns">
      <button onclick="startTimer(2)">START</button>
      <button onclick="send(2,0)">STOP</button>
    </div>
    <div class="timer-set">
      <input type="number" id="m2" placeholder="Min" min="0">
      <input type="number" id="s2in" placeholder="Seg" min="0" max="59">
      <button onclick="setTimer(2)">Set</button>
    </div>
  </div>

  <div class="card">
    <h3>Luz LED</h3>
    <div class="status" id="s3">Estado: APAGADO</div>
    <div class="switch">
      <button class="btn-on" onclick="send(3,1)">ENCENDER</button>
      <button class="btn-off" onclick="send(3,0)">APAGADO</button>
    </div>
    <div class="timer" id="t3">00:00:00</div>
    <div class="timer-btns">
      <button onclick="startTimer(3)">START</button>
      <button onclick="send(3,0)">STOP</button>
    </div>
    <div class="timer-set">
      <input type="number" id="m3" placeholder="Min" min="0">
      <input type="number" id="s3in" placeholder="Seg" min="0" max="59">
      <button onclick="setTimer(3)">Set</button>
    </div>
  </div>

  <div class="card">
    <h3>Bomba 2</h3>
    <div class="status" id="s4">Estado: APAGADO</div>
    <div class="switch">
      <button class="btn-on" onclick="send(4,1)">ENCENDER</button>
      <button class="btn-off" onclick="send(4,0)">APAGADO</button>
    </div>
    <div class="timer" id="t4">00:00:00</div>
    <div class="timer-btns">
      <button onclick="startTimer(4)">START</button>
      <button onclick="send(4,0)">STOP</button>
    </div>
    <div class="timer-set">
      <input type="number" id="m4" placeholder="Min" min="0">
      <input type="number" id="s4in" placeholder="Seg" min="0" max="59">
      <button onclick="setTimer(4)">Set</button>
    </div>
  </div>
</div>

<div id="status">Estado: Conectado ✅</div>

<script>
let timerVals = {1:0, 2:0, 3:0, 4:0};

function send(relay, state) {
  fetch(`/toggle?r=r${relay}&s=${state}`);
}

function setTimer(r) {
  let m = parseInt(document.getElementById("m"+r).value) || 0;
  let s = parseInt(document.getElementById("s"+r+"in").value) || 0;
  let total = m*60 + s;
  timerVals[r] = total;
  fetch(`/timer?r=r${r}&sec=${total}`);
}

function startTimer(r) {
  if(timerVals[r] > 0) fetch(`/timer?r=r${r}&sec=${timerVals[r]}`);
}

// Actualizar datos cada 2 seg
setInterval(() => {
  fetch("/getdata")
 .then(r => r.json())
 .then(d => {
    document.getElementById("temp").innerHTML = d.temp.toFixed(1);
    document.getElementById("hum").innerHTML = d.hum.toFixed(0);
    document.getElementById("time").innerHTML = new Date().toLocaleTimeString();

    for(let i=1; i<=4; i++) {
      let st = d["r"+i];
      document.getElementById("s"+i).className = "status " + (st?"on":"off");
      document.getElementById("s"+i).innerHTML = "Estado: " + (st?"ENCENDIDO":"APAGADO");

      let sec = d["t"+i];
      if(sec < 0) sec = 0;
      let h = Math.floor(sec/3600);
      let m = Math.floor((sec%3600)/60);
      let s = sec%60;
      document.getElementById("t"+i).innerHTML =
        String(h).padStart(2,'0')+":"+String(m).padStart(2,'0')+":"+String(s).padStart(2,'0');
    }
  });
}, 2000);
</script>
</body>
</html>
"""

@app.get("/")
async def home():
    return HTMLResponse(html)

@app.get("/toggle")
async def toggle(r: str, s: int):
    reles[r] = s
    if s == 0: timers[r] = 0
    return "OK"

@app.get("/timer")
async def timer(r: str, sec: int):
    timers[r] = sec
    timer_start[r] = time.time()
    reles[r] = 1
    return "OK"

@app.get("/data")
async def data(t: float, h: float):
    global temp, hum
    temp = t
    hum = h

    # Calcular timers restantes
    now = time.time()
    for r in ["r1","r2","r3","r4"]:
        if timers[r] > 0:
            elapsed = now - timer_start[r]
            remaining = timers[r] - elapsed
            if remaining <= 0:
                timers[r] = 0
                reles[r] = 0

    # Responder al ESP32: estados de relés
    return f"{reles['r1']},{reles['r2']},{reles['r3']},{reles['r4']}"

@app.get("/getdata")
async def getdata():
    now = time.time()
    t_rem = {}
    for r in ["r1","r2","r3","r4"]:
        if timers[r] > 0:
            elapsed = now - timer_start[r]
            t_rem[r] = max(0, int(timers[r] - elapsed))
        else:
            t_rem[r] = 0

    return {
        "temp": temp,
        "hum": hum,
        "r1": reles["r1"], "t1": t_rem["r1"],
        "r2": reles["r2"], "t2": t_rem["r2"],
        "r3": reles["r3"], "t3": t_rem["r3"],
        "r4": reles["r4"], "t4": t_rem["r4"]
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
