import requests
import fitz  # PyMuPDF
import io
import base64

from openai import OpenAI

import json

import re

import random


def pdf_to_image_message(pdf_url:str)->list:
    # Descargar el PDF desde la URL
    response = requests.get(pdf_url)
    pdf_bytes = response.content

    # Cargar el PDF en PyMuPDF
    pdf_documento = fitz.open(stream=pdf_bytes, filetype="pdf")

    image_urls = []

    # Convertir cada página a una imagen y agregarla a la lista
    for pagina_num in range(len(pdf_documento)):
        pagina = pdf_documento.load_page(pagina_num)  # Cargar la página
        pix = pagina.get_pixmap()  # Obtener el pixmap de la página

        image_buffer = io.BytesIO(pix.tobytes(output="jpeg"))  # Convertir a bytes en formato JPEG
        base64_image = base64.b64encode(image_buffer.getvalue()).decode('utf-8')
        image_url = f"data:image/jpeg;base64,{base64_image}"
        image_urls.append({"type": "image_url", "image_url": {"url": image_url}})

    return image_urls


# ---------------------------------------------------------------------------------------------------------

def cv_get_data(image_urls:list, api_key:str) -> dict:

  client = OpenAI(api_key = api_key)

  system_message = f"""Eres un especialista extrayendo información de las imágenes del CV de una persona para rellenar los campos de un JSON en los que se colocará la información extraída del CV.
**Objetivo:**
A continuación, se presenta un JSON con campos valor vacíos que representan la estructura esperada para extraer datos de un currículo. Usa este JSON como plantilla para rellenar con los datos extraídos del currículo proporcionado. Los valores deben ser vacíos. Después, se proporciona un ejemplo de cómo debería verse el JSON una vez rellenado con datos de un currículo.

**Materiales Proveídos:**
- **Imágenes del CV:** Incluye toda la información personal de la persona lo cual es el foco principal de extracción de los datos.

**Estructura del JSON (vacío):**
{{
  "nombre": "",
  "telefono": "",
  "email": "",
  "linkedin": "",
  "resumen": ""
}}

**Ejemplo de JSON rellenado:**
{{
  "nombre": "Juan Pérez",
  "telefono": "+34 123 456 789",
  "email": "juan.perez@example.com",
  "linkedin": "https://www.linkedin.com/in/juanperez",
  "resumen": "Profesional con más de 10 años de experiencia en el sector financiero, especializado en análisis de inversiones y gestión de riesgos."
}}

No incluyas etiquetas de Json ni nada similar, solo responde con la estructura especificada y tampoco argumentes ni des niguna explicacion, responde unicamente con la estrutura definida.
"""

  user_message = f"""Extrae la informacion presente en las siguientes imagenes de CV:
"""

  response = client.chat.completions.create(
      model="gpt-4o",
      messages=[
          {"role": "system", "content": system_message},
          {"role": "user", "content": [
              {"type": "text", "text": user_message}
            ] + image_urls
          }
      ],
      temperature=0.0,
      top_p = 1,
      seed = 250
  )

  con = 3
  while con:
    try:
      respuesta = response.choices[0].message.content

      respuesta = json.loads(respuesta)
      
      return respuesta
    except:
      con -= 1

  return {"nombre": "",
          "telefono": "",
          "email": "",
          "linkedin": "",
          "resumen": "Error LLM OpenAI"}


# ----------------------------------------------------------------------------------------------------------------------------------

def generar_telefono_aleatorio():
    return int('1313' + ''.join([str(random.randint(0, 9)) for _ in range(7)]))

def proces_info(info_dict:dict)->dict:
  if 'telefono' in info_dict:

    telefono = info_dict['telefono']

    if isinstance(telefono, str) and telefono:
      telefono = int(re.sub(r'[^0-9]', '', info_dict['telefono']))
    elif isinstance(telefono, int):
      pass
    else:
      telefono = generar_telefono_aleatorio()
  else:
    telefono = generar_telefono_aleatorio()

  if 'nombre' in info_dict:
    nombre = info_dict['nombre']
  else:
    nombre = ""

  if 'email' in info_dict:
    email = info_dict['email']
  else:
    email = ""

  if 'linkedin' in info_dict:
    linkedin = info_dict['linkedin']
  else:
    linkedin = ""

  if 'resumen' in info_dict:
    resumen = info_dict['resumen']
  else:
    resumen = ""

  return {
          'nombre': nombre,
          'telefono': telefono,
          'datos':[{'nombre':'Correo', 'valor':email}, {'nombre': 'Linkedin','valor': linkedin}],
          'workflow':[{ 'nombre': 'Carga Candidato','feedback': resumen}]
          }