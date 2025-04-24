import random

def generate_block_color(history, max_repeat=2):
    while True:
        new_color = random.randint(1, 5)  # exclude bonus color (6)
        if len(history) >= max_repeat - 1 and history[-(max_repeat - 1):] == [new_color] * (max_repeat - 1):
            continue
        return new_color
