# Start von einem Basis-Image
FROM python:3.11-slim

# Arbeitsverzeichnis setzen
WORKDIR /app

# System-Pakete installieren
RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    chromium-driver \
    wget \
    gnupg \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Google Chrome installieren
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && apt-get install -y google-chrome-stable

# Sicherstellen, dass pip installiert ist
RUN apt-get update && apt-get install -y python3-pip

# Anforderungen installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Anwendungscode in den Container kopieren
COPY . .

# Port freigeben und Startbefehl definieren
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]


# container mit volume starten: "docker run -v C:\Users\Paddy\Documents\Coding\spielviel-api:/app -p 8000:8000 spielviel-api"