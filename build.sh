#!/usr/bin/env bash
# Sicherstellen, dass die Pakete aktuell sind
apt-get update 

# Chromium-Browser und Chromedriver installieren
apt-get install -y chromium-browser chromium-chromedriver

# Optional: Bereinigen, um Speicherplatz zu sparen
apt-get clean
