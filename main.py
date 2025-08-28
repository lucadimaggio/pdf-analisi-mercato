from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "PDF Service is running 🚀"}

@app.post("/generate-pdf")
def generate_pdf():
    return {"status": "ok", "message": "Qui in futuro genereremo il PDF"}
