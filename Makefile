.PHONY: deps

ECR = 338791806049.dkr.ecr.eu-west-1.amazonaws.com/jan-summer-school-2023
DAGS = s3://dataminded-academy-capstone-resources/dags
IMAGE = capstone

run-local:
	poetry run python src/ingest.py

deps:
	poetry export -f requirements.txt --output requirements.txt --without-hashes


build:
	docker build --platform linux/amd64 -t $(IMAGE) .

run: build
	. .aws.env; docker run -e AWS_REGION=$$AWS_REGION -e AWS_ACCESS_KEY_ID=$$AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY=$$AWS_SECRET_ACCESS_KEY $(IMAGE)

infra:
	pushd infrastructure && terraform init && terraform apply -auto-approve

ecr-login:
	aws ecr get-login-password --region eu-west-1 | docker login --username AWS --password-stdin $(ECR)

push: build ecr-login 
	docker tag $(IMAGE) $(ECR):latest
	docker push $(ECR):latest

dag:
	aws s3 cp dags/ingest.py $(DAGS)/ingest.py

deploy: push dag