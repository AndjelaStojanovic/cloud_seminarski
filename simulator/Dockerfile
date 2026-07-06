FROM python:3.11-slim
WORKDIR /app
COPY requirements-simulator.txt .
RUN pip install --no-cache-dir -r requirements-simulator.txt
COPY simulator.py .
CMD ["python", "simulator.py"]
