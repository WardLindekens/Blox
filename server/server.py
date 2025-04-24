import asyncio
import json
import os
from aiohttp import web
from game.game import Game
from game.board import clear_bottom_row
import settings

async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    game = Game()

    # Send game state to client
    async def send_state():
        await ws.send_json({
            "message_type": "state_update",
            "block": {"x": game.block.x, "y": game.block.y, "color": game.block.color},
            "score": game.score,
            "game_over": game.game_over,
            "board": game.board
        })

    # Send game animations to client
    async def send_animation():
        await ws.send_json({
            "message_type": "animation_event",
            "animations": game.events
        })

    # Listen for client input
    async def input_listener():
        nonlocal game
        async for msg in ws:
            if msg.type == web.WSMsgType.TEXT:
                try:
                    data = json.loads(msg.data)
                    action = data.get("action")

                    if action == "reset":
                        game = Game()

                    elif action == "fast_drop" and data.get("active", False):
                        for _ in range(settings.FAST_DROP_SPEED):
                            locked = game.apply_input("fast_drop")
                            if locked or game.game_over:
                                break
                        await send_state()

                    elif action and not game.game_over:
                        game.apply_input(action)

                except Exception as e:
                    print("Input error:", e)

    # Main game loop
    async def game_loop():
        while True:
            if not game.game_over:
                if game.events:
                    await send_animation()
                    game.events = []
                    await asyncio.sleep(0.6)

                    if game.clear_bottom_row:
                        clear_bottom_row(game.board)
                        game.clear_bottom_row = False
                        game.continue_after_animation()
                    continue

                game.step()
                await send_state()

            await asyncio.sleep(0.2)

    # Run game and input handler concurrently
    await asyncio.gather(input_listener(), game_loop())
    return ws

# Serve index.html at root
async def index():
    return web.FileResponse(path=os.path.join("web", "index.html"))

# Create and configure the app
app = web.Application()
app.router.add_get("/", index)
app.router.add_get("/ws", websocket_handler)
app.router.add_static("/", path="web", name="static")

if __name__ == "__main__":
    web.run_app(app, port=8080)
