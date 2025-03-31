FROM python:3.11-slim

# Install ImageMagick and ipptool (from cups)
RUN apt-get update && apt-get install -y \
    imagemagick \
    cups-ipp-utils \
    && rm -rf /var/lib/apt/lists/*

# Set up app
WORKDIR /app
COPY . /app

# Install dependencies
RUN pip install -r requirements.txt

CMD ["python", "run.py"]