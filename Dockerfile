# Runs the lootcode web app (uses the in-process `subprocess` executor).
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt constraints.txt ./
RUN pip install --no-cache-dir -r requirements.txt -c constraints.txt

COPY . .

# A container binds 0.0.0.0 by definition — the real exposure decision is which
# port the operator publishes, and `docker run -p` / compose is where they make
# it. So the LAN opt-in is set here; the guard still fires for anyone running
# uvicorn directly. Read docs/security.md before publishing this port: there is
# no authentication, and /admin can rewrite the bank and run arbitrary Python.
ENV HOST=0.0.0.0 PORT=8000 LOOTCODE_DB=/app/data/lootcode.db LOOTCODE_TRUST_LAN=1
RUN mkdir -p /app/data
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
