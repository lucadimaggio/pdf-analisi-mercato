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
from PyPDF2 import PdfReader, PdfWriter



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
            current_y = check_and_new_page(c, current_y)
            c.drawString(value_x_start, current_y, line)
            current_y -= 15

        
        return current_y

    # Funzione per disegnare un paragrafo con wrapping del testo
    def draw_paragraph(c, x, y, text, max_width, font_size=12, leading=14):
        c.setFont("Montserrat-Regular", font_size)
        text_lines = simpleSplit(text, "Montserrat-Regular", font_size, max_width)
        
        current_y = y
        for line in text_lines:
            current_y = check_and_new_page(c, current_y)
            c.drawString(x, current_y, line)
            current_y -= leading

        
        return current_y

    # Funzione per disegnare una sezione con titolo e contenuto
    def draw_section(c, x, y, title, content, max_width):
        c.setFont("Montserrat-Bold", 14)
        c.setFillColor(HexColor("#4a4a4a"))
        c.drawString(x, y, title)

    def draw_page_header(c):
        # Titolo principale
        c.setFont("Montserrat-Bold", 60)
        c.setFillColor(white)
        c.drawString(81, page_height - 81, "ANALISI DI MERCATO")

        # Sottotitolo
        c.setFont("Montserrat-Regular", 19.5)
        c.drawString(81, page_height - 176, "DATI RACCOLTI")

        # Paragrafo fisso
        c.setFont("Montserrat-Bold", 22)
        c.drawString(81, page_height - 240, "Benefici dei prodotti:")

    
    def draw_page_layout(c, title, subtitle, paragraph):
        # Titolo principale
        c.setFont("Montserrat-Bold", 60)  # grandezza proporzionata
        c.setFillColor(white)
        c.drawString(81, page_height - 81, title.upper())

        # Sottotitolo
        c.setFont("Montserrat-Regular", 19.5)
        c.drawString(81, page_height - 176, subtitle.upper())

        # Paragrafo
        c.setFont("Montserrat-Regular", 22)
        text_lines = simpleSplit(paragraph, "Montserrat-Regular", 22, 1278)
        current_y = page_height - 240
        for line in text_lines:
            current_y = check_and_new_page(c, current_y)
            c.drawString(81, current_y, line)
            current_y -= 26

        return current_y
    
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
    bottom_margin = 60
    col_width = 450
    col_x_pos = margin
    content_x_pos = col_x_pos + col_width + margin
    y_pos = page_height - margin

    def check_and_new_page(c, current_y):
        if current_y < bottom_margin:
            c.showPage()
            draw_vertical_gradient(c, page_width, page_height, top, mid, bottom)
            c.setFillColor(white)
            draw_page_header(c)  # aggiunge titolo fisso e paragrafo
            return page_height - 300  # riparte sotto il paragrafo fisso
            
        return current_y

    def draw_section_page(c, section_title, items, explanations):
        """
        Crea una nuova pagina con header fisso, titolo di sezione e lista punti.
        """
        # Nuova pagina con gradiente e header
        c.showPage()
        draw_vertical_gradient(c, page_width, page_height, top, mid, bottom)
        c.setFillColor(white)
        draw_page_header(c)

        # Titolo sezione
        c.setFont("Montserrat-Bold", 22)
        c.drawString(81, page_height - 240, section_title)

        # Punto di partenza sotto il titolo
        y_pos = page_height - 300

        # Ciclo sugli elementi
        for idx, item in enumerate(items):
            item = item.strip()
            explanation = explanations[idx].strip() if idx < len(explanations) else ""

            # Disegna "- item" in bold
            c.setFont("Montserrat-Bold", 18)
            text_item = f"- {item}"
            c.drawString(100, y_pos, text_item)

            # Calcola posizione X per continuare
            x_offset = 100 + c.stringWidth(text_item, "Montserrat-Bold", 18)

            # Disegna ": spiegazione" in regular
            if explanation:
                c.setFont("Montserrat-Regular", 18)
                c.drawString(x_offset + 5, y_pos, f": {explanation}")

            y_pos -= 26

        return y_pos



     # Titolo + sottotitolo + paragrafo fisso
    benefici_raw = body.data.get("benefici_prodotti", "")
    benefici_list = benefici_raw.split("|") if benefici_raw else []

    # Disegna header fisso sulla prima pagina
    draw_page_header(c)

    # Punto di partenza sotto il paragrafo fisso
    y_pos = page_height - 300

    # Stampa i benefici dinamici con relative spiegazioni
    spiegazione_raw = body.data.get("spiegazione_benefici_prodotti", "")
    spiegazione_list = spiegazione_raw.split("|") if spiegazione_raw else []

    for idx, beneficio in enumerate(benefici_list):
        beneficio = beneficio.strip()
        spiegazione = spiegazione_list[idx].strip() if idx < len(spiegazione_list) else ""

        y_pos = check_and_new_page(c, y_pos)

        # Disegna "- beneficio" in bold
        c.setFont("Montserrat-Bold", 18)
        text_beneficio = f"- {beneficio}"
        c.drawString(100, y_pos, text_beneficio)

        # Calcola posizione X per continuare dopo il beneficio
        x_offset = 100 + c.stringWidth(text_beneficio, "Montserrat-Bold", 18)

        # Disegna ": spiegazione" in regular
        if spiegazione:
            c.setFont("Montserrat-Regular", 18)
            c.drawString(x_offset + 5, y_pos, f": {spiegazione}")

        y_pos -= 26

    y_pos -= 40  # spazio extra prima della sezione successiva

    # Recupera i dati dei bisogni di Robbins
    bisogni_raw = body.data.get("bisogni_robbins", "")
    bisogni_list = bisogni_raw.split("|") if bisogni_raw else []

    spieg_bisogni_raw = body.data.get("spiegazione_bisogni_robbins", "")
    spieg_bisogni_list = spieg_bisogni_raw.split("|") if spieg_bisogni_raw else []

    # Crea nuova pagina con titolo e bisogni
    draw_section_page(c, "Bisogni Primari (secondo la Teoria di Robbins):", bisogni_list, spieg_bisogni_list)
        
    # Recupera i dati demografici
    target = body.data.get("target_demografico", {})
    demographics_labels = ["Età", "Genere", "Professione", "Interessi", "Stile di vita"]
    demographics_values = [
        target.get("eta", ""),
        target.get("genere", ""),
        target.get("professione", ""),
        target.get("interessi", ""),
        target.get("stile_vita", ""),
    ]

    # Crea nuova pagina con titolo e dati demografici
    draw_section_page(c, "Dati demografici:", demographics_labels, demographics_values)

        # Recupera le obiezioni
    obiezioni_data = body.data.get("obiezioni", {})
    obiezioni_labels = ["Necessità di risolvere il problema", "Possibilità di trovare una soluzione", "Tipo di soluzione proposta", "Possibilità di raggiungere i risultati", "Credibilità azienda"]
    obiezioni_values = [
        obiezioni_data.get("necessita", ""),
        obiezioni_data.get("possibilita", ""),
        obiezioni_data.get("tipo", ""),
        obiezioni_data.get("risultati", ""),
        obiezioni_data.get("credibilita_azienda", ""),
    ]

    # Crea nuova pagina con titolo POSSIBILI DIFFICOLTÀ e obiezioni
    draw_section_page(c, "Obiezioni:", obiezioni_labels, obiezioni_values)

    # Recupera le domande tecniche
    domande_raw = body.data.get("domande_tecniche", "")
    domande_list = domande_raw.split("|") if domande_raw else []

    # Crea nuova pagina con titolo e domande tecniche
    draw_section_page(c, "Domande tecniche:", domande_list, [])

    # Recupera il sito web
    sito_web = body.data.get("sito_web", "il nostro sito")

    # Crea nuova pagina con titolo e competitor
    c.showPage()
    draw_vertical_gradient(c, page_width, page_height, top, mid, bottom)
    c.setFillColor(white)

    # Header della pagina
    c.setFont("Montserrat-Bold", 60)
    c.drawString(81, page_height - 81, "ANALISI DI MERCATO")

    c.setFont("Montserrat-Regular", 19.5)
    c.drawString(81, page_height - 176, "POSSIBILI DIFFICOLTÀ")

    # Paragrafo Competitor diretti
    y_pos = page_height - 260
    c.setFont("Montserrat-Bold", 18)
    c.drawString(81, y_pos, "Competitor diretti:")
    c.setFont("Montserrat-Regular", 18)
    c.drawString(300, y_pos, f"Questi brand vendono articoli simili a quelli offerti da {sito_web} e operano nel nostro stesso mercato.")

    # Paragrafo Competitor indiretti
    y_pos -= 60
    c.setFont("Montserrat-Bold", 18)
    c.drawString(81, y_pos, "Competitor indiretti:")
    c.setFont("Montserrat-Regular", 18)
    c.drawString(300, y_pos, f"Questi sono brand che soddisfano bisogni simili a quelli di {sito_web}, ma operano in mercati differenti.")


    # Recupera i bisogni derivati
    bisogni_derivati_raw = body.data.get("bisogni_derivati", "")
    bisogni_derivati_list = bisogni_derivati_raw.split("|") if bisogni_derivati_raw else []

    spieg_bisogni_derivati_raw = body.data.get("spiegazione_bisogni_derivati", "")
    spieg_bisogni_derivati_list = spieg_bisogni_derivati_raw.split("|") if spieg_bisogni_derivati_raw else []

    # Crea nuova pagina con titolo e bisogni derivati
    draw_section_page(c, "Bisogni Derivati:", bisogni_derivati_list, spieg_bisogni_derivati_list)

    # Salva ogni blocco in un buffer separato
    benefici_buffer = io.BytesIO()
    bis_bisogni_buffer = io.BytesIO()
    demografici_buffer = io.BytesIO()
    obiezioni_buffer = io.BytesIO()
    domande_buffer = io.BytesIO()
    competitor_buffer = io.BytesIO()
    derivati_buffer = io.BytesIO()

    # Chiudi e copia il PDF intero in un buffer principale
    c.save()
    buffer.seek(0)

    # Carica PDF intero e splitta manualmente i blocchi
    custom_reader = PdfReader(buffer)

    # Assegna i blocchi a buffer separati
    def save_block(pages, out_buffer):
        writer = PdfWriter()
        for page in pages:
            writer.add_page(page)
        writer.write(out_buffer)
        out_buffer.seek(0)

    save_block(custom_reader.pages[0:1], benefici_buffer)          # benefici
    save_block(custom_reader.pages[1:2], bis_bisogni_buffer)       # bisogni primari
    save_block(custom_reader.pages[2:3], demografici_buffer)       # demografici
    save_block(custom_reader.pages[3:4], obiezioni_buffer)         # obiezioni
    save_block(custom_reader.pages[4:5], domande_buffer)           # domande
    save_block(custom_reader.pages[5:6], competitor_buffer)        # competitor
    save_block(custom_reader.pages[6:], derivati_buffer)           # bisogni derivati
    



    # === NUOVO BLOCCO: Unisci il template standard con le pagine custom ===
    from PyPDF2 import PdfReader, PdfWriter

    # Percorso del template (relativo alla posizione di main.py)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(base_dir, "templates", "template analisi di mercato.pdf")

    # Log per verificare se il file esiste
    logger.info(f"Percorso template: {template_path}")
    logger.info(f"File esiste? {os.path.exists(template_path)}")

    if not os.path.exists(template_path):
        raise HTTPException(status_code=500, detail=f"Template PDF non trovato: {template_path}")

    # Carica PDF standard (da Canva)
    template_reader = PdfReader(template_path)


    # Carica i blocchi custom
    benefici_reader = PdfReader(benefici_buffer)
    bisogni_reader = PdfReader(bis_bisogni_buffer)
    demo_reader = PdfReader(demografici_buffer)
    obiezioni_reader = PdfReader(obiezioni_buffer)
    domande_reader = PdfReader(domande_buffer)
    competitor_reader = PdfReader(competitor_buffer)
    derivati_reader = PdfReader(derivati_buffer)

    # Writer per il PDF finale
    final_writer = PdfWriter()

    # --- Inserisci prime 3 pagine standard ---
    for i in range(3):
        final_writer.add_page(template_reader.pages[i])

    # --- Inserisci blocchi custom ---
    for page in benefici_reader.pages: final_writer.add_page(page)
    for page in bisogni_reader.pages: final_writer.add_page(page)
    for page in demo_reader.pages: final_writer.add_page(page)

    # --- Inserisci pagina 4 standard ---
    final_writer.add_page(template_reader.pages[3])

    # --- Inserisci altri blocchi custom ---
    for page in obiezioni_reader.pages: final_writer.add_page(page)
    for page in domande_reader.pages: final_writer.add_page(page)
    for page in competitor_reader.pages: final_writer.add_page(page)

    # --- Inserisci pagine standard da 5 a 59 ---
    for i in range(4, 59):
        final_writer.add_page(template_reader.pages[i])

    # --- Inserisci bisogni derivati ---
    for page in derivati_reader.pages: final_writer.add_page(page)

    # --- Inserisci eventuali pagine restanti ---
    for i in range(59, len(template_reader.pages)):
        final_writer.add_page(template_reader.pages[i])


    # Salva il risultato in un nuovo buffer
    final_buffer = io.BytesIO()
    final_writer.write(final_buffer)
    final_buffer.seek(0)


    return StreamingResponse(final_buffer, media_type="application/pdf", headers={
        "Content-Disposition": "inline; filename=analisi.pdf"
    })
