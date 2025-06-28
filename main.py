from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# 存訂單的記憶體清單
orders = []
# 存連線中的 websocket
clients = set()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 你可設定自己的網址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/order")
async def post_order(order: dict):
    orders.append(order)
    # 新單時推播給所有websocket連線
    for ws in clients.copy():
        try:
            await ws.send_json(order)
        except Exception:
            clients.discard(ws)
    return {"ok": True}

@app.get("/orders")
async def get_orders():
    return orders

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    clients.add(ws)
    try:
        while True:
            await ws.receive_text()  # 讓連線不會自動斷
    except Exception:
        pass
    finally:
        clients.discard(ws)
