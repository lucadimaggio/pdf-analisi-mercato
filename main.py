from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from jinja2 import Environment, FileSystemLoader
import pdfkit
import io

app = FastAPI()

# Configurazione Jinja2
env = Environment(loader=FileSystemLoader("templates"))

@app.get("/")
def home():
    return {"message": "PDF Service is running 🚀"}

@app.post("/generate-pdf")
async def generate_pdf(request: Request):
    # Prendi il JSON (anche se per ora non lo usiamo)
    data = await request.json()

    # Renderizza il template HTML (report.html)
    template = env.get_template("report.html")
    html_content = template.render(message="Analisi di mercato generata con successo (via pdfkit)")

    # Configura pdfkit per usare il binario dentro /app/bin/ (Railway)
    config = pdfkit.configuration(wkhtmltopdf="/app/bin/wkhtmltopdf")

    # Converte HTML in PDF usando pdfkit
    pdf_bytes = pdfkit.from_string(html_content, False, configuration=config)


    # Restituisce il PDF come file
    return StreamingResponse(io.BytesIO(pdf_bytes), media_type="application/pdf", headers={
        "Content-Disposition": "inline; filename=analisi.pdf"
    })
