FROM python:3.10.6-slim-bullseye

# Fix for
#   ImportError: libGL.so.1: cannot open shared object file: No such file or directory
#   ImportError: libgthread-2.0.so.0: cannot open shared object file: No such file or directory
RUN apt-get update && apt-get install libgl1 libglib2.0-0 libsm6 libxrender1 libxext6 -y

# Set working directory
WORKDIR /app

# Have the newest PIP
RUN pip install --upgrade pip

# Install dependencies
COPY ./requirements.txt /app
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy the source code
COPY . /app

# Run the app
CMD ["python", "main.py"]
