# Start von einem Basis-Image
FROM python:3.11-slim

# Arbeitsverzeichnis setzen
WORKDIR /app

# System-Pakete installieren
RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    wget \
    chromium-driver \
    gnupg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Google Chrome installieren (ohne apt-key)
RUN apt-get update && apt-get install -y curl gnupg wget unzip && \
    curl -fsSL https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-linux-signing-key.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-linux-signing-key.gpg] http://dl.google.com/linux/chrome/deb/ stable main" \
        > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && apt-get install -y google-chrome-stable && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Sicherstellen, dass pip installiert ist
RUN apt-get update && apt-get install -y python3-pip

# Anforderungen installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Anwendungscode in den Container kopieren
COPY . .

# Port freigeben und Startbefehl definieren
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--proxy-headers", "--forwarded-allow-ips", "*"]
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]


