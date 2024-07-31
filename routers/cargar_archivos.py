from fastapi import APIRouter, Depends, Request, File, UploadFile
from fastapi.responses import JSONResponse
import os
from datetime import datetime
from jwt_manager import JWTBearer

cargar_archivos = APIRouter()

@cargar_archivos.post("/cargar_archivos/", dependencies=[Depends(JWTBearer())])
async def upload_file(request: Request, file: UploadFile = File(...)):
    # Directorio temporal
    temp_dir = "static/temp_files"
    os.makedirs(temp_dir, exist_ok=True)

    # Obtener la fecha y hora actual para agregar al nombre del archivo
    now = datetime.now().strftime("%Y%m%d%H%M%S")
    
    # Crear el nuevo nombre del archivo con la fecha y hora
    new_filename = f"{os.path.splitext(file.filename)[0]}_{now}{os.path.splitext(file.filename)[1]}"
    new_file_path = os.path.join(temp_dir, new_filename)
    
    # Guardar el archivo subido
    with open(new_file_path, "wb") as buffer:
        buffer.write(await file.read())

    # Generar la URL para la descarga del archivo
    path = os.path.join(new_filename).replace("\\", "/")

    # Devolver la URL del archivo modificado
    response = {
        "path": path
    }

    return JSONResponse(content=response)
