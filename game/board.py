import settings

def block_collides(board, x, y):
    if y >= settings.ROWS:
        return True
    return board[y][x] != 0

def has_same_color_neighbor(board, x, y):
    color = board[y][x]
    for dx, dy in settings.NEIGHBOR_DELTAS:
        nx, ny = x + dx, y + dy
        if 0 <= nx < settings.COLS and 0 <= ny < settings.ROWS:
            if board[ny][nx] == color:
                return True
    return False

def bottom_rows_full(board, events): #mark that board is full, clear after animation
    full_rows = [row for row in range(settings.ROWS - settings.FULL_ROWS_TO_CLEAR, settings.ROWS) if all(cell != 0 for cell in board[row])]
    if len(full_rows) == settings.FULL_ROWS_TO_CLEAR:
        events.append({"effect": "flicker_row", "rows": board[settings.ROWS - 1]})
        return settings.CLEAR_ROW_SCORE
    return 0

def clear_bottom_row(board):
        del board[settings.ROWS - 1]
        board.insert(0, [0 for _ in range(settings.COLS)])