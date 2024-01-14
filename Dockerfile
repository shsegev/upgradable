# Use Alpine Linux as the base image
FROM python:3.9-alpine

# Set the working directory in the container
WORKDIR /app
COPY ./requirements.txt /app/requirements.txt
# Install dependencies
RUN pip install -r requirements.txt

# Copy the local code to the container
COPY ./upservice /app

# Expose the port on which the application will run
EXPOSE 8000

# Command to run the application
CMD ["python", "main.py"]
