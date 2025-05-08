FROM python:3.9-slim

# Installieren von Chromium und ChromeDriver
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Arbeitsverzeichnis im Container
WORKDIR /app

# Kopieren der Anwendungsdateien
COPY . /app/

# Installieren der Python-Abhängigkeiten
RUN pip install --no-cache-dir -r requirements.txt

# Port freigeben
EXPOSE 5000

# Anwendung starten
CMD ["python", "app.py"]
