.PHONY: deps

run-local:
	poetry run python src/ingest.py

deps:
	poetry export -f requirements.txt --output requirements.txt --without-hashes


build:
	docker build -t capstone .

run: build
	docker run capstone