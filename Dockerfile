FROM python:3.9

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application files
COPY . .

# Ensure the .env file is copied
COPY .env .env

# Expose port 5000
EXPOSE 5000

# Run the application
CMD ["python", "jupyter.py"]