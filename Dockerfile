FROM python:3.10.7-slim-bullseye


WORKDIR /app

# Have the newest PIP
RUN pip install --upgrade pip

# Install the requirements
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the source code
COPY app/ .

# Run the app
CMD ["python", "main.py"]
