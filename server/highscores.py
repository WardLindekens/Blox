import json
import os

HIGHSCORE_FILE = "data/highscores.json"
MAX_ENTRIES = 10

def load_highscores():
    if not os.path.exists(HIGHSCORE_FILE):
        return []
    with open(HIGHSCORE_FILE, "r") as f:
        return json.load(f)

def save_highscores(scores):
    with open(HIGHSCORE_FILE, "w") as f:
        json.dump(scores, f, indent=4)

def add_highscore(name, score):
    scores = load_highscores()
    lowest = scores[MAX_ENTRIES -1]["score"]

    if len(scores) >= MAX_ENTRIES and score <= lowest:
        return

    scores.append({"name": name, "score": score})
    scores.sort(key=lambda s: s["score"], reverse=True)
    scores = scores[:MAX_ENTRIES]
    save_highscores(scores)

def reset_highscores():
    save_highscores([])
