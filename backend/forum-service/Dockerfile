# Use an official Python runtime as a base image
FROM python:3.9-slim-bookworm

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE=forum_service.settings

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project
COPY . /app/

# Create and set permissions for logs directory
RUN mkdir -p /app/logs && chmod 755 /app/logs

# Create a non-root user and switch to it
RUN adduser --disabled-password --gecos '' myuser
RUN chown -R myuser:myuser /app
USER myuser

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "forum_service.wsgi:application"]