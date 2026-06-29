# ==============================================================
#							PAC MAN
# ==============================================================

PYTHON = python3
UV = $(shell command -v uv 2> /dev/null || echo $(HOME)/.local/bin/uv)
UV_PROJECT_ENVIRONMENT = .venv

NAME = pac-man
EXEC_NAME = $(NAME).py
SRC_DIR = src
CONFIG_FILE = config.json
BUILD_DIR = ./build
DIST_DIR = ./dist

all: install

install:
	@if [ ! -e $(UV) ]; then \
		echo "installing uv..."; \
		curl -LsSf https://astral.sh/uv/install.sh | sh >/dev/null 2>&1; \
	fi
	@echo "Syncing dependencies..."
	@$(UV) sync

run:
	@$(UV) run python $(EXEC_NAME) $(CONFIG_FILE)

debug:
	@$(UV) run python -m pdb $(EXEC_NAME) $(CONFIG_FILE)

build: install
	@echo "Building package..."
	@$(UV) run pyinstaller \
		--log-level ERROR \
		--noconsole \
		--noconfirm \
		--specpath $(BUILD_DIR) \
		--workpath $(BUILD_DIR) \
		--distpath $(DIST_DIR) \
		--contents-directory . \
		--name=$(NAME) \
		--add-data "$(PWD)/assets:assets" \
		pac-man.py
	@echo "Copying required files..."
	@cp config.json dist/$(NAME)/config.json
	@cp USER_DOC.md dist/$(NAME)/USER_DOC.md
	@echo "Done! Package created at: $(DIST_DIR)/$(NAME)"

dist: build
	@echo "Zipping package files..."
	@cd $(DIST_DIR) && zip -r $(NAME).zip $(NAME) >/dev/null
	@echo "Done! Zipped file created at: $(DIST_DIR)/$(NAME)/$(NAME).zip"

lint:
	@echo "Running flake8..."
	@$(UV) run flake8 $(EXEC_NAME) $(SRC_DIR)
	@echo "Running mypy..."
	@$(UV) run mypy $(EXEC_NAME) $(SRC_DIR)

lint-strict:
	@echo "Running flake8..."
	@$(UV) run flake8 $(EXEC_NAME) $(SRC_DIR)
	@echo "Running mypy --strict..."
	@$(UV) run mypy $(EXEC_NAME) $(SRC_DIR) --strict

clean:
	@if [ -n "$$(find . -type d \( -name ".mypy_cache" -o -name "__pycache__" \
	-o -name ".uv_cache" -o -name ".pytest_cache" \) -print -quit)" ]; then \
		echo "Cleaning cache files..."; \
		find . -type d \( -name ".mypy_cache" -o -name "__pycache__" -o -name \
		".uv_cache" -o -name ".pytest_cache" \) -exec rm -rf {} +; \
	fi
	@echo "Removing build artifacts..."
	@$(RM) -r $(BUILD_DIR)

fclean: clean
	@echo "Removing virtual environment..."
	@$(RM) -r $(UV_PROJECT_ENVIRONMENT)
	@echo "Removing build directory..."
	@$(RM) -r $(DIST_DIR)

re: fclean all

.PHONY: all install run debug build dist lint lint-strict clean fclean re
.DEFAULT_GOAL = all
