from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from jinja2 import Environment, FileSystemLoader
import pdfkit
import io
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
    # Usa il valore del body, o il default se non presente
    html_message = body.message

    # Renderizza il template HTML (report.html)
    template = env.get_template("report.html")
    html_content = template.render(message=html_message)

    # Configura pdfkit per usare il binario wkhtmltopdf
    config = pdfkit.configuration(wkhtmltopdf="/app/bin/wkhtmltopdf")

    # Converte HTML in PDF
    pdf_bytes = pdfkit.from_string(html_content, False, configuration=config)

    # Restituisce il PDF come file
    return StreamingResponse(io.BytesIO(pdf_bytes), media_type="application/pdf", headers={
        "Content-Disposition": "inline; filename=analisi.pdf"
    })
