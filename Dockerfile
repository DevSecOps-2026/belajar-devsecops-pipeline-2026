FROM python:3.10-slim
WORKDIR /app

# 1. Update OS Debian untuk menambal celah keamanan sistem (CVE)
RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*

RUN useradd -m appuser
COPY requirements.txt .

# 2. Upgrade pip dan library dasar Python yang terdeteksi rentan oleh Trivy
RUN pip install --no-cache-dir --upgrade pip wheel setuptools jaraco.context

RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN chown -R appuser:appuser /app
USER appuser
EXPOSE 5000
CMD ["python", "app.py"]
