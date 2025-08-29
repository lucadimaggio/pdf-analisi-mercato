import os
import io
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import logging
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.utils import simpleSplit
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.colors import HexColor, Color
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Registra i font Montserrat
pdfmetrics.registerFont(TTFont("Montserrat-Regular", "fonts/Montserrat-Regular.ttf"))
pdfmetrics.registerFont(TTFont("Montserrat-Bold", "fonts/Montserrat-Bold.ttf"))


# Imposta il logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Definiamo il modello di input
class PdfRequest(BaseModel):
    data: dict

@app.get("/")
def home():
    return {"message": "PDF Service is running with ReportLab 🚀"}

@app.post("/generate-pdf")
async def generate_pdf(body: PdfRequest):
    logger.info(f"Dati ricevuti per la generazione del PDF: {body.data}")

    buffer = io.BytesIO()
    
    # Funzione per disegnare chiavi e valori con wrapping del testo
    def draw_key_value(c, x, y, key, value, max_width):
        c.setFont("Montserrat-Bold", 12)
        c.drawString(x, y, key)
        c.setFont("Montserrat-Regular", 12)
        
        # Calcola la larghezza disponibile per il testo del valore
        value_x_start = x + c.stringWidth(key, "Montserrat-Bold", 12) + 5
        value_width = max_width - (value_x_start - x)
        
        # Suddividi il testo in righe che si adattano alla larghezza
        text_lines = simpleSplit(value, "Montserrat-Regular", 12, value_width)
        
        current_y = y
        for line in text_lines:
            c.drawString(value_x_start, current_y, line)
            current_y -= 15
        
        return current_y

    # Funzione per disegnare un paragrafo con wrapping del testo
    def draw_paragraph(c, x, y, text, max_width, font_size=12, leading=14):
        c.setFont("Montserrat-Regular", font_size)
        text_lines = simpleSplit(text, "Montserrat-Regular", font_size, max_width)
        
        current_y = y
        for line in text_lines:
            c.drawString(x, current_y, line)
            current_y -= leading
        
        return current_y

    # Funzione per disegnare una sezione con titolo e contenuto
    def draw_section(c, x, y, title, content, max_width):
        c.setFont("Montserrat-Bold", 14)
        c.setFillColor(HexColor("#4a4a4a"))
        c.drawString(x, y, title)
        y -= 20
        y = draw_paragraph(c, x, y, content, max_width)
        return y
    

    def draw_vertical_gradient(c, width, height, top_color, mid_color, bottom_color, steps=200):
        """
        Disegna un gradiente verticale (90°) da top → mid → bottom.
        """
        for i in range(steps):
            ratio = i / (steps - 1)
            if ratio < 0.5:
                local_ratio = ratio / 0.5
                r = top_color.red + (mid_color.red - top_color.red) * local_ratio
                g = top_color.green + (mid_color.green - top_color.green) * local_ratio
                b = top_color.blue + (mid_color.blue - top_color.blue) * local_ratio
            else:
                local_ratio = (ratio - 0.5) / 0.5
                r = mid_color.red + (bottom_color.red - mid_color.red) * local_ratio
                g = mid_color.green + (bottom_color.green - mid_color.green) * local_ratio
                b = mid_color.blue + (bottom_color.blue - mid_color.blue) * local_ratio

            c.setFillColor(Color(r, g, b))
            y = int(height * ratio)
            c.rect(0, y, width, height / steps + 1, stroke=0, fill=1)


    # Dimensioni della pagina 16:9 in punti (da 1440x810 px, a 96 DPI)
    # 1440 px / 96 dpi * 72 pt/pollice = 1080 pt
    # 810 px / 96 dpi * 72 pt/pollice = 607.5 pt
    page_size = (1080, 607.5)
    c = canvas.Canvas(buffer, pagesize=page_size)

    # Posizionamento
    page_width, page_height = page_size

    # Colori gradiente
    top = HexColor("#000000")      # nero
    mid = HexColor("#001373")      # blu
    bottom = HexColor("#000000")   # nero

    # Disegna sfondo gradiente
    draw_vertical_gradient(c, page_width, page_height, top, mid, bottom)

    # Stili di base e colori
    white = HexColor("#FFFFFF")

    
    margin = 81
    col_width = 450
    col_x_pos = margin
    content_x_pos = col_x_pos + col_width + margin
    y_pos = page_height - margin

    # Titolo del report
    report_title = "ANALISI PMP ALFAMIX"
    c.setFont("Montserrat-Bold", 24)
    c.setFillColor(white)
    c.drawCentredString(margin, y_pos - 20, report_title)
    
    y_pos -= 60
    
    # Dati del cliente
    c.setFont("Montserrat-Bold", 14)
    c.setFillColor(white)
    c.drawString(col_x_pos, y_pos, "DATI CLIENTE")
    y_pos -= 20
    
    y_pos = draw_key_value(c, col_x_pos, y_pos, "Ragione Sociale:", body.data.get("ragione_sociale", ""), col_width)
    y_pos -= 10
    y_pos = draw_key_value(c, col_x_pos, y_pos, "Sito Web:", body.data.get("sito_web", ""), col_width)
    y_pos -= 10
    y_pos = draw_key_value(c, col_x_pos, y_pos, "Descrizione Business:", body.data.get("descrizione_business", ""), col_width)
    y_pos -= 10
    y_pos = draw_key_value(c, col_x_pos, y_pos, "Differenziazione:", body.data.get("differenziazione", ""), col_width)
    y_pos -= 10
    
    # --- Nuova sezione per Target Demografico ---
    y_pos -= 30
    c.setFont("Montserrat-Bold", 14)
    c.drawString(col_x_pos, y_pos, "TARGET DEMOGRAFICO")
    y_pos -= 20
    
    target_data = body.data.get("target_demografico", {})
    y_pos = draw_key_value(c, col_x_pos, y_pos, "Età:", target_data.get("eta", ""), col_width)
    y_pos -= 10
    y_pos = draw_key_value(c, col_x_pos, y_pos, "Genere:", target_data.get("genere", ""), col_width)
    y_pos -= 10
    y_pos = draw_key_value(c, col_x_pos, y_pos, "Professione:", target_data.get("professione", ""), col_width)
    
    # --- Nuove sezioni per Benefici e Obiezioni ---
    y_pos -= 30
    c.setFont("Montserrat-Bold", 14)
    c.drawString(col_x_pos, y_pos, "BENEFICI E OBIEZIONI")
    y_pos -= 20
    
    y_pos = draw_key_value(c, col_x_pos, y_pos, "Benefici:", body.data.get("benefici_prodotti", ""), col_width)
    y_pos -= 10
    y_pos = draw_key_value(c, col_x_pos, y_pos, "Obiezioni:", body.data.get("obiezioni", {}).get("necessita", ""), col_width)
    
    # --- Nuova sezione per Bisogni di Robbins ---
    y_pos -= 30
    c.setFont("Montserrat-Bold", 14)
    c.drawString(col_x_pos, y_pos, "BISOGNI DI ROBBINS")
    y_pos -= 20
    y_pos = draw_paragraph(c, col_x_pos, y_pos, body.data.get("bisogni_robbins", ""), col_width)

    c.save()

    buffer.seek(0)
    return StreamingResponse(buffer, media_type="application/pdf", headers={
        "Content-Disposition": "inline; filename=analisi.pdf"
    })
