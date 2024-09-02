from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from cryptography.fernet import Fernet
from jwt_manager import JWTBearer

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Obtener la clave secreta desde las variables de entorno
KEY_SECRETA = os.getenv('KEY')

if not KEY_SECRETA:
    raise ValueError("KEY no está definida en las variables de entorno")

encriptar_contraseñas_router = APIRouter()

class EncriptarContraseñaRequest(BaseModel):
    dato: str
    key: str

@encriptar_contraseñas_router.post("/encriptar_contraseñas", tags=['Contraseñas'], status_code=200, dependencies=[Depends(JWTBearer())])
async def encriptar_contraseñas(request: EncriptarContraseñaRequest):
    """
    ## **Descripción:**
    Esta función se encarga de encriptar contraseñas antes de almacenarlas en la base de datos.

    ## **Parámetros obligatorios:**
        - dato -> Contraseña a encriptar.
        - key -> Key secreta para encriptar y desencriptar datos.
        
    ## **Códigos retornados:**
        - 200 -> Contraseña encriptada.
        
    """
    # Comparar la clave proporcionada con la clave secreta almacenada en el entorno
    if request.key != KEY_SECRETA:
        raise HTTPException(status_code=403, detail="Clave secreta incorrecta")

    try:
        fernet = Fernet(request.key.encode('utf-8'))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al inicializar Fernet: " + str(e))

    # Datos a encriptar
    data = request.dato.encode()

    try:
        # Encriptar los datos
        encrypted_data = fernet.encrypt(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al encriptar los datos: " + str(e))

    # Devolver la contraseña encriptada como una cadena en base64
    return {"contraseña_encriptada": encrypted_data.decode('utf-8')}
