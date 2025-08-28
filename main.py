from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import io

app = FastAPI()

# Configurazione Jinja2: cerca i template nella cartella "templates"
env = Environment(loader=FileSystemLoader("templates"))

@app.get("/")
def home():
    return {"message": "PDF Service is running 🚀"}

@app.post("/generate-pdf")
async def generate_pdf(request: Request):
    # Prendiamo il JSON inviato da n8n o da Postman
    data = await request.json()

    # Per ora ignoriamo i dati e facciamo solo un PDF base
    template = env.get_template("report.html")
    html_content = template.render(message="Analisi di mercato generata con successo")

    # Convertiamo in PDF con WeasyPrint
    pdf_file = HTML(string=html_content).write_pdf()

    # Restituiamo il PDF come risposta
    return StreamingResponse(io.BytesIO(pdf_file), media_type="application/pdf", headers={
        "Content-Disposition": "inline; filename=analisi.pdf"
    })
