FROM --platform=linux/amd64 public.ecr.aws/o5k8q4t0/capstone:v3.4.1-hadoop-3.3.6-v1

USER 0
COPY requirements.txt requirements.txt

ENV PIP_NO_CACHE_DIR=1
RUN pip install -r requirements.txt

COPY . .

RUN pip install .

CMD ["python3", "src/capstone/ingest.py"]
