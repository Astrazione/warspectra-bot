# COPY app .
# COPY requirements.txt .

# RUN pip install -U -r requirements.txt

# ENV TZ="Europe/Moscow"

# COPY . .

# CMD ["python3.13", "app/main.py"]

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN mkdir -p /app/logs

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

ENV TZ="Europe/Moscow"

CMD ["python", "app/main.py"]

# FROM python:3.11-slim

# ENV PYTHONDONTWRITEBYTECODE=1
# ENV PYTHONUNBUFFERED=1

# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# COPY app .

# ENV TZ="Europe/Moscow"

# CMD ["python", "app/main.py"]