from src.config import load_config
from src.controller.game_controller import GameController


def main() -> None:
    config = load_config("config.json")
    controller = GameController(config)
    controller.run()


if __name__ == "__main__":
    main()
