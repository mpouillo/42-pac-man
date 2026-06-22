*This project has been created as part of the 42 curriculum by mpouillo, zqian.*

# Pac Man

- [Description](#description)
    - [Overview](#overview)
    - [Configuration](#configuration)
    - [Highscore](#highscore)
    - [Maze Generation](#maze-generation)
    - [Implementation](#implementation)
    - [General Software Architecture](#general-software-architecture)
    - [Project Management](#project-management)
- [Instructions](#instructions)
- [Resources](#resources)

## Description

## Overview

The goal of the Pac Man project is simple: recreate the classic 1980 arcade game, in Python 3.10+.

The game must support:
- Robust error handling.
- A JSON configuration file to set game parameters.
- Level generation based on an external `A-Maze-ing` package.
- Highscores stored in a local JSON file.
- A graphical UI with main menu, game view, and game over handling.
- A "cheat" mode for evaluation purposes.
- Deployment to a public gaming platform (e.g., Steam or itch.io).

## Configuration

The configuration file must be formatted asa valid JSON object and contain the following values:

| KEY                           | TYPE          | DESCRIPTION                                                       | EXAMPLE                       |
| ----------------------------- | ------------- | ----------------------------------------------------------------- | ----------------------------- |
| `highscores`                  | `str`         | File to save highscores                                           | `"filename.json"`             |
| `levels`                      | `[str, ...]`  | List of level files to play (in order)                            | `["file1", "file2", "file3"]` |
| `lives`                       | `int`         | Starting value for Pacman's lives                                 | `3`                           |
| `points_per_pacgums`          | `int`         | Points earned for every Pac-gum consumed                          | `10`                          |
| `points_per_super_pacgum`     | `int`         | Points earned for every Super Pac-gum consumed                    | `50`                          |
| `points_per_ghost`            | `int`         | Points earned for every Ghost consumed                            | `200`                         |
| `points_per_second_left`      | `int`         | Points earned at level clear for every second left on the timer   | `100`                         |

## Highscore

Score is calculated based on how many Pac-gums, Super Pac-Gums and Ghosts Pac-Man consumes during the game. They each give a set amount of points depending on the value specified in the configuration file (see [Configuration](#configuration)).

On top of that, whenever a level is cleared, bonus scored is given depending on the time left on the level timer. This value also depends on the configuration file.

## Maze Generation

The assigned A-Maze-ing package contains a `MazeGenerator` class that can be used to generate a maze. It takes the following arguments:
- size: width and height of the maze
- perfect: whether the maze is perfect (single path between entry and exit) or not
- entry_cell: coordinates of the entry point
- exit_cell: coordinates of the exit point
- seed: value for maze reproducibility

For this project, only the size and seed values are important. They both depend on the values parsed in the `<level>.json` file.

The maze is then converted to a list of Enum values (`CellState`) so that both walls and corridors are the same size and can be processed easier.

## Implementation

- This project is written in Python 3.13, using Raylib/Pyray.
- It follows a Model–View–Controller architecture.
- The controller manages inputs, menus, game states, and the main loop.
- The model contains the gameplay rules, score, lives, timer, and progression.
- The view renders the maze, entities, menus, HUD, and end screens.
- Mazes are generated using the external mazegenerator package.
- Pac-Man moves continuously while remaining aligned with the maze grid.
- Buffered inputs allow smooth turns at intersections.
- Four ghosts reproduce distinct behaviors inspired by the original game.
- Ghosts alternate between chase, scatter, frightened, and eaten states.
- Pacgums, super-pacgums, collisions, respawning, and scoring are implemented.
- The game includes multiple levels with configurable difficulty and time limits.
- A JSON configuration validated with Pydantic defines the game settings.
- Highscores are persisted in a JSON file and displayed through the interface.
- The pause menu provides cheats for invincibility, speed, ghost freezing, and level skipping.
- 3D assets are used for walls and characters, with Raylib primitives as fallbacks.
- The project can be installed, linted, debugged, and launched through its Makefile.

## General Software Architecture

This project is based on the **Model-View-Controller (MVC)** structure.

```text
Makefile / python -m src
          |
          v
      __main__.py
          |
          v
   GameController ------> InputState
      |       |
      |       +----------> GameView ----> Raylib + assets 3D
      v
   GameModel
      +-- Level ---------> MazeGenerator
      +-- Pacman
      +-- Ghost x4
      +-- HighscoreManager
```

## Project Management

We began the project by working out a general outline of the project structure and an exhaustive list of protocols, dataclasses and enums. Thanks to this, everything went smoothly and we could split our work cleanly from the very beginning.

Contributions:

[<img src="https://contrib.rocks/image?repo=mpouillo/42-pac-man">](https://github.com/mpouillo/42-pac-man/graphs/contributors)

- **mpouillo**:
    - Model (`game_model.py`, `ghost.py`, `level.py`, `pacman.py`)
    - Config (`config.json`, `config.py`)
    - Highscores (`highscore.py`)
- **zqian**:
    - View (`menus.py`, `pages.py`, `scene_3d.py`, `entities_3d.py`, `fov.py`, `ui.py`, `wall_shapes.py`)
    - Controller (`game_controller.py`, `input.py`)

[More details here](/management/timeline.md)

## Instructions

Configure the `config.json` file following the [Configuration](#configuration) section.

You can manage the project using the provided Makefile:

| Rules         | Action                                                |
| ------------- | ----------------------------------------------------- |
| all           | `install`                                             |
| install       | Install project dependencies                          |
| run           | Run the program using `config.json`                   |
| lint          | Check code for stylistic errors                       |
| lint-strict   | Check code for stylistic errors (strict)              |
| clean         | Remove temporary files                                |
| fclean        | `clean` + Remove virtual environment                  |
| re            | `fclean` + `all`                                      |

## Resources

- [A* Search: A Comprehensive Guide (Medium)](https://medium.com/@tahsinsoyakk/a-search-a-comprehensive-guide-8275ebdf8fae)
- [TAC380 - Lab 5: Pac-Man](https://itp380.org/Lab05.html)
- [Toupty - Pac-Man](https://www.toupty.com/jeupacman.html#gsc.tab=0)
- [raylib](https://www.raylib.com/)
- [raylib GitHub repository](https://github.com/raysan5/raylib)
- [raylib subreddit](https://www.reddit.com/r/raylib/new/)
- [Figma](https://www.figma.com/fr-fr/)
- [YouTube playlist](https://www.youtube.com/watch?v=RGzj-PF7D74&list=PLwR6ZGPvjVOTIMqUXnqyWaIfQg0xdHNZn)
- [YouTube video](https://www.youtube.com/watch?v=MgI4Y9Z6LjA)
