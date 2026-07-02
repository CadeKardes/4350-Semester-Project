FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# /data is where the SQLite database lives - mount a volume here for persistence
VOLUME ["/data"]

EXPOSE 5000

CMD ["python", "server.py"]
