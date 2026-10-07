"""
main.py  --  the web server.

It does two jobs:
  1. runs the game clock (1 tick per second),
  2. answers the browser: "what is happening?" and "I want to do X".

The browser talks to these addresses (the API):
  GET  /api/state                 -> the whole world as text
  POST /api/join                  -> become a player
  POST /api/action                -> do something (build, vote, train, chat...)
  WS   /ws                        -> live updates every second
"""

# Allow this file to be run on its own too (not only as part of the package).
if __package__ in (None, ""):
    import os, sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    __package__ = "server"

import asyncio
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from . import config, storage

WEB_DIR = Path(__file__).resolve().parent.parent / "web"

world = storage.load_or_new()
clients: set[WebSocket] = set()


# ---------------------------------------------------------------
#  THE GAME CLOCK
# ---------------------------------------------------------------
async def game_loop():
    while True:
        try:
            world.tick(config.TICK)
        except Exception as e:       # never let one bad tick stop the game
            print("tick error:", e)
        await broadcast()
        await asyncio.sleep(config.TICK)


async def broadcast():
    if not clients:
        return
    state = world.public_state()
    dead = []
    for ws in list(clients):
        try:
            await ws.send_json(state)
        except Exception:
            dead.append(ws)
    for ws in dead:
        clients.discard(ws)


async def save_loop():
    while True:
        await asyncio.sleep(10)
        try:
            storage.save(world)
        except Exception as e:
            print("save error:", e)


@asynccontextmanager
async def lifespan(app: FastAPI):
    tasks = [asyncio.create_task(game_loop()), asyncio.create_task(save_loop())]
    yield
    for t in tasks:
        t.cancel()
    storage.save(world)          # save once more when we stop


app = FastAPI(title="G-Cards Civilizations", lifespan=lifespan)


# ---------------------------------------------------------------
#  API
# ---------------------------------------------------------------
@app.get("/api/state")
async def api_state(player_id: str | None = None):
    return world.public_state(player_id)


@app.post("/api/join")
async def api_join(request: Request):
    body = await request.json()
    name = (body.get("name") or "Player").strip()[:20]
    country = body.get("country")
    player, error = world.join(name, country)
    if error:
        return JSONResponse({"error": error}, status_code=400)
    storage.save(world)
    return {"player_id": player.id, "player": player.to_dict()}


@app.post("/api/action")
async def api_action(request: Request):
    body = await request.json()
    pid = body.get("player_id")
    action = body.get("action")
    player = world.get_player(pid or "")
    if not player:
        return JSONResponse({"error": "You are not a player."}, status_code=400)

    error = None
    if action == "vote":
        error = world.vote(pid, int(body.get("century", 12)))
    elif action == "build":
        error = world.build(pid, body.get("city"), body.get("building"))
    elif action == "train":
        error = world.train(pid, body.get("troop"), int(body.get("amount", 1)))
    elif action == "buy":
        error = world.buy(pid, body.get("material"), int(body.get("amount", 1)))
    elif action == "research":
        error = world.research(pid, body.get("tech"))
    elif action == "target":
        error = world.set_target(pid, body.get("city"))
    elif action == "pause":
        error = world.toggle_pause(pid)
    elif action == "chat":
        world.say(pid, body.get("text", ""))
    elif action == "ally":
        error = world.request_alliance(pid, body.get("other"))
    elif action == "reset":
        world.reset()
    else:
        error = "Unknown action."

    if error:
        return JSONResponse({"error": error}, status_code=400)
    storage.save(world)
    return {"ok": True, "state": world.public_state(pid)}


# ---------------------------------------------------------------
#  LIVE UPDATES (websocket)
# ---------------------------------------------------------------
@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    await ws.accept()
    clients.add(ws)
    try:
        await ws.send_json(world.public_state())
        while True:
            await ws.receive_text()      # we ignore what the browser sends here
    except WebSocketDisconnect:
        pass
    finally:
        clients.discard(ws)


# ---------------------------------------------------------------
#  THE WEB PAGE  (must be mounted LAST)
# ---------------------------------------------------------------
app.mount("/", StaticFiles(directory=WEB_DIR, html=True), name="web")


# ---------------------------------------------------------------
#  If you run THIS file directly (python server/main.py), start the server.
# ---------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
