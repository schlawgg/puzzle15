from datetime import datetime


class ResultSaver:
    FILE: str = "results.txt"

    @staticmethod
    def save(moves: int, elapsed: float) -> str:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        m, s = divmod(int(elapsed), 60)
        line = f"{now} | Ходів: {moves:4d} | Час: {m:02d}:{s:02d}\n"
        with open(ResultSaver.FILE, "a", encoding="utf-8") as f:
            f.write(line)
        return ResultSaver.FILE

    @staticmethod
    def load_best() -> tuple[int, str] | None:
        try:
            with open(ResultSaver.FILE, encoding="utf-8") as f:
                lines = [l.strip() for l in f if l.strip()]
            if not lines:
                return None
            best: tuple[int, str] | None = None
            for line in lines:
                parts = line.split("|")
                if len(parts) < 3:
                    continue
                moves = int(parts[1].split(":")[1].strip())
                time_str = parts[2].split(":", 1)[1].strip()
                if best is None or moves < best[0]:
                    best = (moves, time_str)
            return best
        except FileNotFoundError:
            return None