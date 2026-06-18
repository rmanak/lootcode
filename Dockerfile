# Runs the lootcode web app (uses the in-process `subprocess` executor).
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV HOST=0.0.0.0 PORT=8000 LOOTCODE_DB=/app/data/lootcode.db
RUN mkdir -p /app/data
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
