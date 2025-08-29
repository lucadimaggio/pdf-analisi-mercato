import os
import pdfkit
import io
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from jinja2 import Environment, FileSystemLoader
from pydantic import BaseModel
import logging

# Imposta il logger per debug
logger = logging.getLogger(__name__)

app = FastAPI()

# Configurazione Jinja2
env = Environment(loader=FileSystemLoader("templates"))

# Definiamo il modello di input
class PdfRequest(BaseModel):
    # Il messaggio è ora opzionale
    message: str | None = None
    # Aggiungiamo i parametri per la larghezza e l'altezza
    width: str | None = None
    height: str | None = None

@app.get("/")
def home():
    return {"message": "PDF Service is running 🚀"}

@app.post("/generate-pdf")
async def generate_pdf(body: PdfRequest):
    html_message = body.message or "Analisi di mercato generata con successo (via pdfkit)"

    template = env.get_template("report.html")
    html_content = template.render(message=html_message)

    # Creiamo un dizionario di opzioni per wkhtmltopdf
    options = {
        'enable-local-file-access': True,
        'encoding': 'UTF-8'
    }

    # Aggiungiamo larghezza e altezza solo se sono presenti nella richiesta
    if body.width:
        options['page-width'] = body.width
    if body.height:
        options['page-height'] = body.height

    # Logga le opzioni per il debug
    logger.info(f"Opzioni wkhtmltopdf: {options}")
    
    # Converte HTML in PDF con le opzioni corrette
    # Nota: la versione di wkhtmltopdf che stiamo usando nel container
    # non supporta l'opzione --page-size con valori personalizzati.
    # Usiamo --page-width e --page-height.
    # Se width e height non sono specificati, si userà la dimensione A4 di default.
    try:
        pdf_bytes = pdfkit.from_string(html_content, False, options=options)
    except Exception as e:
        logger.error(f"Errore durante la generazione del PDF: {e}")
        return {"error": f"Errore durante la generazione del PDF: {e}"}

    # Restituisce il PDF come file
    return StreamingResponse(io.BytesIO(pdf_bytes), media_type="application/pdf", headers={
        "Content-Disposition": "inline; filename=analisi.pdf"
    })
