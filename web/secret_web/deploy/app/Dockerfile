FROM python:3.12
LABEL authors="maxtheyoung"

WORKDIR /app

RUN useradd -u 1337 -c 'aHR0cHM6Ly95b3V0dS5iZS9kUXc0dzlXZ1hjUQ==' -s '/bin/nologin' -d '/app' lamer
RUN apt update
RUN apt install nmap net-tools -y


COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . .

USER lamer

CMD ["bash", "-c", "while !</dev/tcp/db/5432; do sleep 1; done; uvicorn main:app --host 0.0.0.0 --port 8000"]
