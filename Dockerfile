FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY matrix_spiral/ ./matrix_spiral/
COPY tests/ ./tests/
COPY example.py .
CMD ["pytest", "tests/"]