from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from routers.userlog import userlog_router
from fastapi.staticfiles import StaticFiles
import requests
from routers.cargar_archivos import cargar_archivos
from routers.correos import correo_archivo_adjunto_router
from routers.transcribe import transcribe_app
from routers.envio_mensajes_whatsapp import envio_mensajes_whatsapp_router
from routers.sms import sms_router
from routers.desencriptar_contraseña import desencriptar_contraseñas_router
from routers.encriptar_contraseña import encriptar_contraseñas_router

app = FastAPI()
app.title = "Universal Learning API"
app.version = "0.0.1"

# Configuración de CORS
origins = [
    "https://elasistenteia.com",
    "https://fastapitesting-production.up.railway.app/",
    "https://fastapi-production-e76b.up.railway.app/",
    "https://adminmoodle-production-98d3.up.railway.app/",
    "https://asistentecomercial-production.up.railway.app/"
    # Agrega aquí cualquier otro origen que necesites permitir
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(userlog_router)
app.include_router(cargar_archivos)

app.include_router(transcribe_app)
app.include_router(correo_archivo_adjunto_router)
app.include_router(envio_mensajes_whatsapp_router)

app.include_router(sms_router)

app.include_router(encriptar_contraseñas_router)
app.include_router(desencriptar_contraseñas_router)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get('/', tags=['home'])
def message():
    response = requests.get('https://ipinfo.io/ip')
    ip_address = response.text.strip()
    print(ip_address)
    return HTMLResponse(f'<h1>Universal Learning API</h1><p>Client IP: {ip_address}</p>')
