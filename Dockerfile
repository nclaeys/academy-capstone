FROM --platform=linux/amd64 capstone-image:latest

USER 0
COPY requirements.txt requirements.txt

ENV PIP_NO_CACHE_DIR=1
RUN pip install -r requirements.txt

COPY . .

RUN pip install .

CMD ["python3", "src/capstone/ingest.py"]
