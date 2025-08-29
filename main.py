import os
import pdfkit
import io
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from jinja2 import Environment, FileSystemLoader
from pydantic import BaseModel
import logging

# Imposta il logger per debug
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Configurazione Jinja2
env = Environment(loader=FileSystemLoader("templates"))

# Definiamo il modello di input che ora accetta i dati del report e l'orientamento
class PdfRequest(BaseModel):
    data: dict | None = None
    width: str | None = None
    height: str | None = None
    orientation: str | None = None # Aggiungiamo il parametro di orientamento

@app.get("/")
def home():
    return {"message": "PDF Service is running 🚀"}

@app.post("/generate-pdf")
async def generate_pdf(body: PdfRequest):
    # Logga i dati ricevuti per il debug
    logger.info(f"Dati ricevuti per la generazione del PDF: {body.data}")

    template = env.get_template("report.html")
    
    # Passa l'intero dizionario 'data' al template
    html_content = template.render(data=body.data)

    options = {
        'enable-local-file-access': True,
        'encoding': 'UTF-8'
    }

    # Aggiungi l'orientamento, se specificato
    if body.orientation:
        options['orientation'] = body.orientation
    # Se width e height sono specificati, li aggiungi alle opzioni
    if body.width:
        options['page-width'] = body.width
    if body.height:
        options['page-height'] = body.height

    logger.info(f"Opzioni wkhtmltopdf: {options}")
    
    try:
        # Converte HTML in PDF con le opzioni corrette.
        pdf_bytes = pdfkit.from_string(html_content, False, options=options)
        
        return StreamingResponse(io.BytesIO(pdf_bytes), media_type="application/pdf", headers={
            "Content-Disposition": "inline; filename=analisi.pdf"
        })

    except Exception as e:
        logger.error(f"Errore durante la generazione del PDF: {e}")
        return {"error": f"Errore durante la generazione del PDF: {e}"}
