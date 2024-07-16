import requests
import fitz  # PyMuPDF
import io
import base64

from openai import OpenAI

import json

import datetime

import re

import random

def pdf_to_image_message(pdf_url):
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

def cv_get_data(image_urls, api_key):

  client = OpenAI(api_key = api_key)

  MODEL="gpt-4o"

  system_message = f"""Eres un especilista extrayendo informacion de las imagens del CV de una persona para rellenar los campos de un json en los que se colocara la informacion extraida del CV.
**Objetivo:**
A continuación, se presenta un JSON con campos valor vacíos que representan la estructura esperada para extraer datos de un currículo. Usa este JSON como plantilla para rellenar con los datos extraídos del currículo proporcionado. Los valores deben ser vacíos. Después, se proporciona un ejemplo de cómo debería verse el JSON una vez rellenado con datos de un currículo.

**Materiales Proveídos:**
- **Imágenes del CV:** Incluye toda la informacion personal de la persona lo cual es el foco principal de extraccion de los datos.

### Estructura del JSON Vacía


{{
  "competencias": [
    {{
      "nombre": "Fortalezas",
      "valor": []
    }},
    {{
      "nombre": "Debilidades",
      "valor": []
    }},
    {{
      "nombre": "Hobbies",
      "valor": []
    }},
    {{
      "nombre": "Motivación",
      "valor": ""
    }}
  ],
  "datos": [
    {{
      "id": "name",
      "nombre": "Nombre",
      "valor": ""
    }},
    {{
      "id": "email",
      "nombre": "Correo",
      "valor": ""
    }},
    {{
      "nombre": "Fuente",
      "privado": true,
      "valor": []
    }},
    {{
      "nombre": "Rol",
      "valor": []
    }},
    {{
      "nombre": "Que Rol deseas Desempeñar en 1 a 2 años",
      "privado": true,
      "valor": []
    }},
    {{
      "nombre": "Nivel",
      "valor": []
    }},
    {{
      "nombre": "Modalidad",
      "valor": []
    }},
    {{
      "nombre": "Edad",
      "valor": ""
    }},
    {{
      "nombre": "Años de Experiencia",
      "valor": ""
    }},
    {{
      "id": "linkedIn",
      "nombre": "Linkedin",
      "type": "url",
      "valor": ""
    }}
  ],
  "default": {{
    "footer": [
      {{
        "nombre": "Resumen",
        "valor": ""
      }}
    ]
  }},

  "nombre": "",
  "profileImgUrl": "",
  "skills": [],
  "telefono": null,
  "timestamp": ""
}}
```

### Ejemplo de JSON Relleno

Ejemplo de Datos del Currículo (Ejemplo):
- Nombre: Juan Pérez
- Correo: juan.perez@example.com
- Edad: 30
- Años de Experiencia: 8
- Linkedin: https://linkedin.com/in/juanperez
- Fortalezas: Trabajo en equipo, Liderazgo
- Debilidades: Perfeccionismo
- Hobbies: Lectura, Ciclismo
- Motivación: Crecimiento profesional
- Fuente: Referencia interna
- Rol: Desarrollador de Software
- Que Rol deseas Desempeñar en 1 a 2 años: Gerente de Proyectos
- Nivel: Senior
- Modalidad: Remoto
- Resumen: Profesional con más de 8 años de experiencia en desarrollo de software.
- Habilidades: Python, JavaScript, Gestión de proyectos
- Teléfono: 555-1234
- Timestamp: 2024-06-25

JSON Relleno:
{{
  "competencias": [
    {{
      "nombre": "Fortalezas",
      "valor": ["Trabajo en equipo", "Liderazgo"]
    }},
    {{
      "nombre": "Debilidades",
      "valor": ["Perfeccionismo"]
    }},
    {{
      "nombre": "Hobbies",
      "valor": ["Lectura", "Ciclismo"]
    }},
    {{
      "nombre": "Motivación",
      "valor": "Crecimiento profesional"
    }}
  ],
  "datos": [
    {{
      "id": "name",
      "nombre": "Nombre",
      "valor": "Juan Pérez"
    }},
    {{
      "id": "email",
      "nombre": "Correo",
      "valor": "juan.perez@example.com"
    }},
    {{
      "nombre": "Fuente",
      "privado": true,
      "valor": ["Referencia interna"]
    }},
    {{
      "nombre": "Rol",
      "valor": ["Desarrollador de Software"]
    }},
    {{
      "nombre": "Que Rol deseas Desempeñar en 1 a 2 años",
      "privado": true,
      "valor": ["Gerente de Proyectos"]
    }},
    {{
      "nombre": "Nivel",
      "valor": ["Senior"]
    }},
    {{
      "nombre": "Modalidad",
      "valor": ["Remoto"]
    }},
    {{
      "nombre": "Edad",
      "valor": "30"
    }},
    {{
      "nombre": "Años de Experiencia",
      "valor": "8"
    }},
    {{
      "id": "linkedIn",
      "nombre": "Linkedin",
      "type": "url",
      "valor": "https://linkedin.com/in/juanperez"
    }}
  ],
  "default": {{
    "footer": [
      {{
        "nombre": "Resumen",
        "valor": "Profesional con más de 8 años de experiencia en desarrollo de software."
      }}
    ]
  }},

  "nombre": "Juan Pérez",
  "profileImgUrl": "",
  "skills": ["Python", "JavaScript", "Gestión de proyectos"],
  "telefono": "555-1234",
  "timestamp": ""
}}

Este prompt detallado está ajustado según tus especificaciones para facilitar la extracción de datos de un currículo utilizando un sistema automatizado o manual.
No incluyas etiquetas de Json ni nada similar, solo responde con la estructura especificada y tampoco argumentes ni des niguna explicacion, responde unicamente con la estrutura definida.
"""


  user_message = f"""Extrae la informacion presente en las siguientes imagenes de CV:
"""

  response = client.chat.completions.create(
      model=MODEL,
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

      try:
        now_utc = datetime.datetime.now(datetime.timezone.utc)

        iso_format_z = now_utc.isoformat().replace('+00:00', 'Z')

        respuesta['timestamp'] = iso_format_z
      except:
        pass

      try:
        if 'skills' in respuesta:
          respuesta['skills'] = []
        else:
          respuesta['skills'] = []
      except:
        pass


      try:
        if 'telefono' in  respuesta:
          telefono = respuesta['telefono']

          if type(telefono) is str and len(telefono):
            numeros = re.findall(r'\d+', telefono)
            numero_limpio = ''.join(numeros)
            respuesta['telefono'] = int(numero_limpio)

          elif type(telefono) is int:
            pass

          else:
            respuesta['telefono'] = int(''.join([str(random.randint(1,9)) for i in range(0,8)]) + '0000')

            if 'nombre' in respuesta:
              respuesta['nombre'] += '--SIN TELEFONO IDENTIFICADO'
      except:
        pass

      try:
        respuesta["estado"] = "Carga Candidato"
      except:
        pass


      return respuesta
    except:
      con -= 1

  return None