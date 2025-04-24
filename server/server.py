import asyncio
import websockets
import json
from game.game import Game
from game.board import clear_bottom_row
import settings

async def handle_client(websocket):
    player_fast_drop = False
    game = Game()

    while True:
        try:
            msg = await asyncio.wait_for(websocket.recv(), timeout=0.1) #increase for level diff towards 0.01
            data = json.loads(msg)
            action = data.get("action")

            if action == "reset":
                player_fast_drop = False
                game = Game()
            elif action == "fast_drop":
                player_fast_drop = data.get("active", False)
            elif action and not game.game_over:
                game.apply_input(action)
        except asyncio.TimeoutError:
            pass                    #allowed to timeout without new data

        if not game.game_over:
            if game.events:
                await websocket.send(json.dumps({
                    "message_type": "animation_event",
                    "animations": game.events
                }))
                game.events = []
                await asyncio.sleep(0.6) # let animation finish
                if game.clear_bottom_row:
                    clear_bottom_row(game.board)
                    game.clear_bottom_row = False
                    game.continue_after_animation()
                continue

            if player_fast_drop:
                for _ in range(settings.FAST_DROP_SPEED):
                    locked = game.apply_input("fast_drop")
                    if locked or game.game_over:
                        break
            else:
                game.step()

            await websocket.send(json.dumps({
                "message_type": "state_update",
                "block": {"x": game.block.x, "y": game.block.y, "color": game.block.color},
                "score": game.score,
                "game_over": game.game_over,
                "board": game.board
            }))

        await asyncio.sleep(0.1)

async def main():
    async with websockets.serve(handle_client, "0.0.0.0", 8000):
        print("Server started on ws://0.0.0.0:8000")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())