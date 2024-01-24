# Use the official Python image as the base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Copy the Flask app code into the container
COPY . .

# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt

# Set the environment variable for the Flask app port
ENV PORT 8080

# # Expose the port on which the Flask app will run
# EXPOSE $PORT

# Set the entry point for the container
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app