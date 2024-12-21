# Use a base image with Python 3.9
FROM python:3.9

# Set the working directory inside the container
WORKDIR /app

# Copy the cloud server's socket into the container
COPY cloud_server.py .

# Install the required dependencies
RUN pip install jsonpickle
RUN pip install numpy
RUN pip install sage

# Set the command to run the data owner
CMD ["python", "cloud_server.py"]