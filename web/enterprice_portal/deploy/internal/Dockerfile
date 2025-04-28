FROM python:3.9-slim

WORKDIR /app

COPY internal_app.py .

RUN pip install flask

CMD ["python", "internal_app.py"]