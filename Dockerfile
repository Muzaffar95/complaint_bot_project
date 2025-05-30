FROM python:3.11-slim

WORKDIR /app

COPY . .

# Добавляем PYTHONPATH
ENV PYTHONPATH=/app

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --upgrade pip

CMD ["python", "bot/main.py"]
