from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import Dict
from fastapi.responses import JSONResponse
import uvicorn
import os
from dotenv import load_dotenv

from cv_module.cv_score import cv_score
from test_module.test_score import test_score
from linkedin_module.linkedin_score import linkedin_score

load_dotenv()

app = FastAPI()

API_KEY_AUTH = os.getenv('API_KEY_AUTH')

if API_KEY_AUTH is None:
    raise Exception("API_KEY_AUTH not configured in .env file")

def get_api_key(api_key_auth: str = Header(...)):
    if api_key_auth != API_KEY_AUTH:
        raise HTTPException(status_code=403, detail="Unauthorized")
    return api_key_auth


# EndPoint Linkedin

class RequestDataLk(BaseModel):
    json_data: Dict
    url_perfil: str

@app.post("/analizar_linkedin")
async def analizar_linkedin(request_data: RequestDataLk, api_key_auth: str = Depends(get_api_key)):
    try:
        json_str = request_data.json_data
        url_perfil = request_data.url_perfil

        resultado = linkedin_score(url_perfil, json_str, api_key=os.getenv('API_KEY_MODEL'))

        return JSONResponse(content={"resultado": resultado}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# EndPoint CV

class RequestDataCv(BaseModel):
    json_data: Dict
    pdf_url: str
    
@app.post("/analizar_cv")
async def analizar_cv(request_data: RequestDataCv, api_key_auth: str = Depends(get_api_key)):
    try:
        json_str = request_data.json_data
        pdf_url = request_data.pdf_url

        resultado = cv_score(pdf_url, json_str, api_key=os.getenv('API_KEY_MODEL'))

        return JSONResponse(content={"resultado": resultado}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# EndPoint Test Gorila

class RequestDataG(BaseModel):
    pdf_url: str

@app.post("/analizar_test")
async def analizar_test(request_data: RequestDataG, api_key_auth: str = Depends(get_api_key)):
    try:
        pdf_url = request_data.pdf_url

        resultado = test_score(pdf_url, api_key=os.getenv('API_KEY_MODEL'))

        return JSONResponse(content={"resultado": resultado}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)





#uvicorn main:app --reload