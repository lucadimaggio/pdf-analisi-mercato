# Usa un'immagine Python 3.10 basata su Debian Bullseye
FROM python:3.10-slim-bullseye

# Imposta la directory di lavoro all'interno del container
WORKDIR /app

# Installa wkhtmltopdf e le sue dipendenze richieste dal repository Bullseye
RUN apt-get update && apt-get install -y \
    wkhtmltopdf \
    build-essential \
    libjpeg-dev \
    zlib1g-dev \
    libxrender1 \
    libfontconfig1 \
    xfonts-base \
    && rm -rf /var/lib/apt/lists/*

# Copia i file del progetto nella directory di lavoro
COPY . .

# Installa le dipendenze Python
RUN pip install --no-cache-dir -r requirements.txt

# Espone la porta su cui gira l'applicazione
EXPOSE 8080

# Comando per avviare l'applicazione con uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
