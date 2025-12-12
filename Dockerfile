FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# system deps
RUN apt-get update && apt-get install -y build-essential git curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 8000
CMD ["uvicorn", "app_v2:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
