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

desencriptar_contraseñas_router = APIRouter()

class DesencriptarContraseñaRequest(BaseModel):
    encrypted_data: str
    key: str

@desencriptar_contraseñas_router.post("/desencriptar_contraseñas", tags=['Contraseñas'], status_code=200, dependencies=[Depends(JWTBearer())])
async def desencriptar_contraseñas(request: DesencriptarContraseñaRequest):
    """
    ## **Descripción:**
    Esta función se encarga de desencriptar contraseñas que han sido encriptadas y almacenadas en la base de datos.

    ## **Parámetros obligatorios:**
        - encrypted_data -> Contraseña encriptada que se desea desencriptar.
        - key -> Key secreta para encriptar y desencriptar datos.
        
    ## **Códigos retornados:**
        - 200 -> Contraseña desencriptada.
        
    """
    # Comparar la clave proporcionada con la clave secreta almacenada en el entorno
    if request.key != KEY_SECRETA:
        raise HTTPException(status_code=403, detail="Clave secreta incorrecta")

    try:
        fernet = Fernet(request.key.encode('utf-8'))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al inicializar Fernet: " + str(e))

    try:
        # Decodificar los datos desde base64 y desencriptar
        encrypted_data = request.encrypted_data.encode('utf-8')
        decrypted_data = fernet.decrypt(encrypted_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al desencriptar los datos: " + str(e))

    # Devolver la contraseña desencriptada como una cadena
    return {"contraseña_desencriptada": decrypted_data.decode('utf-8')}
