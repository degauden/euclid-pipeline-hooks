# list the commands
default:
	just --list
# pre-commit autoupdate
autoupdate:
	pre-commit autoupdate
# pre-commit install
install:
	pre-commit install
# pre-commit run --all-files
runall:
	pre-commit run --all-files
