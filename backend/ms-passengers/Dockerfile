# TODO: Completar según stack elegido
# Este Dockerfile será completado cuando el equipo elija el lenguaje y framework

# Ejemplo para Node.js:
# FROM node:18-alpine
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

ENV PYTHONPATH=/app/src

EXPOSE 8001

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
