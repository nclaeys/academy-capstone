.PHONY: deps

ECR = 338791806049.dkr.ecr.eu-west-1.amazonaws.com/jan-summer-school-2023
DAGS = s3://dataminded-academy-capstone-resources/dags

run-local:
	poetry run python src/ingest.py

deps:
	poetry export -f requirements.txt --output requirements.txt --without-hashes


build:
	docker build --platform linux/amd64 -t capstone .

run: build
	docker run capstone

infra:
	pushd infrastructure && terraform init && terraform apply -auto-approve

ecr-login:
	aws ecr get-login-password --region eu-west-1 | docker login --username AWS --password-stdin $(ECR)

push: build ecr-login 
	docker tag capstone $(ECR):latest
	docker push $(ECR):latest

dag:
	aws s3 cp dags/ingest.py $(DAGS)/ingest.py

deploy: push dag