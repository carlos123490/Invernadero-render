from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import asyncio

app = FastAPI()

# HTML de la web
html = """
<!DOCTYPE html>
<html>
<head>
<title>Invernadero en Vivo</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body { font-family: Arial; background: #1a1a1a; color: white; text-align: center; padding: 50px; }
h1 { font-size: 2em; }
.temp { font-size: 4em; color: #4CAF50; }
.status { margin-top: 30px; padding: 10px; border-radius: 8px; }
.connected { background: #2e7d32; }
.disconnected { background: #c62828; }
</style>
</head>
<body>
<h1>🌱 Invernadero en Vivo</h1>
<div class="temp">Temperatura: <span id="temp">--</span> °C</div>
<div class="temp">Humedad: <span id="hum">--</span> %</div>
<div id="status" class="status disconnected">Estado WS: Desconectado ❌</div>

<script>
let ws;
function connect() {
  ws = new WebSocket("wss://invernadero-render.onrender.com/ws");
  ws.onopen = () => {
    document.getElementById("status").className = "status connected";
    document.getElementById("status").innerHTML = "Estado WS: Conectado ✅";
  };
  ws.onmessage = (event) => {
    let data = JSON.parse(event.data);
    document.getElementById("temp").innerHTML = data.temp.toFixed(1);
    document.getElementById("hum").innerHTML = data.hum.toFixed(0);
  };
  ws.onclose = () => {
    document.getElementById("status").className = "status disconnected";
    document.getElementById("status").innerHTML = "Estado WS: Desconectado ❌";
    setTimeout(connect, 3000);
  };
}
connect();
</script>
</body>
</html>
"""

@app.get("/")
async def get():
    return HTMLResponse(html)

# ESTO ES LO QUE TE FALTABA
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            # Reenvía los datos a todos los navegadores conectados
            await websocket.send_text(data)
    except WebSocketDisconnect:
        pass
