from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

clientes_web = set()

# Sirve el index.html automáticamente
app.mount("/", StaticFiles(directory=".", html=True), name="static")

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    clientes_web.add(ws)
    print("Cliente conectado")

    try:
        while True:
            data_str = await ws.receive_text()
            data = json.loads(data_str)

            # Normalizar llaves por si acaso
            data_norm = {k.lower().replace("_", "").replace(" ", ""): v for k, v in data.items()}
            print(f"[WS] Datos: {data_norm}")

            # Reenviar a todos los navegadores conectados
            for cliente in list(clientes_web):
                if cliente!= ws:
                    try:
                        await cliente.send_text(json.dumps(data_norm))
                    except:
                        clientes_web.discard(cliente)

    except WebSocketDisconnect:
        clientes_web.discard(ws)
        print("Cliente desconectado")

@app.get("/health")
def health():
    return {"status": "ok"}