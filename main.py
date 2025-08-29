import os
import io
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import logging
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.utils import simpleSplit
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.colors import black, HexColor

# Imposta il logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Definiamo il modello di input
class PdfRequest(BaseModel):
    data: dict | None = None

@app.get("/")
def home():
    return {"message": "PDF Service is running with ReportLab 🚀"}

@app.post("/generate-pdf")
async def generate_pdf(body: PdfRequest):
    logger.info(f"Dati ricevuti per la generazione del PDF: {body.data}")

    buffer = io.BytesIO()
    
    # Dimensioni della pagina 16:9 in punti (da 1440x810 px, a 96 DPI)
    # 1440 px / 96 dpi * 72 pt/pollice = 1080 pt
    # 810 px / 96 dpi * 72 pt/pollice = 607.5 pt
    page_size = (1080, 607.5)
    c = canvas.Canvas(buffer, pagesize=page_size)
    
    # Stili di base
    styles = getSampleStyleSheet()
    normal_style = styles['Normal']
    heading_style = styles['Heading1']
    heading_style.alignment = TA_CENTER
    normal_style.alignment = TA_LEFT
    normal_style.fontSize = 12
    normal_style.leading = 14  # Spaziatura tra le righe
    
    # Colori
    gray = HexColor("#4a4a4a")
    dark_gray = HexColor("#2c2c2c")

    # Posizionamento
    page_width, page_height = page_size
    margin = 50
    
    # --- Colonna laterale per le informazioni chiave ---
    col_width = 300
    col_x_pos = margin
    content_x_pos = col_x_pos + col_width + margin
    y_pos = page_height - margin

    # Titolo del report
    report_title = "ANALISI PMP ALFAMIX"
    c.setFont("Helvetica-Bold", 24)
    c.setFillColor(dark_gray)
    c.drawCentredString(page_width / 2, y_pos - 20, report_title)
    
    y_pos -= 60
    
    # Dati del cliente nella colonna laterale
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(gray)
    c.drawString(col_x_pos, y_pos, "DATI CLIENTE")
    y_pos -= 20
    
    c.setFont("Helvetica", 12)
    y_pos = draw_key_value(c, col_x_pos, y_pos, "Ragione Sociale:", body.data.get("cliente", {}).get("ragione_sociale", ""), col_width)
    y_pos = draw_key_value(c, col_x_pos, y_pos, "Sito Web:", body.data.get("cliente", {}).get("sito_web", ""), col_width)
    
    c.line(col_x_pos, y_pos - 10, col_x_pos + col_width, y_pos - 10)
    y_pos -= 30
    
    # Altre sezioni nella colonna laterale
    c.setFont("Helvetica-Bold", 14)
    c.drawString(col_x_pos, y_pos, "TARGET DEMOGRAFICO")
    y_pos -= 20
    y_pos = draw_key_value(c, col_x_pos, y_pos, "Età:", body.data.get("target_demografico", {}).get("eta", ""), col_width)
    y_pos = draw_key_value(c, col_x_pos, y_pos, "Genere:", body.data.get("target_demografico", {}).get("genere", ""), col_width)
    
    # --- Contenuti principali a destra ---
    
    content_y_pos = page_height - margin - 60
    
    c.setFont("Helvetica-Bold", 14)
    c.drawString(content_x_pos, content_y_pos, "DESCRIZIONE BUSINESS")
    content_y_pos -= 20
    
    business_desc = body.data.get("cliente", {}).get("descrizione_business", "")
    content_y_pos = draw_paragraph(c, content_x_pos, content_y_pos, business_desc, page_width - content_x_pos - margin)
    
    # Funzione per disegnare chiavi e valori
    def draw_key_value(canvas, x, y, key, value, max_width):
        canvas.setFont("Helvetica-Bold", 12)
        canvas.drawString(x, y, key)
        canvas.setFont("Helvetica", 12)
        
        y -= 15
        
        # Gestione del wrapping del testo
        text_lines = simpleSplit(value, "Helvetica", 12, max_width - canvas.stringWidth(key, "Helvetica-Bold", 12) - 10)
        for line in text_lines:
            canvas.drawString(x + canvas.stringWidth(key, "Helvetica-Bold", 12) + 5, y, line)
            y -= 15
        return y

    # Funzione per disegnare un paragrafo
    def draw_paragraph(canvas, x, y, text, max_width):
        style = styles['Normal']
        style.alignment = TA_LEFT
        p = Paragraph(text, style)
        w, h = p.wrapOn(canvas, max_width, page_height)
        p.drawOn(canvas, x, y - h)
        return y - h - 15

    # Altri dati...
    # Puoi aggiungere altre sezioni del report in modo simile
    
    c.save()

    buffer.seek(0)
    return StreamingResponse(buffer, media_type="application/pdf", headers={
        "Content-Disposition": "inline; filename=analisi.pdf"
    })
