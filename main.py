import os
import pdfkit
import io
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from jinja2 import Environment, FileSystemLoader
from pydantic import BaseModel

# Inizializza l'applicazione FastAPI
app = FastAPI()

# Configurazione Jinja2 per i template HTML
env = Environment(loader=FileSystemLoader("templates"))

# Definiamo il modello di input, aspettandoci un campo 'data' con una struttura generica
class PdfRequest(BaseModel):
    data: dict

@app.get("/")
def home():
    # Endpoint di benvenuto per verificare che il servizio sia attivo
    return {"message": "PDF Service is running 🚀"}

@app.post("/generate-pdf")
async def generate_pdf(body: PdfRequest):
    # Dati da passare al template HTML
    data = body.data

    # Carica il template HTML
    template = env.get_template("report.html")
    
    # Renderizza il template con i dati ricevuti
    html_content = template.render(data=data)

    # Configurazione per il PDF: formato personalizzato e orientamento orizzontale
    options = {
        'orientation': 'Landscape',
        'page-width': '1440px',
        'page-height': '810px',
        'margin-top': '0mm',
        'margin-right': '0mm',
        'margin-bottom': '0mm',
        'margin-left': '0mm',
    }
    
    # Converte HTML in PDF, passando le opzioni di formato
    pdf_bytes = pdfkit.from_string(html_content, False, options=options)

    # Restituisce il PDF come file in streaming
    return StreamingResponse(io.BytesIO(pdf_bytes), media_type="application/pdf", headers={
        "Content-Disposition": "inline; filename=analisi.pdf"
    })
