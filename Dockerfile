FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
COPY tests ./tests
EXPOSE 8080
# Scenario switch: change this to true, commit and push to simulate a bad release
ENV SIMULATE_ANOMALY=false
CMD ["python", "app.py"]
