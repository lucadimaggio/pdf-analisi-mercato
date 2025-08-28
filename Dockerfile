# Use a slim Python 3.10 image as the base
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Install wkhtmltopdf and other system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    build-essential \
    libxrender1 \
    libxext6 \
    libjpeg-dev \
    zlib1g-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/* \
    && wget https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-2/wkhtmltopdf_0.12.6.1-2.bullseye_amd64.deb \
    && dpkg -i wkhtmltopdf_0.12.6.1-2.bullseye_amd64.deb \
    && rm wkhtmltopdf_0.12.6.1-2.bullseye_amd64.deb

# Copy the project files into the working directory
COPY . .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port on which the application runs
EXPOSE 8000

# Command to start the application with uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]