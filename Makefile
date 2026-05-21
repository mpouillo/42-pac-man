# ==============================================================
#							PAC MAN
# ==============================================================

PYTHON = python3
UV = $(shell command -v uv 2> /dev/null || echo $(HOME)/.local/bin/uv)
UV_PROJECT_ENVIRONMENT = .venv

SRC_DIR = src
CONFIG_FILE

all: install

install:
	@if [ ! -e $(UV) ]; then \
		echo "installing uv..."; \
		curl -LsSf https://astral.sh/uv/install.sh | sh >/dev/null 2>&1; \
	fi
	@echo "Syncing dependencies..."
	@$(UV) sync

run:
	@$(UV) run python -m $(SRC_DIR) $(CONFIG_FILE)

debug:
	@$(UV) run python -m pdb -m $(SRC_DIR) $(CONFIG_FILE)

lint:
	@echo "Running flake8..."
	@$(UV) run flake8 $(SRC_DIR)
	@echo "Running mypy..."
	@$(UV) run mypy $(SRC_DIR)

lint-strict:
	@echo "Running flake8..."
	@$(UV) run flake8 $(SRC_DIR)
	@echo "Running mypy --strict..."
	@$(UV) run mypy $(SRC_DIR) --strict

clean:
	@if [ -n "$$(find . -type d \( -name ".mypy_cache" -o -name "__pycache__" \
	-o -name ".uv_cache" -o -name ".pytest_cache" \) -print -quit)" ]; then \
		echo "Cleaning cache files..."; \
		find . -type d \( -name ".mypy_cache" -o -name "__pycache__" -o -name \
		".uv_cache" -o -name ".pytest_cache" \) -exec rm -rf {} +; \
	fi

fclean: clean
	@echo "Removing virtual environment..."
	@$(RM) -r $(UV_PROJECT_ENVIRONMENT)

re: fclean all

.PHONY: all install run debug lint lint-strict clean fclean re
.DEFAULT_GOAL = all
