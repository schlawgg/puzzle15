"""
main.py — Точка входу програми «Гра у 15»

Ініціалізує кореневе вікно tkinter та запускає головний клас PuzzleApp.

Запуск:
    python main.py
    
"""

import tkinter as tk
from app import PuzzleApp


if __name__ == "__main__":
    root = tk.Tk()
    app  = PuzzleApp(root)
    root.mainloop()
