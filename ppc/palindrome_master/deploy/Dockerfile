FROM python:3.9-slim

WORKDIR /app

COPY words .
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN apt update && apt install -y socat

COPY server.py .

EXPOSE 5000

CMD ["socat", "TCP-LISTEN:5000,reuseaddr,fork", "EXEC:'python3 server.py'"]
