FROM public.ecr.aws/dataminded/spark-k8s-glue:v3.2.4-hadoop-3.3.5-v1

USER 0
COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .

RUN pip install .

CMD ["python3", "src/capstone/ingest.py"]
