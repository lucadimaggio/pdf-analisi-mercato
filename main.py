import os
import pdfkit
import io
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from jinja2 import Environment, FileSystemLoader
from pydantic import BaseModel

app = FastAPI()

# Configurazione Jinja2
env = Environment(loader=FileSystemLoader("templates"))

# Definiamo il modello di input
class PdfRequest(BaseModel):
    message: str | None = "Analisi di mercato generata con successo (via pdfkit)"


@app.get("/")
def home():
    return {"message": "PDF Service is running 🚀"}


@app.post("/generate-pdf")
async def generate_pdf(body: PdfRequest):
    html_message = body.message

    template = env.get_template("report.html")
    html_content = template.render(message=html_message)

    # Converte HTML in PDF. Non serve la configurazione personalizzata
    # perché il binario sarà nel PATH di sistema (sia locale che su Railway).
    pdf_bytes = pdfkit.from_string(html_content, False)

    # Restituisce il PDF come file
    return StreamingResponse(io.BytesIO(pdf_bytes), media_type="application/pdf", headers={
        "Content-Disposition": "inline; filename=analisi.pdf"
    })
