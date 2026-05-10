import tkinter as tk
from tkinter import messagebox, font as tkfont

from model  import PuzzleModel
from solver import PuzzleSolver
from timer  import GameTimer
from saver  import ResultSaver


class PuzzleApp:
    BG         = "#24244e"
    TILE_BG    = "#313244"
    TILE_FG    = "#cdd6f4"
    TILE_HOVER = "#45475a"
    EMPTY_BG   = "#181825"
    ACCENT     = "#ffffff"
    SUCCESS    = "#a6e3a1"
    TEXT_MUTED = "#6c7086"
    PANEL_BG   = "#181825"

    #константи відображення
    TILE_SIZE  = 100   #розмір однієї плитки у пікселях
    PAD        = 6     #відступ між плитками
    ANIM_DELAY = 350   #затримка між кроками авто-розв'язання (мс)

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Гра у 15")
        self.root.resizable(False, False)
        self.root.configure(bg=self.BG)

        self.model  = PuzzleModel()
        self.solver = PuzzleSolver()
        self.timer  = GameTimer()
        self.saver  = ResultSaver()

        self.moves: int = 0
        self._solving:        bool            = False
        self._solution_steps: list[list[int]] = []
        self._step_idx:       int             = 0

        #Завантажуємо найкращий результат із файлу (якщо є)
        self._best: tuple[int, str] | None = ResultSaver.load_best()

        self._build_menu()
        self._build_ui()
        self.model.shuffle()
        self._refresh_board()
        self._tick()

    #побудова меню

    def _build_menu(self) -> None:
        menubar = tk.Menu(self.root, bg=self.PANEL_BG, fg=self.TILE_FG,
                          activebackground=self.TILE_HOVER,
                          activeforeground=self.ACCENT,
                          relief="flat", bd=0)

        #Меню «Гра»
        game_menu = tk.Menu(menubar, tearoff=0,
                            bg=self.PANEL_BG, fg=self.TILE_FG,
                            activebackground=self.TILE_HOVER,
                            activeforeground=self.ACCENT)
        game_menu.add_command(label="Нова гра        Ctrl+N", command=self._new_game)
        game_menu.add_command(label="Авто-розв'язання  Ctrl+S", command=self._auto_solve)
        game_menu.add_separator()
        game_menu.add_command(label="Зберегти результат  Ctrl+D", command=self._save_result)
        game_menu.add_separator()
        game_menu.add_command(label="Вийти              Alt+F4", command=self._quit)
        menubar.add_cascade(label="Гра", menu=game_menu)

        #Меню «Про гру»
        about_menu = tk.Menu(menubar, tearoff=0,
                             bg=self.PANEL_BG, fg=self.TILE_FG,
                             activebackground=self.TILE_HOVER,
                             activeforeground=self.ACCENT)
        about_menu.add_command(label="Про програму", command=self._show_about)
        about_menu.add_command(label="Правила гри", command=self._show_rules)
        about_menu.add_separator()
        menubar.add_cascade(label="Довідка", menu=about_menu)

        self.root.config(menu=menubar)

        #Клавіатурні скорочення
        self.root.bind("<Control-n>", lambda _: self._new_game())
        self.root.bind("<Control-s>", lambda _: self._auto_solve())
        self.root.bind("<Control-d>", lambda _: self._save_result())
        self.root.bind("<Control-r>", lambda _: self._show_rules())
    #побудова основного UI

    def _build_ui(self) -> None:
        #Заголовок
        tk.Label(
            self.root, text="Гра у 15",
            bg=self.BG, fg=self.ACCENT,
            font=("Segoe UI", 22, "bold")
        ).pack(pady=(18, 4))

        #Панель статистики (ходи + час)
        stat_frame = tk.Frame(self.root, bg=self.PANEL_BG)
        stat_frame.pack(fill="x", padx=24, pady=(14, 2))

        self._moves_var = tk.StringVar(value="Ходів: 0")
        self._time_var  = tk.StringVar(value="Час: 00:00")

        for var, side in [(self._moves_var, "left"), (self._time_var, "right")]:
            tk.Label(
                stat_frame, textvariable=var,
                bg=self.PANEL_BG, fg=self.TILE_FG,
                font=("Segoe UI", 13, "bold"),
                padx=16, pady=6
            ).pack(side=side)

        #Рядок рекорду
        stat_frame = tk.Frame(self.root, bg=self.PANEL_BG)
        stat_frame.pack(fill="x", padx=24, pady=(14, 2))

        self._record_var = tk.StringVar()
        self._update_record_label()

        for var, side in [(self._record_var, "left")]:
            tk.Label(
                stat_frame, textvariable=var,
                bg=self.PANEL_BG, fg=self.TILE_FG,
                font=("Segoe UI", 13, "bold"),
                padx=16, pady=6
            ).pack(side=side)

        #Ігрове поле (Canvas)
        board_px = self.model.SIZE * self.TILE_SIZE + (self.model.SIZE + 1) * self.PAD
        self._canvas = tk.Canvas(
            self.root,
            width=board_px, height=board_px,
            bg=self.PANEL_BG, highlightthickness=0
        )
        self._canvas.pack(padx=24, pady=6)
        self._canvas.bind("<Button-1>", self._on_click)
        self._canvas.bind("<Motion>",   self._on_hover)

        self._tile_rects: list[int]    = []
        self._tile_texts: list[int]    = []
        self._hover_tile: int | None   = None
        self._init_tiles()

        #Рядок повідомлень
        self._msg_var = tk.StringVar(value="")
        tk.Label(
            self.root, textvariable=self._msg_var,
            bg=self.BG, fg=self.SUCCESS,
            font=("Segoe UI", 12, "bold"), height=2
        ).pack()

        #Кнопки керування
        btn_frame = tk.Frame(self.root, bg=self.BG)
        btn_frame.pack(pady=(0, 18))

        buttons = [
            ("🔀  Нова гра",           self._new_game),
            ("🤖  Авто-розв'язання",   self._auto_solve),
            ("💾  Зберегти",           self._save_result),
            ("❌  Вийти",             self._quit),
        ]
        for text, cmd in buttons:
            tk.Button(
                btn_frame, text=text, command=cmd,
                bg=self.TILE_BG, fg=self.TILE_FG,
                activebackground=self.TILE_HOVER,
                activeforeground=self.ACCENT,
                font=("Segoe UI", 11),
                relief="flat", bd=0,
                padx=14, pady=7, cursor="hand2"
            ).pack(side="left", padx=6)

    def _init_tiles(self) -> None:
        self._canvas.delete("all")
        self._tile_rects.clear()
        self._tile_texts.clear()
        S = self.TILE_SIZE
        P = self.PAD
        f = tkfont.Font(family="Segoe UI", size=26, weight="bold")
        for i in range(self.model.SIZE ** 2):
            r, c = divmod(i, self.model.SIZE)
            x0 = P + c * (S + P)
            y0 = P + r * (S + P)
            rect = self._canvas.create_rectangle(
                x0, y0, x0 + S, y0 + S,
                fill=self.TILE_BG, outline="", tags=f"tile{i}"
            )
            text = self._canvas.create_text(
                x0 + S // 2, y0 + S // 2,
                text="", fill=self.TILE_FG, font=f, tags=f"tile{i}"
            )
            self._tile_rects.append(rect)
            self._tile_texts.append(text)

    def _refresh_board(self) -> None:
        for i, val in enumerate(self.model.get_board()):
            if val == 0:
                self._canvas.itemconfig(self._tile_rects[i], fill=self.EMPTY_BG)
                self._canvas.itemconfig(self._tile_texts[i], text="")
            else:
                self._canvas.itemconfig(self._tile_rects[i], fill=self.TILE_BG)
                self._canvas.itemconfig(self._tile_texts[i], text=str(val))

    #рекорд
    def _update_record_label(self) -> None:
        if self._best is None:
            self._record_var.set("🏆  Рекорд: поки що немає")
        else:
            moves, time_str = self._best
            self._record_var.set(f"🏆  Рекорд: {moves} ходів за {time_str}")

    #обробники подій
    def _tile_at(self, x: int, y: int) -> int | None:
        S = self.TILE_SIZE
        P = self.PAD
        c = (x - P) // (S + P)
        r = (y - P) // (S + P)
        if 0 <= r < self.model.SIZE and 0 <= c < self.model.SIZE:
            return r * self.model.SIZE + c
        return None

    def _on_click(self, event: tk.Event) -> None:
        if self._solving:
            return
        pos = self._tile_at(event.x, event.y)
        if pos is None or self.model.get_board()[pos] == 0:
            return
        if self.model.move(pos):
            if self.moves == 0:
                self.timer.start()
            self.moves += 1
            self._moves_var.set(f"Ходів: {self.moves}")
            self._refresh_board()
            self._check_win()

    def _on_hover(self, event: tk.Event) -> None:
        pos   = self._tile_at(event.x, event.y)
        board = self.model.get_board()
        if pos == self._hover_tile:
            return
        if self._hover_tile is not None and board[self._hover_tile] != 0:
            self._canvas.itemconfig(self._tile_rects[self._hover_tile], fill=self.TILE_BG)
        self._hover_tile = pos
        if pos is not None and board[pos] != 0 and self.model.can_move(pos):
            self._canvas.itemconfig(self._tile_rects[pos], fill=self.TILE_HOVER)

    def _check_win(self) -> None:
        if self.model.is_solved():
            self.timer.stop()
            self._msg_var.set("🎉 Вітаємо! Головоломку розв'язано!")
            elapsed = self.timer.elapsed()
            m, s = divmod(int(elapsed), 60)
            messagebox.showinfo(
                "Перемога!",
                f"Ви розв'язали головоломку!\n\n"
                f"Ходів: {self.moves}\n"
                f"Час:   {m:02d}:{s:02d}\n\n"
                f"Натисніть «Зберегти», щоб записати результат."
            )

    #команди меню/кнопок

    def _new_game(self) -> None:
        self._solving = False
        self.moves    = 0
        self.timer.reset()
        self._msg_var.set("")
        self._moves_var.set("Ходів: 0")
        self.model.shuffle()
        self._refresh_board()

    def _auto_solve(self) -> None:
        if self._solving:
            self._solving = False
            self._msg_var.set("Авто-розв'язання зупинено.")
            return
        if self.model.is_solved():
            messagebox.showinfo("Інфо", "Гра вже розв'язана!")
            return

        self._msg_var.set("🔍 Шукаю розв'язок…")
        self.root.update()

        steps = self.solver.solve(self.model.get_board())
        if steps is None:
            self._msg_var.set("❌ Розв'язок не знайдено (перевищено ліміт вузлів).")
            return

        self._solving        = True
        self._solution_steps = steps
        self._step_idx       = 1
        self.timer.start()
        self._msg_var.set(f"🤖 Авто-розв'язання… ({len(steps) - 1} ходів)")
        self._play_step()

    def _play_step(self) -> None:
        if not self._solving or self._step_idx >= len(self._solution_steps):
            self._solving = False
            self.timer.stop()
            self._check_win()
            return
        self.model.set_board(self._solution_steps[self._step_idx])
        self.moves += 1
        self._moves_var.set(f"Ходів: {self.moves}")
        self._refresh_board()
        self._step_idx += 1
        self.root.after(self.ANIM_DELAY, self._play_step)

    def _save_result(self) -> None:
        if self.moves == 0:
            messagebox.showwarning("Попередження", "Гра ще не розпочата.")
            return
        elapsed  = self.timer.elapsed()
        filename = self.saver.save(self.moves, elapsed)
        m, s     = divmod(int(elapsed), 60)

        #Оновлюємо рекорд у пам'яті та мітку, якщо результат кращий
        if self._best is None or self.moves < self._best[0]:
            self._best = (self.moves, f"{m:02d}:{s:02d}")
            self._update_record_label()

        messagebox.showinfo(
            "Збережено",
            f"Результат збережено у файл «{filename}»\n\n"
            f"Ходів: {self.moves}  |  Час: {m:02d}:{s:02d}"
        )

    def _show_rules(self) -> None:
        messagebox.showinfo(
            "Правила гри — Гра у 15",
            "🎯 МЕТА\n"
            "Розставити плитки від 1 до 15 у порядку зростання зліва направо,\n"
            "зверху вниз. Порожня клітинка має бути в правому нижньому куті.\n\n"
            "🕹️ ЯК ГРАТИ\n"
            "• Натисніть на плитку, що знаходиться поруч із порожньою клітинкою —"
            "  вона зсунеться на її місце.\n"
            "• Пересувати можна лише сусідні плитки (вгору, вниз, ліворуч, праворуч).\n"
            "• Намагайтеся розв'язати головоломку за мінімальну кількість ходів\n"
            "  і якомога швидше!\n\n"
            "🤖 АВТО-РОЗВ'ЯЗАННЯ\n"
            "Якщо зайшли у глухий кут — скористайтеся кнопкою «Авто-розв'язання».\n"
            "Програма знайде оптимальний розв'язок за алгоритмом.\n\n"
            "💾 ЗБЕРЕЖЕННЯ\n"
            "Після завершення гри натисніть «Зберегти» — результат буде записано\n"
            "у файл results.txt. Найкращий результат відображається на екрані.\n\n"
            "🔀 НОВА ГРА\n"
            "Кнопка «Нова гра» перемішує поле і скидає лічильники.\n"
            "Усі позиції гарантовано розв'язні."
    )

    def _show_about(self) -> None:
        messagebox.showinfo(
            "Про програму",
            "Гра у 15\n"
            "Курсова робота з дисципліни «Основи програмування»\n\n"
            "Студент: Малиновський Борис Дмитрович\n"
            "Група: ІП-53\n"
            "КПІ ім. І. Сікорського, 2026\n\n"
            "Алгоритм розв'язання: A* (Manhattan + Linear Conflict)\n"
            "Мова: Python 3.10+  |  GUI: tkinter"
        )

    def _quit(self) -> None:
        if messagebox.askyesno("Вихід", "Завершити роботу програми?"):
            self.timer.stop()
            self.root.destroy()

    #таймер

    def _tick(self) -> None:
        self._time_var.set(f"Час: {self.timer.format()}")
        self.root.after(1000, self._tick)