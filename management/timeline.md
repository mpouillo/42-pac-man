2026-05-21
	: Started project
	: Defined project structure: created basic files and decided on protocols

2026-05-30
	: Started working on the GameModel:
		- Created Level class, with parsing of the grid returned by MazeGenerator
		- Created Ghost, Pacman and GameModel class (incomplete)
		- Created constants.py file
		- Created level_{id}.json assets

2026-05-31
	: Updates to levels:
		- Fixes and improvements to Level class
		- Updates to level_{id}.json file structure and values
	: Completed Ghost logic (pathfinding)
	: Created HighscoreManager class
	: Updated GameModel, protocols.py

2026-06-01
	: Various additions to Model classes
		- Completed Pacman logic
		- Improvements and fixes to Ghost logic
		- Improvement to Level data management
	: Updates to protocols.py
	: Created config.py and config.json
	: Created stubs for GameController and __main__

2026-06-03
	: Improvements to ghost AI
	: Improvements to code structure

2026-06-11
	: Initial project setup:
		- First controller and UI implementation
		- Fixed GhostState and GhostType
		- Added 3D-related files and the first version of the 3D map
		- Started preparing the 3D walls

2026-06-12
	: Fixed reset, restart, and highscore history
	: Added the pseudo/player dialog and updated the pseudo popup
	: Continued preparing and fixing the wall design

2026-06-13
	: Fixed username-related logic

2026-06-16
	: Adjusted the position of the username window shown at game over
	: This commit was local-only and was not visible in the remote repository

2026-06-17
	: Added the wall type system:
		- Created wall_shapes.py
		- Added wall types
		- Added shadow effects

2026-06-19
	: Focused on the game view and UI:
		- Added the game-over page, maze image, ghost animations, and mouse menu controls
		- Added cheat mode
		- Adjusted the field of view and wall direction
		- Refined mouse and keyboard control priorities
		- Updated the highscore and username pages
		- Stopped ghost state printing after game over or victory
		- Standardized title and content sizing
		- Updated constants and split UI code into separate files

2026-06-20
	: Continued work on the game-view branch:
		- Preserved wall styles and tested 3D models
		- Replayed and migrated wall, shadow, game-over, cheat-mode, and UI-splitting work from June 17 to June 19
		- Updated the 3D ghost and Pac-Man movement frames

2026-06-21
	: Integration, fixes, and final cleanup:
		- Fixed 3D assets, merge conflicts, mypy issues, and wall sizing
		- Updated the README and levels
		- Removed unused variables
		- Added remaining-time scoring for level completion
		- Added try/except handling to main
		- Fixed highscore JSON handling and ghost snapping
		- Merged develop and game-view hotfixes
		- Adjusted the lives/time HUD and highscore username flashing
		- Updated the mouse interaction area and cursor console behavior
		- Improved the main menu's 3D effects and background image
		- Added a Pac-Man death shake effect and fixed overlapping ghosts
		- Reorganized the view layer
