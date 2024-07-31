from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from routers.userlog import userlog_router
from fastapi.staticfiles import StaticFiles
import requests
from routers.cargar_archivos import cargar_archivos



app = FastAPI()
app.title = "Universal Learning API"
app.version = "0.0.1"


app.include_router(userlog_router)

app.include_router(cargar_archivos)


app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get('/', tags=['home'])
def message():
    response = requests.get('https://ipinfo.io/ip')
    ip_address = response.text.strip()
    print(ip_address)
    return HTMLResponse(f'<h1>Universal Learning API</h1><p>Client IP: {ip_address}</p>')
