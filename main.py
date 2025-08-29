import os
import pdfkit
import io
from fastapi import FastAPI
from fastapi.responses import StreamingResponse, Response
from jinja2 import Environment, FileSystemLoader
from pydantic import BaseModel
from typing import Dict, Any

app = FastAPI()

# Configurazione Jinja2
env = Environment(loader=FileSystemLoader("templates"))

# Modello di input aggiornato per accettare un JSON completo
class PdfRequest(BaseModel):
    data: Dict[str, Any]

@app.get("/")
def home():
    """Endpoint per verificare se il servizio è attivo."""
    return {"message": "PDF Service is running 🚀"}

@app.post("/generate-pdf")
async def generate_pdf(body: PdfRequest):
    """
    Endpoint che riceve dati JSON, li usa per renderizzare un template HTML
    e restituisce un file PDF.
    """
    try:
        # Carica il template HTML
        template = env.get_template("report.html")

        # Passa i dati dal corpo della richiesta al template
        # Il modello dei dati è 'data', quindi accediamo con body.data
        html_content = template.render(data=body.data)

        # Definisci le opzioni di configurazione per il PDF
        # Dimensioni personalizzate e orientamento orizzontale
        options = {
            'orientation': 'Landscape',
            'page-width': '1440px',
            'page-height': '810px',
            'margin-top': '0mm',
            'margin-right': '0mm',
            'margin-bottom': '0mm',
            'margin-left': '0mm'
        }

        # Converte l'HTML in PDF usando pdfkit con le opzioni
        pdf_bytes = pdfkit.from_string(html_content, False, options=options)

        # Restituisce il PDF come file
        return StreamingResponse(io.BytesIO(pdf_bytes), media_type="application/pdf", headers={
            "Content-Disposition": "inline; filename=analisi.pdf"
        })
    except Exception as e:
        return Response(content=f"Errore durante la generazione del PDF: {str(e)}", status_code=500, media_type="text/plain")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
