from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# 用來儲存訂單（只存在記憶體，伺服器重啟會消失）
orders = []
# 用來存放所有連線中的 WebSocket
clients = set()

# 加入 CORS 中介軟體，讓跨網域請求可以通過
app.add_middleware(
    CORSMiddleware,
   allow_origins=[
    "https://comfy-puffpuff-2afc75.netlify.app",
],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 提供外部送訂單（POST）
@app.post("/order")
async def post_order(order: dict):
    orders.append(order)
    # 新單推播給所有 WebSocket 連線
    for ws in clients.copy():
        try:
            await ws.send_json(order)
        except Exception:
            clients.discard(ws)
    return {"ok": True}

# 提供所有訂單查詢（GET）
@app.get("/orders")
async def get_orders():
    return orders

# WebSocket 連線（讓 app 實時接收新訂單）
@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    clients.add(ws)
    try:
        while True:
            # 這裡只是佔用住連線不讓他自動斷線，沒做接收任何訊息
            await ws.receive_text()
    except Exception:
        pass
    finally:
        clients.discard(ws)

# 本地測試時可以加這段，部署在 Railway 可不用
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
