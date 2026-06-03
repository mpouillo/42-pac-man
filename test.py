import pyray as pr
from typing import List

# Import your protocols and necessary enums
from protocols import (
    ModelProtocol,
    ViewProtocol,
    ControllerProtocol,
    GamePhase,
    Direction,
    CellState,
    GhostType,
    CheatType
)

# Import your actual Model and Config loader
from src.config import load_config
from src.model.game_model import GameModel


class DebugView(ViewProtocol):
    """
    A 2D Pyray View implementation specifically for testing the GameModel.
    """
    def __init__(self):
        self.cell_size = 30
        self.offset_x = 50
        self.offset_y = 50

    def initialize(self, window_width: int, window_height: int) -> None:
        pr.init_window(window_width, window_height, "Pac-Man Model Tester")
        pr.set_target_fps(60)

    def render(self, model: ModelProtocol) -> None:
        pr.begin_drawing()
        pr.clear_background(pr.BLACK)

        phase = model.get_game_phase()

        if phase == GamePhase.MAIN_MENU:
            pr.draw_text("PAC-MAN DEBUGGER", 220, 200, 40, pr.YELLOW)
            pr.draw_text("Press ENTER to Start", 280, 300, 20, pr.WHITE)

        elif phase == GamePhase.PLAYING:
            self._draw_maze(model)
            self._draw_entities(model)
            self._draw_hud(model)

        elif phase == GamePhase.GAME_OVER:
            pr.draw_text("GAME OVER", 300, 250, 40, pr.RED)
            pr.draw_text("Check console for restarts", 260, 320, 20, pr.WHITE)

        elif phase == GamePhase.WIN:
            pr.draw_text("LEVEL CLEARED!", 260, 250, 40, pr.GREEN)

        pr.end_drawing()

    def shutdown(self) -> None:
        pr.close_window()

    def _draw_maze(self, model: ModelProtocol) -> None:
        maze = model.get_grid()
        if not maze:
            return

        for y, row in enumerate(maze):
            for x, cell in enumerate(row):
                px = self.offset_x + x * self.cell_size
                py = self.offset_y + y * self.cell_size

                if cell == CellState.WALL:
                    pr.draw_rectangle(px, py, self.cell_size, self.cell_size, pr.DARKBLUE)
                    pr.draw_rectangle_lines(px, py, self.cell_size, self.cell_size, pr.BLUE)
                elif cell == CellState.PACGUM:
                    pr.draw_circle(px + self.cell_size // 2, py + self.cell_size // 2, 3, pr.RAYWHITE)
                elif cell == CellState.SUPER_PACGUM:
                    pr.draw_circle(px + self.cell_size // 2, py + self.cell_size // 2, 8, pr.RAYWHITE)

    def _draw_entities(self, model: ModelProtocol) -> None:
        # Draw Pac-Man
        pacman = model.get_pacman()
        if pacman:
            px = int(self.offset_x + pacman.x * self.cell_size + self.cell_size // 2)
            py = int(self.offset_y + pacman.y * self.cell_size + self.cell_size // 2)
            pr.draw_circle(px, py, self.cell_size // 2 - 2, pr.YELLOW)

            # Simple facing indicator (draws a small black line pointing in the direction)
            dx, dy = pacman.direction.value
            pr.draw_line(px, py, px + (dx * 10), py + (dy * 10), pr.BLACK)

        # Draw Ghosts
        ghost_colors = {
            GhostType.RED: pr.RED,
            GhostType.PINK: pr.PINK,
            GhostType.BLUE: pr.SKYBLUE,
            GhostType.ORANGE: pr.ORANGE
        }

        ghosts = model._ghosts
        if ghosts:
            for ghost in ghosts:
                gx = int(self.offset_x + ghost.x * self.cell_size + self.cell_size // 2)
                gy = int(self.offset_y + ghost.y * self.cell_size + self.cell_size // 2)
                color = ghost_colors.get(ghost.type, pr.PURPLE)

                # Draw square-ish ghost body
                pr.draw_rectangle(
                    gx - self.cell_size // 2 + 2,
                    gy - self.cell_size // 2 + 2,
                    self.cell_size - 4,
                    self.cell_size - 4,
                    color
                )

                # Draw target
                tx = int(self.offset_x + ghost._target[0] * self.cell_size + self.cell_size // 2)
                ty = int(self.offset_y + ghost._target[1] * self.cell_size + self.cell_size // 2)
                pr.draw_rectangle(
                    tx - self.cell_size // 2 + 2,
                    ty - self.cell_size // 2 + 2,
                    self.cell_size - 4,
                    self.cell_size - 4,
                    pr.color_alpha(color, 0.5)
                )

                for step in ghost._path:
                    px = int(self.offset_x + step[0] * self.cell_size + self.cell_size // 2)
                    py = int(self.offset_y + step[1] * self.cell_size + self.cell_size // 2)
                    pr.draw_rectangle(
                        px - self.cell_size // 2 + 2,
                        py - self.cell_size // 2 + 2,
                        self.cell_size - 4,
                        self.cell_size - 4,
                        pr.color_alpha(pr.GREEN, 0.5)
                    )

    def _draw_hud(self, model: ModelProtocol) -> None:
        pr.draw_text(f"Score: {model.get_score()}", 20, 10, 20, pr.WHITE)
        pr.draw_text(f"Lives: {model.get_lives()}", 200, 10, 20, pr.WHITE)
        pr.draw_text(f"Time: {int(model.get_remaining_time())}", 400, 10, 20, pr.WHITE)
        pr.draw_text(f"Level: {model.get_current_level()}", 600, 10, 20, pr.WHITE)


class DebugController(ControllerProtocol):
    """
    A lightweight Controller mapping keyboard inputs to the Model.
    """
    def __init__(self, model: ModelProtocol, view: ViewProtocol):
        self.model = model
        self.view = view

    def run(self) -> None:
        # Standard size, will fit most debug mazes. Tweak if your grid is huge.
        self.view.initialize(800, 800)

        while not pr.window_should_close():
            self._handle_input()

            # Update game state
            delta_time = pr.get_frame_time()
            self.model.update(delta_time)

            # Render game state
            self.view.render(self.model)

        self.view.shutdown()

    def _handle_input(self) -> None:
        phase = self.model.get_game_phase()

        if phase == GamePhase.MAIN_MENU:
            if pr.is_key_pressed(pr.KEY_ENTER):
                self.model.set_game_phase(GamePhase.PLAYING)

        elif phase == GamePhase.PLAYING:
            # Map arrow keys or WASD to Pac-Man direction
            if pr.is_key_down(pr.KEY_UP) or pr.is_key_down(pr.KEY_W):
                self.model.set_player_input(Direction.UP)
            elif pr.is_key_down(pr.KEY_DOWN) or pr.is_key_down(pr.KEY_S):
                self.model.set_player_input(Direction.DOWN)
            elif pr.is_key_down(pr.KEY_LEFT) or pr.is_key_down(pr.KEY_A):
                self.model.set_player_input(Direction.LEFT)
            elif pr.is_key_down(pr.KEY_RIGHT) or pr.is_key_down(pr.KEY_D):
                self.model.set_player_input(Direction.RIGHT)

            # Cheat Toggles for Debugging
            if pr.is_key_pressed(pr.KEY_I):
                self.model.toggle_cheat(CheatType.INVINCIBILITY)
                print("Toggled: INVINCIBILITY")
            if pr.is_key_pressed(pr.KEY_F):
                self.model.toggle_cheat(CheatType.GHOST_FREEZE)
                print("Toggled: GHOST FREEZE")
            if pr.is_key_pressed(pr.KEY_N):
                self.model.toggle_cheat(CheatType.LEVEL_SKIP)
                print("Triggered: LEVEL SKIP")


if __name__ == "__main__":
    # 1. Load the configuration
    # (Ensure "config.json" exists in your working directory)
    try:
        config = load_config("config.json")
    except Exception as e:
        print(f"Failed to load config, ensure config.json exists. Error: {e}")
        exit(1)

    # 2. Instantiate Model, View, and Controller
    model = GameModel(config)
    view = DebugView()
    controller = DebugController(model, view)

    # 3. Start the test loop
    controller.run()
