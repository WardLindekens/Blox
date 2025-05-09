import random
import settings

from .block import Block
from .utils import generate_block_color
from .board import block_collides, has_same_color_neighbor, bottom_rows_full

class Game:
    def __init__(self):
        self.board = [[0 for _ in range(settings.COLS)] for _ in range(settings.ROWS)]
        self.block = self._new_block()
        self.score = 0
        self.game_over = False
        self.color_history = []
        self.events = []
        self.clear_bottom_row = False
        self.level = 1
        self.blocks_placed = 0
        self.score_last_levelup = 0
        self.block_placed = False #To know when to play sound

    def _new_block(self):
        return Block(settings.COLS // 2, 0, random.randint(1, 5))

    def update_level(self):
        score_threshold = self.score_last_levelup + (self.level ** 1.5) * settings.SCORE_THRESHOLD
        block_threshold = settings.BLOCKS_PLACED_THRESHOLD + (self.level * 8)

        if self.score > score_threshold or self.blocks_placed > block_threshold:
            self.level += 1
            self.blocks_placed = 0
            self.score_last_levelup = self.score

    def step(self): #Return block locked afterwards
        self.block.y += 1
        if block_collides(self.board, self.block.x, self.block.y):
            self.block.y -= 1
            self.lock_block()
            if not self.game_over:
                self.check_bonus()
                cleared = bottom_rows_full(self.board, self.events)
                if cleared:
                    self.clear_bottom_row = True
                    self.score += cleared * self.level
                else:    
                    self.spawn_block()
            return True
        return False

    def apply_input(self, action):
        x, y = self.block.x, self.block.y
        if action == "move_left" and x > 0 and not block_collides(self.board, x - 1, y):
            self.block.x -= 1
        elif action == "move_right" and x < settings.COLS - 1 and not block_collides(self.board, x + 1, y):
            self.block.x += 1
        elif action == "fast_drop":
            self.score += 1 * self.level
            return self.step()
        return False
    
    def lock_block(self):
        x, y = self.block.x, self.block.y
        self.board[y][x] = self.block.color
        self.score += settings.BLOCK_PLACED_SCORE * self.level
        self.block_placed = True
        if has_same_color_neighbor(self.board, x, y):
            self.game_over = True

    def spawn_block(self):
        self.blocks_placed += 1
        new_color = generate_block_color(self.color_history)
        self.color_history.append(new_color)
        if len(self.color_history) > 3:
            self.color_history.pop(0)

        self.block = Block(settings.COLS // 2, 0, new_color)

        if block_collides(self.board, self.block.x, self.block.y):
            self.game_over = True

    def check_bonus(self):
        for y in range(settings.ROWS):
            for x in range(settings.COLS):
                color = self.board[y][x]
                if color == 0 or color == settings.BONUS_COLOR:
                    continue
                #Diagonal \
                if x + 3 < settings.COLS and y + 3 < settings.ROWS and \
                    self.board[y + 1][x + 1] == color and \
                    self.board[y + 2][x + 2] == color and \
                    self.board[y + 3][x + 3] == color :
                    self.board[y][x] = 6
                    self.board[y + 1][x + 1] = 6
                    self.board[y + 2][x + 2] = 6
                    self.board[y + 3][x + 3] = 6
                    self.score += settings.BONUS_SCORE * self.level
                #Diagonal /
                if x - 3 >= 0 and y + 3 < settings.ROWS and \
                    self.board[y + 1][x - 1] == color and \
                    self.board[y + 2][x - 2] == color and \
                    self.board[y + 3][x - 3] == color :
                    self.board[y][x] = 6
                    self.board[y + 1][x - 1] = 6
                    self.board[y + 2][x - 2] = 6
                    self.board[y + 3][x - 3] = 6
                    self.score += settings.BONUS_SCORE * self.level

    def continue_after_animation(self):
        if not self.game_over:
            self.spawn_block()
