FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    gettext \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

COPY . .

ENV PYTHONUNBUFFERED=1

RUN chmod +x ./start.sh

CMD ["./start.sh"]