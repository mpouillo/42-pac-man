*This project has been created as part of the 42 curriculum by mpouillo, zqian.*

# USER GUIDE

## How to Run

1. **Extract** the entire `.zip` archive into a folder.
2. Open the folder and double-click **`pacman`** or run **`./pacman`** to launch the game.

*Note: Do not move the executable file out of this folder, or it will lose track of its assets and configuration files.*

---

## Controls

| Action | Key / Input |
| :--- | :--- |
| **Move Pac-Man** | `W` `A` `S` `D` / Arrow Keys |
| **Pause Game** | `Escape` |
| **Navigate Menus**| Arrow Keys + `Enter` |

> [!TIP]
> You can also use the mouse to click on buttons!

---

## Game Customization (Options & Configuration)

You can customize the gameplay parameters by editing the **`config.json`** file located right next to the game executable using any text editor (like Notepad or VS Code).

### Available Options:

* **`highscores`** *(String)*: The path to the file where highscores are saved.
* **`levels`** *(List of Strings)*: The order and files used for level progression.
* **`lives`** *(Integer)*: The number of lives Pac-Man starts with. (Default: `3`)
* **`points_per_pacgums`** *(Integer)*: Points awarded for regular pellets.
* **`points_per_super_pacgum`** *(Integer)*: Points awarded for energizers.
* **`points_per_ghost`** *(Integer)*: Points awarded for eating a frightened ghost.
* **`points_per_second_left`** *(Integer)*: Points earned at level clear for every second left on the timer.

If your settings ever break the game, you can restore it by copying the following defaults:

<details>
<summary>Default config.json values</summary>
<pre>
# config.json
{
    "highscores": "highscores.json",
    "levels": [
        "assets/levels/level_1.json",
        "assets/levels/level_2.json",
        "assets/levels/level_3.json",
        "assets/levels/level_4.json",
        "assets/levels/level_5.json",
        "assets/levels/level_6.json",
        "assets/levels/level_7.json",
        "assets/levels/level_8.json",
        "assets/levels/level_9.json",
        "assets/levels/level_10.json"
    ],
    "lives": 3,
    "points_per_pacgum": 10,
    "points_per_super_pacgum": 50,
    "points_per_ghost": 200,
    "points_per_second_left": 100
}
</pre>
</details>

---

## Dev / Evaluation Cheat Mode

For testing and evaluation purposes, a built-in cheat system is available when the game is paused:

* Open the **Pause Menu** to toggle features like:
    * Invincibility Mode
    * Speed Boost
    * Freeze Ghosts
    * Skip Level
