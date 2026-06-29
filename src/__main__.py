
import sys

from pathlib import Path

from src.config import load_config
from src.controller.game_controller import GameController


def main() -> None:
    if hasattr(sys, '_MEIPASS') or getattr(sys, 'frozen', False):
        base_path = Path(sys.executable).parent
    else:
        base_path = Path(__file__).resolve().parent.parent

    config_path = base_path / "config.json"
    config = load_config(str(config_path))

    controller = GameController(config)
    controller.run()


if __name__ == "__main__":
    try:
        main()
    except BaseException as e:
        sys.exit(f"Error: {e}")
