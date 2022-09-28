FROM python:3.10.6-slim-bullseye

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
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8989"]
CMD ["python", "main.py"]
