
import os
import requests
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from jwt_manager import JWTBearer

load_dotenv()
AUTH_KEY = os.getenv("AUTH_KEY")
API_URL = "https://api.turbo-smtp.com/api/v2/mail/send"
AUTH_USER_TSMTP = os.getenv("AUTH_USER_TSMTP")
AUTH_PASS_TSMTP = os.getenv("AUTH_PASS_TSMTP")
MVAPI_KEY = os.getenv("MVAPI_KEY")

MAX_LENGTH_CORREO = 80

class AttachmentSchema(BaseModel):
    content: str
    name: str
    type: str

class EmailSchema(BaseModel):
    from_e: EmailStr = Field(..., max_length=MAX_LENGTH_CORREO)
    to: EmailStr = Field(..., max_length=MAX_LENGTH_CORREO)
    subject: str
    cc: str
    html_content: str
    content: str
    attachments: Optional[List[AttachmentSchema]] = None

class EmailBatchSchema(BaseModel):
    emails: List[EmailSchema]

correo_archivo_adjunto_router = APIRouter()

@correo_archivo_adjunto_router.post("/enviar_correos_archivo_adjunto", tags=['correo'], status_code=200, dependencies=[Depends(JWTBearer())])
def enviar_correos(batch: EmailBatchSchema):
    """
    ## **Descripción:**
    Esta función permite enviar correos electrónicos usando SMTP TURBO.

    ## **Parámetros obligatorios:**
        - from -> Dirección de correo eléctronico desde donde se enviará el mensaje.
        - to -> Dirección de correo eléctronico destinatario del mensaje.
        - subject -> Asunto del mensaje.
        - content -> Texto con el contenido del cuerpo del correo.
    ## **Parámetros opcionales:**
        - cc -> Enviar copia del mensaje a otro destinatario.
        - bcc -> Enviar copia del mensaje a otro destinatario en oculto.
        
        - html_content -> Contenido del cuerpo del correo en formato HTML.
        - attachments -> En caso de necesitar anexar un documento al mensaje, deberá ser ingresado por medio de attachments con los siguientes parámetros:
            - content -> Corresponde al archivo en base64.
            - name -> Corresponde al nombre del archivo.
            - type -> Corresponde al tipo de archivo.

    ## **Códigos retornados:**
        - 200 -> La operación se realizó correctamente.
        - 452 -> No se pudo realizar la operación.
        
    """
    if not AUTH_USER_TSMTP or not AUTH_PASS_TSMTP or not AUTH_KEY:
        raise HTTPException(status_code=500, detail="Missing email authentication credentials")

    message_ids = []

    for email in batch.emails:
        data = {
            "authuser": AUTH_USER_TSMTP,
            "authpass": AUTH_PASS_TSMTP,
            "from": email.from_e,
            "to": email.to,
            "subject": email.subject,
            "content": email.content,
            "html_content": email.html_content,
        }

        if email.cc:
            data["cc"] = email.cc

        if email.attachments:
            data["attachments"] = [
                {
                    "content": attachment.content,
                    "name": attachment.name,
                    "type": attachment.type
                } for attachment in email.attachments
            ]

        headers = {
            'Authorization': AUTH_KEY
        }

        try:
            response = requests.post(API_URL, headers=headers, json=data)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=500, detail=f"Error sending email to {email.to}: {str(e)}")

        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=f"Error sending email to {email.to}: {response.text}")

        response_data = response.json()
        message_id = response_data.get('mid')
        if message_id:
            message_ids.append(message_id)

    return {"message": "Todos los correos fueron enviados exitosamente.", "message_ids": message_ids}




#Servicio para realizar verificacion de correos con la plataforma millionviewer
@correo_archivo_adjunto_router.get("/verificar_email/", tags=['correo'], status_code=200, dependencies=[Depends(JWTBearer())])
def verificar_correo(email: str = Query(max_length=MAX_LENGTH_CORREO)):
    """
    ## **Descripción:**
    Esta función permite verificar la calidad de un correo electrónico.

    ## **Parámetros obligatorios:**
        - email -> Dirección de correo eléctronico a validar.
        

    ## **Códigos retornados:**
        - 200 -> Datos del análisis del correo electrónico ingresado.
        - 500 -> Error en la solicitud a MillionVerifier
    """
    url = f"https://api.millionverifier.com/api/v3/?api={MVAPI_KEY}&email={email}&timeout=20"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()  # Devuelve la respuesta de la API como JSON
        else:
            raise HTTPException(status_code=response.status_code, detail="Error en la solicitud a MillionVerifier")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
