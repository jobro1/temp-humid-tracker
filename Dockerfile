FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY all_graphs.py mqtt_to_kafka.py ./

EXPOSE 8050

CMD ["python", "all_graphs.py"]
