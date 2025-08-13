# Use Python 3.13 slim image
FROM python:3.13-slim-bookworm

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application
COPY . .

# Ensure .env variables are loaded (if you have a .env file)
# Using python-dotenv is recommended in your app
# ENV variables can also be passed at runtime with -e
# Example: docker run -e OPENAI_API_KEY=xxxx ...
ENV PYTHONUNBUFFERED=1

# Expose port 8080 for FastAPI
EXPOSE 8080

# Command to run the app (adjust main:app if different)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
