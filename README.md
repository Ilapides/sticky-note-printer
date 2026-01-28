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
```

### 2. Configure Environment

Copy `.env.example` to `.env` and set `PRINTER_IP`, `PRINTER_PORT`, and `TEMP_IMAGE_DIR`.

### 3. Run with Docker

```bash
docker-compose up --build
```

---

## API Endpoints

### POST /print/tasks (legacy)

Send a simple task list:

```bash
curl -X POST http://localhost:5000/print/tasks \
  -H "Content-Type: application/json" \
  -d '{"tasks": ["Buy milk", "Take out trash"]}'
```

### POST /print/grocery

Send a structured grocery list with pixel-accurate layout:

```bash
curl -X POST http://localhost:5000/print/grocery \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Weekly Groceries",
    "areas": [
      {
        "name": "Produce",
        "items": [
          {"qty": "2", "unit": "lb", "name": "onions", "note": "yellow", "checked": false},
          {"qty": "1", "unit": "bunch", "name": "cilantro", "checked": false}
        ]
      },
      {
        "name": "Dairy",
        "items": [
          {"qty": "1", "unit": "gal", "name": "milk", "note": "whole", "checked": false}
        ]
      }
    ],
    "options": {
      "width_px": 576,
      "margin_px": 16,
      "line_gap_px": 6,
      "include_checked": false
    }
  }'
```

Response:

```json
{
  "preview_png_base64": "...",
  "sent_to_printer": true,
  "saved_paths": {"png": "...", "bmp": "..."}
}
```

---

## Running Tests

```bash
pip install -r requirements.txt
pytest tests/
