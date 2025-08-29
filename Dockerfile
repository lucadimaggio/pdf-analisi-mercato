# Usa un'immagine Python 3.10 basata su Debian Bullseye
FROM python:3.10-slim-bullseye

# Imposta la directory di lavoro all'interno del container
WORKDIR /app

# Installa le dipendenze essenziali per wkhtmltopdf
RUN apt-get update && apt-get install -y \
    wget \
    build-essential \
    libxrender1 \
    libfontconfig1 \
    libjpeg-dev \
    xfonts-base \
    && rm -rf /var/lib/apt/lists/*

# Scarica e installa la versione statica e patchata di wkhtmltopdf
# che supporta l'esecuzione in ambienti headless e formati personalizzati
RUN wget https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.6/wkhtmltox_0.12.6-1.bullseye_amd64.deb -O /tmp/wkhtmltox.deb \
    && dpkg -i /tmp/wkhtmltox.deb \
    && rm /tmp/wkhtmltox.deb \
    && cp /usr/local/bin/wkhtmltopdf /usr/bin/wkhtmltopdf

# Copia i file del progetto nella directory di lavoro
COPY . .

# Installa le dipendenze Python
RUN pip install --no-cache-dir -r requirements.txt

# Espone la porta su cui gira l'applicazione
EXPOSE 8080

# Comando per avviare l'applicazione con uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
