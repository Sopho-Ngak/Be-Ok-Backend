# Use the official Python image as the base image
FROM python:3.10-slim

# Update the package list and install the required packages
RUN apt-get update &&\
    apt-get install build-essential python3-dev libpq-dev -y &&\
    apt-get install gcc -y &&\
    apt-get install python3-pip -y

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy the Django project code
COPY . .

# Collect the static files
RUN python manage.py collectstatic --no-input

# Expose the port the app runs on
EXPOSE 8000

# Start the Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]