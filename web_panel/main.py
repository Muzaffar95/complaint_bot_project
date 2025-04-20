from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from web_panel.routes import router

app = FastAPI(title="Complaint Admin Panel")

# Раздача PDF-файлов
app.mount("/pdfs", StaticFiles(directory="pdfs"), name="pdfs")

# Роуты (панель и фильтры)
app.include_router(router)

