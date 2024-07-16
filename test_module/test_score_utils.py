import requests
import fitz  # PyMuPDF
import io
import base64

from openai import OpenAI

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


#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def puntaje_eval(image_urls, api_key):

  client = OpenAI(api_key = api_key)

  MODEL="gpt-4o"

  system_message = f"""**Tarea: Extracción y Justificación del Puntaje Promedio de un Candidato**

**Objetivo:**
Extraer el puntaje promedio y proporcionar una justificación detallada utilizando los desgloses de desempeño detallados, los cuales se encuentran en imágenes de un PDF de evaluación de candidato.

**Materiales Proveídos:**
- **Imágenes de un PDF de Evaluación:** Cada imagen representa una página del PDF que contiene el puntaje promedio general y un desglose detallado por área de competencia evaluada.

**Instrucciones Detalladas:**

1. **Extracción del Puntaje Promedio:**
   - Identifica y registra el puntaje promedio general del candidato que se menciona en la primera imagen del PDF proporcionado.

2. **Análisis Detallado de la Evaluación:**
   - Examina las imágenes subsecuentes y extrae el puntaje obtenido en cada una de las competencais presentadas.
   
3. **Documentación de la Justificación:**
   - Basándote en la información proporcionada en las imágenes de las áreas específicas, elabora una justificación de por qué el puntaje promedio refleja adecuadamente las capacidades del candidato.
   - Incluye ejemplos específicos de las áreas de alta y baja puntuación para apoyar la justificación.

4. **Formato de Respuesta:**
   - El resultado debe ser un Diccionario de Python que contenga:
     - El puntaje promedio en forma numérica.
     - Puntaje de cada competencia
     - Una justificación textual de por qué se llegó a ese puntaje promedio. Si identificas que en los resultados se muestra que el candidato dejo preguntas sin responder, debes mencionarlo. Las preguntas sin responder corresponden a los segmentos de barras que estan de color gris

**Ejemplo de Estructura de Salida en Diccionario Python:**

{{
    "puntaje_promedio": 40,
    "evaluaciones": {{"Evaluacion 1": 43, "Evaluacion 2": 37}},
    "justificacion": "El candidato obtuvo un puntaje promedio del 40%, lo que refleja un desempeño variado en las diferentes áreas evaluadas. Destacó en ...."
}}

No incluyas etiquetas de Python ni nada similar, solo responde con la estructura especificada.
"""

  user_message = f"""Genera tu resumen para la siguinete evaluacion:
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
      seed = 300
  )

  con = 3
  while con:
    try:
      respuesta = response.choices[0].message.content

      respuesta = eval(respuesta)
      
      respuesta['score'] = respuesta['puntaje_promedio']/100
      
      return respuesta
    
    except:
      con -= 1

  return {'puntaje_promedio': 50, 'evaluaciones': {}, 'justificacion': 'Error: puntaje_eval: LLM no devuelve respuesta', 'score': 0.5}