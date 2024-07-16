import requests
import fitz  # PyMuPDF
import io
import base64

from openai import OpenAI

from bs4 import BeautifulSoup

from datetime import datetime, date

def procesar_json(json_vacante):

  rol = ', '.join(json_vacante['rol'])
  stack = ', '.join(json_vacante['stack'])

  soup = BeautifulSoup(json_vacante["descripcion"], "html.parser")
  description = soup.get_text(separator="\n")

  vacante = f"""**Rol:**  
  {rol}  

  **Stack:**  
  {stack}  

  **Descripcion:**  
  {description}
  """

  return vacante

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

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

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def puestos_relevantes(image_urls, vacante, api_key):

  client = OpenAI(api_key = api_key)

  MODEL="gpt-4o"

  hoy = date.today()
  hoy = hoy.strftime("%m/%Y")

  system_message = f"""**Tarea: Extracción de Fechas de Vacantes Relevantes de un CV**

**Objetivo:**
Extraer de un CV las fechas de inicio y fin de las posiciones laborales que sean relevantes para un puesto específico y proporcionar una justificación de por qué se seleccionaron estas vacantes.

**Materiales Proveídos:**
- **Imágenes del CV:** Incluyen experiencia laboral, educación, habilidades técnicas y certificaciones. Debes enfocarte únicamente en la experiencia laboral.
- **Descripción del Puesto Laboral:** Texto breve que detalla el título y el stack de habilidades requerido para el puesto.


**Instrucciones Detalladas:**

1. **Revisión del CV:**
   - Examina el CV para identificar todas las posiciones laborales listadas, registrando las fechas de inicio y fin de cada una.

2. **Identificación de Experiencias Relevantes:**
   - Selecciona solo aquellas posiciones que estén directamente relacionadas con las habilidades, el stack y requisitos del puesto que estás evaluando dado en **Descripción del Puesto Laboral**.

3. **Documentación de Fechas y Justificación:**
   - Para cada posición relevante, extrae las fechas de inicio y fin.
   - Proporciona una justificación clara de por qué cada posición fue seleccionada como relevante, basada en la descripción del puesto y las competencias necesarias.

4. **Formato de Respuesta:**
   - El resultado debe ser un Diccionario que contenga una lista con las fechas en formato numérico 'mes/año' ('%m/%Y') de las posiciones relevantes y una justificación de la elección, En caso de referise a actualidad como fecha en la fecha debes poner {hoy}.
   - El resultado debe incluir tambien el tiempo que se desempeñó la persona en el puesto en el fomrato de tupla: (años, meses).

**Ejemplo de Estructura de Salida en Diccionario de Python:**
{{
    "vacantes_relevantes": [
        {{
            "posicion": "Desarrollador Front-End",
            "empresa": "Empresa XYZ",
            "fecha_inicio": "03/2015",
            "fecha_fin": "05/2020",
            "tiempo": (5,2),
            "justificacion": "La posición coincide con las habilidades requeridas de desarrollo Front-End especificadas para el puesto actual."
        }},
        {{
            "posicion": "Ingeniero de Software",
            "empresa": "Empresa ABC",
            "fecha_inicio": "06/2018",
            "fecha_fin": "07/2021",
            "tiempo": (3,1),
            "justificacion": "El trabajo involucró tecnologías clave como React y Node.js, que son esenciales para el puesto actual."
        }}
    ]
}}

No incluyas etiquetas de Python ni nada similar, solo responde con la estructura especificada.
"""


  user_message = f"""Genera la evaluación para el siguiente Puesto Laboral y las imágenes del CV de la persona:
**Descripción del Puesto Laboral:**
{vacante}
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
      respuesta = eval(respuesta)
      return respuesta
    except:
      con -= 1

  return None

def suma_tiempo(dic_puestos_relevantes):

  suma_meses = 0

  for puesto in dic_puestos_relevantes['vacantes_relevantes']:

    try:
      inicio = puesto['fecha_inicio']
      fin = puesto['fecha_fin']

      fecha1_dt = datetime.strptime(inicio, '%m/%Y')
      fecha2_dt = datetime.strptime(fin, '%m/%Y')

      meses = (fecha2_dt.year - fecha1_dt.year) * 12 + (fecha2_dt.month - fecha1_dt.month)
    except:
      try:
        meses = puesto['tiempo'][0] * 12 + puesto['tiempo'][1]
      except:
        meses = 13

    if 12 <= meses <= 120:
      suma_meses += meses

  anhos = suma_meses // 12
  meses = suma_meses % 12

  return anhos, meses


def seniority_eval(image_urls, vacante, api_key):

  try:

    dic_puestos_relevantes = puestos_relevantes(image_urls, vacante, api_key)

    anhos, meses = suma_tiempo(dic_puestos_relevantes)

    tiempo = float(f"{anhos}.{str(meses)}")

    # el tiempo calculado en añ0s.meses
    if tiempo <= 1:
      seniority = 'Trainee'
      nota = round(1/5,2)

    elif 1 < tiempo <= 2:
      seniority = 'Junior'
      nota = round(2/5,2)

    elif 2 < tiempo <= 5:
      seniority = 'Semi_Senior'
      nota = round(3/5,2)

    elif 5 < tiempo <= 10:
      seniority = 'Senior'
      nota = round(4/5,2)

    else:
      seniority = 'Especialista'
      nota = 1.0

    try:

      justificacion = f'La persona tiene una experiencia laboral relevante con el puesto de {anhos} años y {meses} meses acumulados:\n\n'

      for puesto in dic_puestos_relevantes['vacantes_relevantes']:
        text = f"Puesto: {puesto['posicion']}\nEmpresa: {puesto['empresa']}\nFecha inicio: {puesto['fecha_inicio']}\nFecha final: {puesto['fecha_fin']}\nDescripcion: {puesto['justificacion']}\n-------"
        justificacion += text
    except:

      justificacion = 'Error justificacion seniority_eval'

    return {'nota': nota, 'nivel': seniority, 'justificacion': justificacion}

  except:
    return {'nota':0.5, 'nivel':'Indefinido', 'justificacion':'Error seniority_eval'}
  

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def stack_eval(image_urls, vacante, api_key):
  client = OpenAI(api_key = api_key)

  MODEL="gpt-4o"

  system_message = """Eres un especialista en evaluación de stacks tecnológicos. Tu tarea consiste en evaluar qué tan bien se ajusta el stack tecnológico que domina el profesional, según lo reflejado en su CV (proporcionado como imágenes), con el stack requerido para un puesto específico. La evaluación debe calificar el ajuste como Mal, Regular, Bien, Muy Bien o Excelente y proporcionar una justificación.

**Datos que recibirás:**
- **Imágenes del CV del Profesional:** Se te darán las imágenes del CV de la persona, incluyendo experiencia laboral, habilidades técnicas y certificaciones relevantes.
- **Descripción del Puesto Laboral:** Proveerá una descripción breve del puesto, incluyendo responsabilidades y habilidades técnicas requeridas.

**Pasos a seguir:**
1. Identifica el stack tecnológico que domina el profesional según lo reflejado en las imágenes de su CV.
2. Compara el stack identificado con el stack requerido en la **Descripción del Puesto Laboral**.
3. Evalúa qué tan bien se ajusta el stack del profesional con el del puesto requerido utilizando los siguientes criterios:
    - **Mal:** Si el stack del profesional apenas coincide con el stack requerido.
    - **Regular:** Si el stack del profesional coincide parcialmente con el stack requerido.
    - **Bien:** Si el stack del profesional coincide en la mayoría con el stack requerido.
    - **Muy Bien:** Si el stack del profesional coincide casi por completo con el stack requerido.
    - **Excelente:** Si el stack del profesional coincide completamente con el stack requerido.

**Formato de Respuesta:**
- Proporciona una evaluación clara del ajuste del stack tecnológico en formato diccionario de Python: `{{'nivel': 'Muy Bien', 'justificacion': '...'}}`
- Incluye una breve justificación para tu evaluación, explicando cómo los datos proporcionados en las imágenes del CV y la descripción del puesto cumplen con los criterios de evaluación mencionados.

**Ejemplo de Respuesta:**
{
    'nivel': 'Muy Bien',
    'justificacion': 'El profesional tiene experiencia en la mayoría de las tecnologías requeridas para el puesto, incluyendo React, Node.js y MongoDB. Además, ha trabajado en proyectos similares que implican el uso de Docker y Kubernetes.'
}

No incluyas etiquetas de Python ni nada similar, solo responde con la estructura especificada.
"""

  user_message = f"""Genera la evaluacion para el siguiente Puesto Laboral y las imagenes del CV de la persona:
  **Descripción del Puesto Laboral:**
  {vacante}
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

      respuesta = eval(respuesta)

      dic_nota = {'Mal':1, 'Regular':2, 'Bien':3, 'Muy Bien':4, 'Excelente':5}

      nota_stack = dic_nota[respuesta['nivel']] / 5

      respuesta['nota'] = nota_stack

      return respuesta
    except:
      con -= 1

  return {'nivel': 'Indefinido', 'justificacion': 'Error stack_eval', 'nota':0.5}

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def estudios_eval(image_urls, vacante, api_key):
  client = OpenAI(api_key = api_key)

  MODEL="gpt-4o"

  system_message = """Eres un especialista en evaluación de perfiles académicos. Tu tarea consiste en evaluar qué tan bien se ajusta la formación académica y los cursos de una persona, según lo reflejado en su CV (proporcionado como imágenes), con los requisitos de estudio necesarios para un puesto específico. La evaluación debe calificar el ajuste como Mal, Regular, Bien, Muy Bien o Excelente y proporcionar una justificación.

**Datos que recibirás:**
- **Imágenes del CV del Candidato:** Se te darán las imágenes del CV de la persona, incluyendo educación formal, cursos adicionales y certificaciones relevantes.
- **Descripción del Puesto Laboral:** Proveerá una descripción breve del puesto, incluyendo requisitos de estudio y habilidades necesarias.

**Pasos a seguir:**
1. Excluye cualquier consideración sobre la experiencia profesional o laboral del candidato.
2. Examina únicamente la formación académica y los cursos adicionales del candidato según lo indicado en las imágenes de su CV.
3. Compara la formación y los cursos del candidato con los requisitos de estudio y las habilidades necesarias en la **Descripción del Puesto Laboral**.
4. Evalúa qué tan bien se ajusta la formación y los cursos del candidato con los requisitos de estudio del puesto requerido utilizando los siguientes criterios:
    - **Mal:** Si la formación y los cursos del candidato no son relevantes o apenas coinciden con los requisitos de estudio del puesto.
    - **Regular:** Si la formación y los cursos del candidato son parcialmente relevantes o solo coinciden en parte con los requisitos de estudio del puesto.
    - **Bien:** Si la formación y los cursos del candidato son en su mayoría relevantes y coinciden con los requisitos de estudio del puesto.
    - **Muy Bien:** Si la formación y los cursos del candidato son casi en su totalidad relevantes y coinciden con los requisitos de estudio del puesto.
    - **Excelente:** Si la formación y los cursos del candidato son completamente relevantes y coinciden perfectamente con los requisitos de estudio del puesto.

**Formato de Respuesta:**
- Proporciona una evaluación clara del ajuste de la formación y los cursos en formato diccionario de Python: `{{'nivel': 'Muy Bien', 'justificacion': '...'}}`
- Incluye una breve justificación para tu evaluación, explicando cómo la formación y los cursos del candidato cumplen con los requisitos de estudio mencionados en la descripción del puesto.

**Ejemplo de Respuesta:**
{
    'nivel': 'Muy Bien',
    'justificacion': 'El candidato tiene una sólida formación académica en Ingeniería de Software, que es relevante para el puesto de Desarrollador de Software Senior. Además, ha realizado varios cursos adicionales en tecnologías modernas como Python, JavaScript y DevOps, lo cual coincide perfectamente con los requisitos de estudio del puesto.'
}

No incluyas etiquetas de Python ni nada similar, solo responde con la estructura especificada.
"""


  user_message = f"""Genera la evaluacion para el siguiente Puesto Laboral y las imagenes del CV de la persona:
  **Descripción del Puesto Laboral:**
  {vacante}
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

      respuesta = eval(respuesta)

      dic_nota = {'Mal':1, 'Regular':2, 'Bien':3, 'Muy Bien':4, 'Excelente':5}

      nota_stack = dic_nota[respuesta['nivel']] / 5

      respuesta['nota'] = nota_stack

      return respuesta
    except:
      con -= 1


  return {'nivel': 'Indefinido', 'justificacion': 'Error estudios_eval', 'nota':0.5}

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def cv_format_eval(image_urls, api_key):
  client = OpenAI(api_key = api_key)

  MODEL="gpt-4o"

  system_message = """Eres un experto en diseño y formato de currículums vitae. Tu tarea consiste en evaluar la calidad del formato de un CV basándote en imágenes proporcionadas del mismo. La evaluación debe calificar la calidad del formato como Mal, Regular, Bien, Muy Bien o Excelente y proporcionar una justificación.

**Datos que recibirás:**
- **Imágenes del CV del Candidato:** Se te darán las imágenes del CV de la persona, enfocándote en la legibilidad, el uso del espacio, la jerarquía visual y la consistencia del diseño.

**Pasos a seguir:**
1. Excluye cualquier consideración sobre el contenido específico del CV como la experiencia o habilidades del candidato.
2. Examina únicamente el diseño, la presentación y la legibilidad del CV según lo indicado en las imágenes.
3. Evalúa aspectos como la tipografía, el uso de márgenes, la separación entre secciones, la claridad en la organización de la información y la consistencia en el diseño gráfico.
4. Evalúa qué tan bien está presentado el CV utilizando los siguientes criterios:
    - **Mal:** Si el CV es difícil de leer, está demasiado abarrotado o carece de cualquier forma clara de jerarquía visual.
    - **Regular:** Si el CV tiene algunos elementos de buen diseño pero es inconsistente en su aplicación o tiene algunos problemas de legibilidad.
    - **Bien:** Si el CV es claro y legible, con una buena organización pero mejorable en algunos detalles de diseño.
    - **Muy Bien:** Si el CV muestra un diseño profesional con buena legibilidad y uso efectivo del espacio y la jerarquía visual.
    - **Excelente:** Si el CV es excepcional en todos los aspectos de diseño, presentación y estructuración, haciendo uso óptimo del espacio y ofreciendo una excelente legibilidad y profesionalismo.

**Formato de Respuesta:**
- Proporciona una evaluación clara del formato del CV en formato diccionario de Python: `{{'nivel': 'Muy Bien', 'justificacion': '...'}}`
- Incluye una breve justificación para tu evaluación, explicando cómo los elementos de diseño y la presentación del CV contribuyen a su eficacia general.

**Ejemplo de Respuesta:**
{
    'nivel': 'Muy Bien',
    'justificacion': 'El CV presenta una estructuración impecable con un uso efectivo de la tipografía y los márgenes. La jerarquía visual es clara, facilitando una rápida comprensión de la información más importante, lo que refleja un alto nivel de profesionalismo en la presentación.'
}

No incluyas etiquetas de Python ni nada similar, solo responde con la estructura especificada.
"""



  user_message = f"""Genera la evaluacion para el siguiente Puesto Laboral dado en las imagenes:
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

      respuesta = eval(respuesta)

      dic_nota = {'Mal':1, 'Regular':2, 'Bien':3, 'Muy Bien':4, 'Excelente':5}

      nota_stack = dic_nota[respuesta['nivel']] / 5

      respuesta['nota'] = nota_stack

      return respuesta
    except:
      con -= 1


  return {'nivel': 'Indefinido', 'justificacion': 'Error estudios_eval', 'nota':0.5}

