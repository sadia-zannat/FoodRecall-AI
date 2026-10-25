FROM python:3.12-slim
WORKDIR /app
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt
COPY backend ./backend
COPY frontend ./frontend
COPY data ./data
ENV PYTHONUNBUFFERED=1
EXPOSE 8000
CMD ["sh","-c","exec python -m uvicorn backend.app:app --host 0.0.0.0 --port ${PORT:-8000}"]
