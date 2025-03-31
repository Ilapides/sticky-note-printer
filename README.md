# 🖨️ Sticky Note Printer Web App

A simple Flask-based web application that turns your task list into a printable sticky note using the Amazon Smart Sticky Note Printer.

This project:
- Accepts a list of tasks via a REST API
- Renders them into an image
- Converts the image to a printable BMP format compatible with the printer
- Sends the print job over IPP

---

## 🚀 Features

- 📋 REST API to submit tasks
- 🖼 Converts tasks to styled images
- 🧾 BMP3-compatible print rendering
- 🐳 Docker support for easy deployment
- ✅ Tested with the Amazon Smart Sticky Note Printer (Knectek Labs)

---

## 🧰 Tech Stack

- Python 3.11
- Flask
- Pillow
- ImageMagick (via `convert`)
- ipptool (from `cups-ipp-utils`)
- Docker & Docker Compose

---

## 📦 Setup

### 1. Clone the Repo

```bash
git clone https://github.com/yourusername/sticky-note-printer.git
cd sticky-note-printer
