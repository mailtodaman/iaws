# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies
# This is a more efficient way of installing packages, which also cleans up the apt cache to reduce image size.
RUN apt-get update && apt-get install -y --no-install-recommends \
    unzip \
    wget \
    vim \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# You can remove the commented out `pip install` commands if they are included in your requirements.txt

# Copy the current directory contents into the container at the work directory
# Assuming that the Docker build context is set to the project root directory (where manage.py is located)
COPY awssheet/ .

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Collect static files
# Uncomment this if you are collecting static files in your Django project
# RUN python3 manage.py collectstatic --noinput

# Start your Django application
# There can only be one CMD instruction in a Dockerfile. If you list more than one, only the last CMD will take effect.
CMD python3 manage.py migrate sessions && python3 manage.py runserver 0.0.0.0:8000
