#!/usr/bin/env bash

# Installiere Chromium und Chromedriver über pip
pip install chromedriver-autoinstaller
pip install pyppeteer

# Installiere Chromium über pyppeteer
python -m pyppeteer.install