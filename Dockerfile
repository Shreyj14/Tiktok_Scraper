# Use an official Python runtime as the parent image
FROM python:3.8-slim

# Set environment varibles
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install Chrome and chromedriver for Selenium
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the current directory contents into the container at /usr/src/app
COPY . /usr/src/app/

# Set work directory
WORKDIR /usr/src/app

# Run the script
CMD ['ls']
CMD ["python", "./tiktok_scrapper.py"]  
