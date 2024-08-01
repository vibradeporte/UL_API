from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
import requests
from dotenv import load_dotenv
import os
from return_codes import *
import re
from typing import List
from jwt_manager import JWTBearer

# Cargar variables de entorno desde el archivo .env
load_dotenv()

ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')

envio_mensajes_whatsapp_router = APIRouter()

class MessageRequest(BaseModel):
    numero: str
    parametros: List[str]

@envio_mensajes_whatsapp_router.post("/envio_mensajes_whatsapp",tags=['whatsapp'], status_code=200, dependencies=[Depends(JWTBearer())])
async def send_messages(plantilla: str, id_telefono: str, mensajes: List[MessageRequest]=None):
    """
    ## **Descripción:**
    Esta función permite enviar mensajes a whatsapp colectivamente.

    ## **Parámetros obligatorios:**
        - plantilla -> Nombre de la plantilla creada previamente en el API de WhatsApp.
        - id_telefono -> Id del número desde el cual se van a enviar los mensajes.
        - mensajes -> Lista de objetos que contiene todos los campos a enviar en la plantilla.

    ## **Códigos retornados:**
        - 200 -> Los mensajes se enviaron correctamente.
        - 453 -> 
        - 454 -> 
    """
    regex = r'^[0-9]+$'
    
    for mensaje in mensajes:
        if len(mensaje.numero) > 20:
            codigo = SOBRAN_CARACTERES_20
            mensaje_texto = HTTP_MESSAGES.get(codigo)
            raise HTTPException(codigo, mensaje_texto)
        
        if not re.match(regex, mensaje.numero):
            codigo = TELEFONO_INCORRECTO
            mensaje_texto = HTTP_MESSAGES.get(codigo)
            raise HTTPException(codigo, mensaje_texto)
    
    FACEBOOK_API_URL = f"https://graph.facebook.com/v19.0/{id_telefono}/messages"

    headers = {
        'Authorization': f'Bearer {ACCESS_TOKEN}',
        'Content-Type': 'application/json'
    }

    results = []
    
    for mensaje in mensajes:
        parameters = [{"type": "text", "text": param} for param in mensaje.parametros]
        
        data = {
            "messaging_product": "whatsapp",
            "to": mensaje.numero,
            "type": "template",
            "template": {
                "name": plantilla,
                "language": {
                    "code": "es"
                },
                "components": [
                    {
                        "type": "body",
                        "parameters": parameters
                    }
                ]
            }
        }

        response = requests.post(FACEBOOK_API_URL, headers=headers, json=data)
        if response.status_code != 200:
            results.append({
                "numero": mensaje.numero,
                "status": response.status_code,
                "error": response.text
            })
        else:
            results.append(response.json())
    
    return results
