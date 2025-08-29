import os
import pdfkit
import io
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from jinja2 import Environment, FileSystemLoader
from pydantic import BaseModel
import logging

# Configurazione del logger
logging.basicConfig(level=logging.INFO)

# Inizializza l'applicazione FastAPI
app = FastAPI()

# Configurazione Jinja2 per i template HTML
env = Environment(loader=FileSystemLoader("templates"))

# Definiamo il modello di input, aspettandoci un campo 'data' con una struttura generica
class PdfRequest(BaseModel):
    data: dict

# Imposta il percorso di wkhtmltopdf se necessario (utile per ambienti di produzione come Railway)
# Il percorso corretto dipenderà dalla tua configurazione Dockerfile
WKHTMLTOPDF_PATH = os.environ.get('WKHTMLTOPDF_PATH', '/usr/local/bin/wkhtmltopdf')

# Controlla se il binario esiste
if not os.path.exists(WKHTMLTOPDF_PATH):
    logging.warning(f"wkhtmltopdf non trovato al percorso: {WKHTMLTOPDF_PATH}. Tentativo di utilizzo del PATH di sistema.")
    pdfkit_config = None
else:
    pdfkit_config = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_PATH)
    logging.info(f"wkhtmltopdf configurato al percorso: {WKHTMLTOPDF_PATH}")

@app.get("/")
def home():
    # Endpoint di benvenuto per verificare che il servizio sia attivo
    return {"message": "PDF Service is running 🚀"}

@app.post("/generate-pdf")
async def generate_pdf(body: PdfRequest):
    try:
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
            'page-size': None, # Rimuove l'impostazione predefinita del formato
        }
        
        # Converte HTML in PDF, passando le opzioni di formato e la configurazione
        pdf_bytes = pdfkit.from_string(html_content, False, options=options, configuration=pdfkit_config)

        # Restituisce il PDF come file in streaming
        return StreamingResponse(io.BytesIO(pdf_bytes), media_type="application/pdf", headers={
            "Content-Disposition": "inline; filename=analisi.pdf"
        })
    except Exception as e:
        logging.error(f"Errore durante la generazione del PDF: {e}")
        raise HTTPException(status_code=500, detail=f"Errore durante la generazione del PDF: {str(e)}")
