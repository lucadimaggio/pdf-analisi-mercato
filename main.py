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
pdfmetrics.registerFont(TTFont("Montserrat-Regular", "fonts/Montserrat-Regular.ttf", subfontIndex=0))
pdfmetrics.registerFont(TTFont("Montserrat-Bold", "fonts/Montserrat-Bold.ttf", subfontIndex=0))
pdfmetrics.registerFont(TTFont("Montserrat-ExtraBold", "fonts/Montserrat-ExtraBold.ttf", subfontIndex=0))


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



def draw_page_header(c):
    # Titolo principale
    c.setFont("Montserrat-ExtraBold", 80)
    c.drawString(100, 675, "ANALISI DI MERCATO")

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




def render_section_to_buffer(section_title, draw_func):
    """
    Crea un buffer PDF per una singola sezione.
    - section_title: titolo/sottotitolo della sezione
    - draw_func: funzione che accetta (canvas, page_width, page_height) e disegna il contenuto
    """
    section_buffer = io.BytesIO()
    c = canvas.Canvas(section_buffer, pagesize=(1440, 810))

    # Colori gradiente
    top = HexColor("#000000")
    mid = HexColor("#001373")
    bottom = HexColor("#000000")
    white = HexColor("#FFFFFF")

    # Sfondo gradiente
    draw_vertical_gradient(c, 1440, 810, top, mid, bottom)

    # Header
    c.setFillColor(white)
    draw_page_header(c)

    # Sottotitolo
    if section_title:
        c.setFont("Montserrat-Regular", 26)
        c.drawString(100, 626, section_title.upper())

    # Disegna contenuto personalizzato
    draw_func(c, 1440, 810)

    # Salva il buffer
    c.save()
    section_buffer.seek(0)
    return section_buffer


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





 

    
    def draw_page_layout(c, subtitle):
        # Titolo principale
        c.setFont("Montserrat-ExtraBold", 80)
        c.setFillColor(white)
        c.drawString(100, 675, "ANALISI DI MERCATO")

        # Sottotitolo dinamico
        c.setFont("Montserrat-Regular", 26)
        c.drawString(100, 626, subtitle.upper())

    # Funzione per disegnare una sezione con titolo e contenuto
    def draw_section(c, x, y, title, content, max_width):
        c.setFont("Montserrat-Bold", 14)
        c.setFillColor(HexColor("#4a4a4a"))
        c.drawString(x, y, title)

      

    



    # Dimensioni della pagina 16:9 in punti (da 1440x810 px, a 96 DPI)
    page_size = (1440, 810)
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

    
    margin = 81           # ≈ 144
    bottom_margin = 60     # ≈ 106
    col_width = 450
    col_x_pos = margin
    content_x_pos = col_x_pos + col_width + margin
    y_pos = page_height - margin

    def check_and_new_page(c, current_y, subtitle=None):
        if current_y < bottom_margin:
            c.showPage()
            draw_vertical_gradient(c, page_width, page_height, top, mid, bottom)
            c.setFillColor(white)
            draw_page_header(c)  # aggiunge titolo fisso

            
            
            # Se è stato passato un sottotitolo, ridisegnalo
            if subtitle:
                c.setFont("Montserrat-Regular", 26)
                c.drawString(100, 626, subtitle.upper())
            
            return page_height - 300  # riparte sotto il paragrafo fisso
            
        return current_y


    def draw_benefici_section(c, page_width, page_height, data):
        benefici_raw = data.get("benefici_prodotti", "")
        benefici_list = benefici_raw.split("|") if benefici_raw else []

        spiegazione_raw = data.get("spiegazione_benefici_prodotti", "")
        spiegazione_list = spiegazione_raw.split("|") if spiegazione_raw else []

        y_pos = page_height - 300
        count = 0  # contatore benefici nella pagina
        max_per_page = 2

        for idx, beneficio in enumerate(benefici_list):
            beneficio = beneficio.strip()
            spiegazione = spiegazione_list[idx].strip() if idx < len(spiegazione_list) else ""

            # Se ho già stampato 2 benefici, forzo nuova pagina
            if count >= max_per_page:
                c.showPage()
                draw_vertical_gradient(c, page_width, page_height, HexColor("#000000"), HexColor("#001373"), HexColor("#000000"))
                c.setFillColor(HexColor("#FFFFFF"))
                draw_page_header(c)
                c.setFont("Montserrat-Regular", 26)
                c.drawString(100, 626, "BENEFICI PER IL CLIENTE")
                y_pos = page_height - 300
                count = 0

            # Disegna beneficio
            c.setFont("Montserrat-Bold", 29.2)
            text_beneficio = f"- {beneficio}"
            c.drawString(100, y_pos, text_beneficio)
            y_pos -= 36

            # Disegna spiegazione
            if spiegazione:
                c.setFont("Montserrat-Regular", 29.2)
                text_lines = simpleSplit(spiegazione, "Montserrat-Regular", 29.2, page_width - 200)
                for line in text_lines:
                    y_pos = check_and_new_page(c, y_pos, subtitle="BENEFICI PER IL CLIENTE")
                    c.drawString(120, y_pos, line)
                    y_pos -= 36

            y_pos -= 30
            count += 1
    
    def draw_bisogni_section(c, page_width, page_height, data):
        bisogni_raw = data.get("bisogni_robbins", "")
        bisogni_list = bisogni_raw.split("|") if bisogni_raw else []

        spieg_bisogni_raw = data.get("spiegazione_bisogni_robbins", "")
        spieg_bisogni_list = spieg_bisogni_raw.split("|") if spieg_bisogni_raw else []

        y_pos = page_height - 300
        count = 0
        max_per_page = 2

        for idx, bisogno in enumerate(bisogni_list):
            bisogno = bisogno.strip()
            spiegazione = spieg_bisogni_list[idx].strip() if idx < len(spieg_bisogni_list) else ""

            if count >= max_per_page:
                c.showPage()
                draw_vertical_gradient(c, page_width, page_height, HexColor("#000000"), HexColor("#001373"), HexColor("#000000"))
                c.setFillColor(HexColor("#FFFFFF"))
                draw_page_header(c)
                c.setFont("Montserrat-Regular", 26)
                c.drawString(100, 626, "BISOGNI PRIMARI (SECONDO LA TEORIA DI ROBBINS)")
                y_pos = page_height - 300
                count = 0

            c.setFont("Montserrat-Bold", 29.2)
            c.drawString(100, y_pos, f"- {bisogno}")
            y_pos -= 36

            if spiegazione:
                c.setFont("Montserrat-Regular", 29.2)
                text_lines = simpleSplit(spiegazione, "Montserrat-Regular", 29.2, page_width - 200)
                for line in text_lines:
                    y_pos = check_and_new_page(c, y_pos, subtitle="BISOGNI PRIMARI (SECONDO LA TEORIA DI ROBBINS)")
                    c.drawString(120, y_pos, line)
                    y_pos -= 36

            y_pos -= 30
            count += 1

    def draw_demografici_section(c, page_width, page_height, data):
        draw_vertical_gradient(c, page_width, page_height, HexColor("#000000"), HexColor("#001373"), HexColor("#000000"))
        c.setFillColor(HexColor("#FFFFFF"))
        draw_page_header(c)
        c.setFont("Montserrat-Regular", 26)
        c.drawString(100, 626, "DATI DEMOGRAFICI")

        target = data.get("target_demografico", {})

        # 🔹 Divisione manuale in due gruppi
        labels_page1 = ["Età", "Genere", "Professione"]
        values_page1 = [
            target.get("eta", ""),
            target.get("genere", ""),
            target.get("professione", ""),
        ]

        labels_page2 = ["Interessi", "Stile di vita"]
        values_page2 = [
            target.get("interessi", ""),
            target.get("stile_vita", ""),
        ]

        # 🔹 Prima pagina (Età, Genere, Professione)
        y_pos = page_height - 300
        for label, value in zip(labels_page1, values_page1):
            y_pos = check_and_new_page(c, y_pos, subtitle="DATI DEMOGRAFICI")

            # Label in bold (solo titolo, senza valore accanto)
            c.setFont("Montserrat-Bold", 29.2)
            c.drawString(100, y_pos, f"- {label}")
            y_pos -= 36


            # Valore in regular sotto il label
            c.setFont("Montserrat-Regular", 29.2)
            text_lines = simpleSplit(value, "Montserrat-Regular", 29.2, page_width - 200)
            for line in text_lines:
                y_pos = check_and_new_page(c, y_pos, subtitle="DATI DEMOGRAFICI")
                c.drawString(120, y_pos, line)
                y_pos -= 36

            y_pos -= 20

        # 🔹 Seconda pagina (Interessi, Stile di vita)
        c.showPage()
        draw_vertical_gradient(c, page_width, page_height, HexColor("#000000"), HexColor("#001373"), HexColor("#000000"))
        c.setFillColor(HexColor("#FFFFFF"))
        draw_page_header(c)
        c.setFont("Montserrat-Regular", 26)
        c.drawString(100, 626, "DATI DEMOGRAFICI")

        y_pos = page_height - 300
        for label, value in zip(labels_page2, values_page2):
            y_pos = check_and_new_page(c, y_pos, subtitle="DATI DEMOGRAFICI")

            # Label in bold (solo titolo, senza valore accanto)
            c.setFont("Montserrat-Bold", 29.2)
            c.drawString(100, y_pos, f"- {label}")
            y_pos -= 36


            # Valore in regular sotto il label
            c.setFont("Montserrat-Regular", 29.2)
            text_lines = simpleSplit(value, "Montserrat-Regular", 29.2, page_width - 200)
            for line in text_lines:
                y_pos = check_and_new_page(c, y_pos, subtitle="DATI DEMOGRAFICI")
                c.drawString(120, y_pos, line)
                y_pos -= 36


            y_pos -= 20


    def draw_obiezioni_section(c, page_width, page_height, data):
        obiezioni_data = data.get("obiezioni", {})

        obiezioni_labels = [
            "Necessità di risolvere il problema",
            "Possibilità di trovare una soluzione",
            "Tipo di soluzione proposta",
            "Possibilità di raggiungere i risultati",
            "Credibilità azienda"
        ]

        obiezioni_values = [
            obiezioni_data.get("necessita", ""),
            obiezioni_data.get("possibilita", ""),
            obiezioni_data.get("tipo_soluzione", ""),
            obiezioni_data.get("risultati", ""),
            obiezioni_data.get("credibilita_azienda", "")
        ]

        for idx, (label, value) in enumerate(zip(obiezioni_labels, obiezioni_values)):
            if idx > 0:  # Solo dalla seconda obiezione in poi
                c.showPage()
            draw_vertical_gradient(c, page_width, page_height, HexColor("#000000"), HexColor("#001373"), HexColor("#000000"))
            c.setFillColor(HexColor("#FFFFFF"))
            draw_page_header(c)
            c.setFont("Montserrat-Regular", 26)
            c.drawString(100, 626, "OBIEZIONI")
            c.setFont("Montserrat-Bold", 29.2)



            y_pos = page_height - 300

            c.drawString(100, y_pos, f"- {label}")
            y_pos -= 36

            if value:
                c.setFont("Montserrat-Regular", 29.2)
                sub_values = value.split("|")
                for sub in sub_values:
                    sub = sub.strip()
                    if not sub:
                        continue
                    text_lines = simpleSplit(sub, "Montserrat-Regular", 29.2, page_width - 200)
                    for line in text_lines:
                        y_pos = check_and_new_page(c, y_pos, subtitle="OBIEZIONI")
                        c.drawString(120, y_pos, line)
                        y_pos -= 36

            y_pos -= 30

    def draw_domande_section(c, page_width, page_height, data):
        draw_vertical_gradient(c, page_width, page_height, HexColor("#000000"), HexColor("#001373"), HexColor("#000000"))
        c.setFillColor(HexColor("#FFFFFF"))
        draw_page_header(c)
        c.setFont("Montserrat-Regular", 26)
        c.drawString(100, 626, "DOMANDE TECNICHE")

        domande_raw = data.get("domande_tecniche", "")
        domande_list = domande_raw.split("|") if domande_raw else []

        y_pos = page_height - 300
        count = 0
        max_per_page = 3

        for domanda in domande_list:
            domanda = domanda.strip()
            if not domanda:
                continue

            # Se raggiungo 3 domande, vado a nuova pagina
            if count >= max_per_page:
                c.showPage()
                draw_vertical_gradient(c, page_width, page_height, HexColor("#000000"), HexColor("#001373"), HexColor("#000000"))
                c.setFillColor(HexColor("#FFFFFF"))
                draw_page_header(c)
                c.setFont("Montserrat-Regular", 26)
                c.drawString(100, 626, "DOMANDE TECNICHE")
                y_pos = page_height - 300
                count = 0

            y_pos = check_and_new_page(c, y_pos, subtitle="DOMANDE TECNICHE")

            # Disegna la domanda in regular
            c.setFont("Montserrat-Regular", 29.2)
            text_lines = simpleSplit(f"- {domanda}", "Montserrat-Regular", 29.2, page_width - 200)
            for line in text_lines:
                y_pos = check_and_new_page(c, y_pos, subtitle="DOMANDE TECNICHE")
                c.drawString(100, y_pos, line)
                y_pos -= 36

            count += 1


    def draw_competitor_section(c, page_width, page_height, data):
        draw_vertical_gradient(c, page_width, page_height, HexColor("#000000"), HexColor("#001373"), HexColor("#000000"))
        c.setFillColor(HexColor("#FFFFFF"))
        draw_page_header(c)
        c.setFont("Montserrat-Regular", 26)
        c.drawString(100, 626, "POSSIBILI DIFFICOLTÀ")

        sito_web = data.get("sito_web", "il nostro Brand")

        y_pos = page_height - 300

        # Titolo sezione Competitor diretti
        c.setFont("Montserrat-Bold", 29.2)
        c.drawString(100, y_pos, "Competitor diretti:")
        y_pos -= 36

        c.setFont("Montserrat-Regular", 29.2)
        text_lines = simpleSplit(
            f"Questi brand vendono articoli simili a quelli offerti da {sito_web} e operano nel nostro stesso mercato.",
            "Montserrat-Regular", 29.2, page_width - 200
        )
        for line in text_lines:
            y_pos = check_and_new_page(c, y_pos, subtitle="POSSIBILI DIFFICOLTÀ")
            c.drawString(120, y_pos, line)
            y_pos -= 36

        # Titolo sezione Competitor indiretti
        y_pos -= 60
        c.setFont("Montserrat-Bold", 29.2)
        c.drawString(100, y_pos, "Competitor indiretti:")
        y_pos -= 36

        c.setFont("Montserrat-Regular", 29.2)
        text_lines = simpleSplit(
            f"Questi sono brand che soddisfano bisogni simili a quelli di {sito_web}, ma operano in mercati differenti.",
            "Montserrat-Regular", 29.2, page_width - 200
        )
        for line in text_lines:
            y_pos = check_and_new_page(c, y_pos, subtitle="POSSIBILI DIFFICOLTÀ")
            c.drawString(120, y_pos, line)
            y_pos -= 36

    def draw_bisogni_derivati_section(c, page_width, page_height, data):
        bisogni_derivati_raw = data.get("bisogni_derivati", "")
        bisogni_derivati_list = bisogni_derivati_raw.split("|") if bisogni_derivati_raw else []

        spieg_bisogni_derivati_raw = data.get("spiegazione_bisogni_derivati", "")
        spieg_bisogni_derivati_list = spieg_bisogni_derivati_raw.split("|") if spieg_bisogni_derivati_raw else []

        y_pos = page_height - 300
        count = 0
        max_per_page = 2

        for idx, bisogno in enumerate(bisogni_derivati_list):
            bisogno = bisogno.strip()
            spiegazione = spieg_bisogni_derivati_list[idx].strip() if idx < len(spieg_bisogni_derivati_list) else ""

            if count >= max_per_page:
                c.showPage()
                draw_vertical_gradient(c, page_width, page_height, HexColor("#000000"), HexColor("#001373"), HexColor("#000000"))
                c.setFillColor(HexColor("#FFFFFF"))
                draw_page_header(c)

                # Reimposta sempre i font dopo showPage()
                c.setFont("Montserrat-Regular", 26)
                c.drawString(100, 626, "BISOGNI DERIVATI")
                c.setFont("Montserrat-Bold", 29.2)

                y_pos = page_height - 300
                count = 0


            c.setFont("Montserrat-Bold", 29.2)
            c.drawString(100, y_pos, f"- {bisogno}")
            y_pos -= 36

            if spiegazione:
                c.setFont("Montserrat-Regular", 29.2)
                text_lines = simpleSplit(spiegazione, "Montserrat-Regular", 29.2, page_width - 200)
                for line in text_lines:
                    y_pos = check_and_new_page(c, y_pos, subtitle="BISOGNI DERIVATI")
                    c.drawString(120, y_pos, line)
                    y_pos -= 36

            y_pos -= 30
            count += 1


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
        c.setFont("Montserrat-Bold", 29.2)
        c.drawString(100, 472, section_title)

        # Punto di partenza sotto il titolo
        y_pos = page_height - 300

        # Ciclo sugli elementi
        for idx, item in enumerate(items):
            item = item.strip()
            explanation = explanations[idx].strip() if idx < len(explanations) else ""

            # Disegna "- item" in bold
            c.setFont("Montserrat-Bold", 29.2)
            text_item = f"- {item}"
            c.drawString(100, y_pos, text_item)
            y_pos -= 36

            if explanation:
                c.setFont("Montserrat-Regular", 29.2)
                text_lines = simpleSplit(explanation, "Montserrat-Regular", 29.2, page_width - 200)
                for line in text_lines:
                    y_pos = check_and_new_page(c, y_pos)
                    c.drawString(120, y_pos, line)
                    y_pos -= 36

            y_pos -= 20


        return y_pos



    benefici_buffer = render_section_to_buffer(
    "BENEFICI PER IL CLIENTE",
    lambda c, w, h: draw_benefici_section(c, w, h, body.data)
)


    bisogni_buffer = render_section_to_buffer(
        "BISOGNI PRIMARI (SECONDO LA TEORIA DI ROBBINS)",
        lambda c, w, h: draw_bisogni_section(c, w, h, body.data)
)

    demografici_buffer = render_section_to_buffer(
        "DATI DEMOGRAFICI",
        lambda c, w, h: draw_demografici_section(c, w, h, body.data)
    )

    obiezioni_buffer = render_section_to_buffer(
        "OBIEZIONI",
        lambda c, w, h: draw_obiezioni_section(c, w, h, body.data)
    )

    domande_buffer = render_section_to_buffer(
        "DOMANDE TECNICHE",
        lambda c, w, h: draw_domande_section(c, w, h, body.data)
    )

    competitor_buffer = render_section_to_buffer(
        "POSSIBILI DIFFICOLTÀ",
        lambda c, w, h: draw_competitor_section(c, w, h, body.data)
    )

    derivati_buffer = render_section_to_buffer(
        "BISOGNI DERIVATI",
        lambda c, w, h: draw_bisogni_derivati_section(c, w, h, body.data)
    )




 

    # Chiudi e copia il PDF intero in un buffer principale
    c.save()
    buffer.seek(0)

    # Carica PDF intero e splitta manualmente i blocchi
    custom_reader = PdfReader(buffer)

    # Assegna i blocchi a buffer separati

    try:
        # === NUOVO BLOCCO: Unisci il template standard con le pagine custom ===

        # Percorso del template (relativo alla posizione di main.py)
        base_dir = os.path.dirname(os.path.abspath(__file__))
        template_path = os.path.join(base_dir, "templates", "template_analisi.pdf")

        # Log per verificare se il file esiste
        logger.info(f"Percorso template: {template_path}")
        logger.info(f"File esiste? {os.path.exists(template_path)}")

        # Stampa il contenuto della cartella templates
        try:
            logger.info(f"Contenuto cartella templates: {os.listdir(os.path.join(base_dir, 'templates'))}")
        except Exception as e:
            logger.warning(f"Impossibile leggere cartella templates: {str(e)}")

        if not os.path.exists(template_path):
            raise HTTPException(status_code=500, detail=f"Template PDF non trovato: {template_path}")

        logger.info(f"Sto per aprire il template: {template_path}")

        try:
            template_reader = PdfReader(template_path)
            logger.info(f"Template caricato con {len(template_reader.pages)} pagine")
        except Exception as e:
            logger.error(f"Errore durante l'apertura del template: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Errore lettura template: {str(e)}")

        # Carica i blocchi custom
        benefici_reader = PdfReader(benefici_buffer)
        bisogni_reader = PdfReader(bisogni_buffer)
        demo_reader = PdfReader(demografici_buffer)
        obiezioni_reader = PdfReader(obiezioni_buffer)
        domande_reader = PdfReader(domande_buffer)
        competitor_reader = PdfReader(competitor_buffer)
        derivati_reader = PdfReader(derivati_buffer)

        logger.info(f"Benefici_buffer: {len(benefici_reader.pages)} pagine")
        logger.info(f"Bisogni_buffer: {len(bisogni_reader.pages)} pagine")
        logger.info(f"Demografici_buffer: {len(demo_reader.pages)} pagine")
        logger.info(f"Obiezioni_buffer: {len(obiezioni_reader.pages)} pagine")
        logger.info(f"Domande_buffer: {len(domande_reader.pages)} pagine")
        logger.info(f"Competitor_buffer: {len(competitor_reader.pages)} pagine")
        logger.info(f"Derivati_buffer: {len(derivati_reader.pages)} pagine")

        # Writer per il PDF finale
        final_writer = PdfWriter()
        logger.info(f"Template ha {len(template_reader.pages)} pagine totali")

        # --- Inserisci prime 3 pagine standard (se esistono) ---
        for i in range(min(3, len(template_reader.pages))):
            final_writer.add_page(template_reader.pages[i])

        # --- Inserisci blocchi custom ---
        for page in benefici_reader.pages: final_writer.add_page(page)
        for page in bisogni_reader.pages: final_writer.add_page(page)
        for page in demo_reader.pages: final_writer.add_page(page)

        # --- Inserisci pagina 4 standard (se esiste) ---
        if len(template_reader.pages) > 3:
            final_writer.add_page(template_reader.pages[3])

        # --- Inserisci altri blocchi custom ---
        for page in obiezioni_reader.pages: final_writer.add_page(page)
        for page in domande_reader.pages: final_writer.add_page(page)
        for page in competitor_reader.pages: final_writer.add_page(page)

        # --- Inserisci pagine standard da 5 a 59 (se esistono) ---
        for i in range(4, min(59, len(template_reader.pages))):
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
        
        import re

        sito_web = body.data.get("sito_web", "cliente")
        sito_web_safe = re.sub(r'[^a-zA-Z0-9_-]', '_', sito_web)


        return StreamingResponse(final_buffer, media_type="application/pdf", headers={
    "Content-Disposition": f"inline; filename=analisi_{sito_web_safe}.pdf"
})


    except Exception as e:
        logger.error(f"Errore generazione PDF: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Errore PDF: {str(e)}")
