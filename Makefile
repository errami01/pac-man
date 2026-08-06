# Project Variables
PYTHON       = python3
PIP          = pip3
MAIN         = pac-man.py
CONFIG       = config.json
PACKAGE_NAME = pac-man

# Colors for terminal output
BLUE         = \033[0;34m
NC           = \033[0m # No Color

.PHONY: all install run debug clean lint lint-strict package

all: install lint run

# III.2: Install project dependencies
install:
	@echo "$(BLUE)Installing dependencies...$(NC)"
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	$(PIP) install mazegenerator-2.1.0-py3-none-any.whl
	#$(PIP) install pyray pyinstaller flake8 mypy

# III.2: Execute the main script
# Program must take exactly one argument (config file)
run:
	@echo "$(BLUE)Running Pac-Man...$(NC)"
	$(PYTHON) $(MAIN) $(CONFIG)

# III.2: Run in debug mode using pdb
debug:
	@echo "$(BLUE)Running in debug mode (pdb)...$(NC)"
	$(PYTHON) -m pdb $(MAIN) $(CONFIG)

# III.2: Remove temporary files and caches
clean:
	@echo "$(BLUE)Cleaning up...$(NC)"
	rm -rf __pycache__
	rm -rf .mypy_cache
	rm -rf .pytest_cache
	rm -rf build/
	rm -rf dist/
	rm -f *.spec
	find . -type d -name "__pycache__" -exec rm -rf {} +

# III.2: Execute mandatory linting commands 
lint:
	@echo "$(BLUE)Running linter (flake8 & mypy)...$(NC)"
	flake8 . --exclude=.venv,__pycache__,.mypy_cache
	mypy . --warn-return-any \
		   --warn-unused-ignores \
		   --ignore-missing-imports \
		   --disallow-untyped-defs \
		   --check-untyped-defs

# III.2: Optional strict linting
lint-strict:
	@echo "$(BLUE)Running strict linter...$(NC)"
	flake8 .
	mypy . --strict

# Packaging for distribution (Itch.io)
package: clean
	@echo "$(BLUE)Packaging for distribution...$(NC)"
	pyinstaller --noconfirm --onefile --windowed \
		--add-data "config.json:." \
		--add-data "res:res" \
		$(MAIN)
	@echo "$(BLUE)Package created in dist/ folder.$(NC)"

# Helper to show usage
help:
	@echo "Usage:"
	@echo "  make install      - Install dependencies"
	@echo "  make run          - Run the game"
	@echo "  make lint         - Run mandatory flake8 and mypy checks"
	@echo "  make package      - Create standalone executable"
	@echo "  make clean        - Remove caches and build files"