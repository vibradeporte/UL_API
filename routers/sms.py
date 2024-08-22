import http
from http.client import HTTPException
import json
import os
import requests
import base64
from dotenv import load_dotenv
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from fastapi import APIRouter, Query, Depends
from jwt_manager import JWTBearer
from typing import List

max_lenght_number = 15
max_lenght_mmsg = 160

class Recipient(BaseModel):
    msisdn: str = Field(..., max_length=max_lenght_number)

class SMSPayload(BaseModel):
    message: str = Field(..., max_length=max_lenght_mmsg)
    tpoa: str
    recipient: List[Recipient]

load_dotenv()
USER_NAME = os.getenv("AUTH_USER_LM")
PASS = os.getenv("LM_TOKEN")

sms_router = APIRouter()

#Servicio para realizar enviós de sms con Labs Mobile
@sms_router.post("/send_sms", tags=['sms'], status_code=200, dependencies=[Depends(JWTBearer())])
def enviar_sms(payload: SMSPayload):
    """
    ## **Descripción:**
    Esta función permite enviar mensajes sms a traves del api de la plataforma de labsmobile.

    ## **Parámetros obligatorios:**
        - message: Texto con el contenido del mensaje a enviar.
        - tpoa: Especificación del remitente del mensaje para que quede registro de quien envio el mensaje (el usuario al que le llega el mensaje no ve esta información).
        - recipients.msisdn: Número o numeros de celular a los que le llegara el mensaje de texto.

    ## **Códigos retornados:**
        - 200 -> La operación se realizó correctamente.
    """
    usrPass = f"{USER_NAME}:{PASS}"
    b64Val = base64.b64encode(bytes(usrPass, 'utf-8'))

    recipient_payload = [{"msisdn": recipient.msisdn} for recipient in payload.recipient]
    
    conn = http.client.HTTPSConnection("api.labsmobile.com")
    
    json_payload = {
        "message": payload.message,
        "tpoa": payload.tpoa,
        "recipient": recipient_payload
    }
    
    headers = {
        'Content-Type': "application/json",
        'Authorization':  "Basic %s" % b64Val.decode('utf-8'),
        'Cache-Control': "no-cache"
    }
    
    try:
        conn.request("POST", "/json/send", body=json.dumps(json_payload), headers=headers)
        res = conn.getresponse()
        data = res.read()
        return {"response": data.decode("utf-8")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))