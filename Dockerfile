FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
CMD ["gunicorn","-k","gevent","-b","0.0.0.0:8000","backend.app:create_app()","--reload"]
