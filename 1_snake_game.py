"""Змейка (tkinter).

Управление: стрелки или WASD (работает и на русской раскладке),
пробел - пауза, R - начать заново. Чем больше съел, тем быстрее змейка.
"""

from __future__ import annotations

import random
import tkinter as tk
from pathlib import Path

CELL = 24
COLS = 20
ROWS = 20
SPEED_START = 225   # миллисекунд между шагами
SPEED_MIN = 90
RECORD_FILE = Path(__file__).with_name("snake_record.txt")

UP, DOWN, LEFT, RIGHT = (0, -1), (0, 1), (-1, 0), (1, 0)
KEYS = {
    "Up": UP, "Down": DOWN, "Left": LEFT, "Right": RIGHT,
    "w": UP, "s": DOWN, "a": LEFT, "d": RIGHT,
    "ц": UP, "ы": DOWN, "ф": LEFT, "в": RIGHT,
}


class SnakeGame:
    """Логика игры без графики (поэтому её легко тестировать)."""

    def __init__(self, cols=COLS, rows=ROWS):
        self.cols = cols
        self.rows = rows
        self.reset()

    def reset(self):
        cx, cy = self.cols // 2, self.rows // 2
        self.snake = [(cx, cy), (cx - 1, cy), (cx - 2, cy)]  # голова первая
        self.direction = RIGHT
        self.pending = RIGHT
        self.score = 0
        self.alive = True
        self.won = False
        self.food = self.spawn_food()

    def spawn_food(self):
        free = [(x, y) for x in range(self.cols) for y in range(self.rows)
                if (x, y) not in self.snake]
        return random.choice(free) if free else None

    def turn(self, new_dir):
        # нельзя развернуться на 180 градусов (змейка врежется сама в себя)
        if (new_dir[0] + self.direction[0], new_dir[1] + self.direction[1]) != (0, 0):
            self.pending = new_dir

    def step(self):
        if not self.alive:
            return
        self.direction = self.pending
        hx, hy = self.snake[0]
        new_head = (hx + self.direction[0], hy + self.direction[1])
        grow = new_head == self.food
        # если не растём, хвост освободит клетку - в неё можно зайти
        body = self.snake if grow else self.snake[:-1]

        hit_wall = not (0 <= new_head[0] < self.cols and 0 <= new_head[1] < self.rows)
        if hit_wall or new_head in body:
            self.alive = False
            return

        self.snake.insert(0, new_head)
        if grow:
            self.score += 1
            self.food = self.spawn_food()
            if self.food is None:      # всё поле занято - победа
                self.alive = False
                self.won = True
        else:
            self.snake.pop()


class SnakeApp:
    def __init__(self, root):
        self.root = root
        root.title("Змейка")
        root.resizable(False, False)

        self.game = SnakeGame()
        self.record = self.load_record()
        self.paused = False
        self.job = None

        self.label = tk.Label(root, font=("Arial", 13))
        self.label.pack(pady=4)
        self.canvas = tk.Canvas(root, width=COLS * CELL, height=ROWS * CELL,
                                bg="#1e1e1e", highlightthickness=0)
        self.canvas.pack()
        tk.Label(root, text="Стрелки/WASD - движение, Пробел - пауза, R - заново"
                 ).pack(pady=4)

        root.bind("<Key>", self.on_key)
        self.start()

    # --- рекорд ---
    @staticmethod
    def load_record() -> int:
        try:
            return int(RECORD_FILE.read_text().strip())
        except (OSError, ValueError):
            return 0

    def save_record(self):
        if self.game.score > self.record:
            self.record = self.game.score
            try:
                RECORD_FILE.write_text(str(self.record))
            except OSError:
                pass

    # --- управление ---
    def on_key(self, event):
        direction = KEYS.get(event.keysym) or KEYS.get(event.char.lower())
        if direction:
            self.game.turn(direction)
        elif event.keysym == "space" and self.game.alive:
            self.paused = not self.paused
        elif event.char.lower() in ("r", "к"):
            self.start()

    def start(self):
        if self.job:
            self.root.after_cancel(self.job)
        self.game.reset()
        self.paused = False
        self.tick()

    def tick(self):
        if not self.paused:
            self.game.step()
        self.draw()
        if self.game.alive:
            delay = max(SPEED_MIN, SPEED_START - self.game.score * 4)
            self.job = self.root.after(delay, self.tick)
        else:
            self.save_record()
            self.draw()

    # --- рисование ---
    def cell(self, pos, color):
        x, y = pos
        self.canvas.create_rectangle(x * CELL + 1, y * CELL + 1,
                                     (x + 1) * CELL - 1, (y + 1) * CELL - 1,
                                     fill=color, outline="")

    def draw(self):
        g = self.game
        self.label.config(text=f"Счёт: {g.score}     Рекорд: {max(self.record, g.score)}")
        self.canvas.delete("all")
        if g.food:
            x, y = g.food
            self.canvas.create_oval(x * CELL + 3, y * CELL + 3,
                                    (x + 1) * CELL - 3, (y + 1) * CELL - 3,
                                    fill="#e74c3c", outline="")
        for i, pos in enumerate(g.snake):
            self.cell(pos, "#7CFC00" if i == 0 else "#2ecc71")

        message = None
        if g.won:
            message = "ПОБЕДА!\nR - заново"
        elif not g.alive:
            message = "Игра окончена\nR - заново"
        elif self.paused:
            message = "ПАУЗА"
        if message:
            self.canvas.create_text(COLS * CELL // 2, ROWS * CELL // 2, text=message,
                                    fill="white", font=("Arial", 22, "bold"),
                                    justify="center")


def main():
    root = tk.Tk()
    SnakeApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
