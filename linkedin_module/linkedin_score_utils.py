from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

import time

import random

import re

from datetime import datetime, date

from openai import OpenAI

from bs4 import BeautifulSoup, NavigableString, Tag


def is_perfil(texto_html, api_key):

  client = OpenAI(api_key = api_key)

  MODEL="gpt-4o"

  system_message = f"""**Tarea: Identificación de Tipo de Página de LinkedIn**

**Objetivo:**
Determinar si el texto extraído de un HTML de LinkedIn corresponde al perfil de una persona o a una página de login, registro u otra que no sea un perfil personal.

**Materiales Proveídos:**
- **Texto HTML Extraído:** Contenido textual del HTML de LinkedIn que puede incluir perfiles personales, páginas de login, registro u otras páginas.

**Instrucciones Detalladas:**

1. **Análisis del Texto HTML:**
   - Examina el texto HTML proporcionado para identificar elementos típicos de un perfil personal de LinkedIn (e.g., nombre, experiencia laboral, educación, habilidades, recomendaciones).

2. **Identificación del Tipo de Página:**
   - Si el texto contiene información característica de un perfil personal (nombre, título profesional, resumen, experiencia laboral, etc.), clasifícalo como un perfil de persona.
   - Si el texto contiene elementos típicos de páginas de login, registro u otros (formularios de autenticación, botones de registro, términos de servicio, etc.), clasifícalo como no perfil de persona.

3. **Formato de Respuesta:**
   - La respuesta debe ser un valor booleano: **True** si el texto corresponde a un perfil personal y **False** si corresponde a una página de login, registro u otra que no sea un perfil personal.

**Ejemplo de Estructura de Salida:**
True

No incluyas etiquetas de Python ni nada similar, solo responde con la estructura especificada.
"""


  user_message = f"""Genera la respuesta para el siguiente texto extraido del html:  
{texto_html}
"""

  response = client.chat.completions.create(
      model=MODEL,
      messages=[
          {"role": "system", "content": system_message},
          {"role": "user", "content":  user_message}
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

  return False


def extraer_texto_etiquetas(html_string):

    etiquetas_texto = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'span', 'a']

    soup = BeautifulSoup(html_string, 'lxml')

    def obtener_texto(etiqueta):
        texto = ''
        for elemento in etiqueta.descendants:
            if isinstance(elemento, NavigableString):
                texto += str(elemento)
            elif isinstance(elemento, Tag) and elemento.name in etiquetas_texto:
                texto += obtener_texto(elemento)
        return texto

    texto = ''
    for etiqueta in soup.find_all(etiquetas_texto):
        texto += obtener_texto(etiqueta) + ' '

    texto = texto.strip()

    texto = re.sub(r'\s+', ' ', texto)
    
    return texto


def get_html_text(url_perfil, api_key):
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Activa el modo headless no ver navegador
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-notifications")

    con = 5
    while con:
        con -= 1

        driver = webdriver.Chrome(options=chrome_options)

        # Navegar a Google
        driver.get('https://www.google.com')

        time.sleep(random.randint(5,10))

        # Realizar una búsqueda en Google
        search_box = driver.find_element(By.NAME, 'q')
        search_box.send_keys(url_perfil)
        search_box.send_keys(Keys.ENTER)

        time.sleep(random.randint(5,10))

        try:
            # Hacer clic en el primer resultado de búsqueda
            first_result = driver.find_element(By.CSS_SELECTOR, 'div.g a')
            first_result.click()
        except:
            continue

        time.sleep(random.randint(5,10))

        html_general_content = driver.page_source

        texto_html = extraer_texto_etiquetas(html_general_content)

        if is_perfil(texto_html, api_key):
            driver.quit()
            return texto_html

        driver.quit()

    return texto_html


def model_get_cv(text_link, api_key):
  
  client = OpenAI(api_key = api_key)

  system_message = """Dado un texto extraído de un perfil de LinkedIn, organiza y presenta la información en el formato de un currículum vítae (CV) estructurado. Asegúrate de incluir las siguientes secciones si la información está disponible: Información de contacto, Perfil, Experiencia, Educación, Licencias y Certificaciones, Conocimientos y Aptitudes, Recomendaciones, Publicaciones, Cursos, Reconocimientos y Premios, Idiomas.
"""


  user_message = f"""Realiza el análisis el siguiente texto:  
1. **Texto Linkedin**  
- {text_link}   
"""

  response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ],
        temperature=0.0,
        max_tokens=4096,
        top_p = 1,
        seed = 250
      )

  respuesta = response.choices[0].message.content

  return respuesta


def get_cv_text_linkedin(url_perfil, api_key):
    
    try:
        texto_html = get_html_text(url_perfil, api_key)

        cv_text = model_get_cv(texto_html, api_key)

        return cv_text
    except:
        return None  


# ------------------------------------------------------------------------------------------------------------------------------------------------------

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

def puestos_relevantes(cv_text, vacante, api_key):

  client = OpenAI(api_key = api_key)

  MODEL="gpt-4o"

  hoy = date.today()
  hoy = hoy.strftime("%m/%Y")

  system_message = f"""**Tarea: Extracción de Fechas de Vacantes Relevantes de un CV extraido de linkedin**

**Objetivo:**
Extraer de un CV las fechas de inicio y fin de las posiciones laborales que sean relevantes para un puesto específico y proporcionar una justificación de por qué se seleccionaron estas vacantes.

**Materiales Proveídos:**
- **Texto del CV-linkedin:** Incluyen toda la infromacion profesional existente en el perfil de linkedin de la persona, experiencia laboral, educación, habilidades técnicas y certificaciones. Debes enfocarte únicamente en la experiencia laboral.
- **Descripción del Puesto Laboral:** Texto breve que detalla el título y el stack de habilidades requerido para el puesto.


**Instrucciones Detalladas:**

1. **Revisión del CV-linkedin:**
   - Examina el CV-linkedin para identificar todas las posiciones laborales listadas, registrando las fechas de inicio y fin de cada una.

2. **Identificación de Experiencias Relevantes:**
   - Selecciona solo aquellas posiciones que estén directamente relacionadas con el puesto laboral, las habilidades, el stack y requisitos del puesto que estás evaluando dado en **Descripción del Puesto Laboral**.

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


  user_message = f"""Genera la evaluación para el siguiente Puesto Laboral y el CV-Linekdin de la persona:
**Descripción del Puesto Laboral:**
{vacante}

**Texto CV-Linkedin**:
{cv_text}
"""

  response = client.chat.completions.create(
      model=MODEL,
      messages=[
          {"role": "system", "content": system_message},
          {"role": "user", "content": user_message}
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


def seniority_eval(cv_text, vacante, api_key):

  try:

    dic_puestos_relevantes = puestos_relevantes(cv_text, vacante, api_key)

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

def stack_eval(cv_text, vacante, api_key):
  client = OpenAI(api_key = api_key)

  MODEL="gpt-4o"

  system_message = """Eres un especialista en evaluación de stacks tecnológicos. Tu tarea consiste en evaluar qué tan bien se ajusta el stack tecnológico que domina el profesional, según lo reflejado en su CV (proporcionado como imágenes), con el stack requerido para un puesto específico. La evaluación debe calificar el ajuste como Mal, Regular, Bien, Muy Bien o Excelente y proporcionar una justificación.

**Datos que recibirás:**
- **Texto del CV-linkedin:** Incluyen toda la infromacion profesional existente en el perfil de linkedin de la persona, experiencia laboral, educación, habilidades técnicas y certificaciones. Debes enfocarte únicamente en la experiencia laboral.
- **Descripción del Puesto Laboral:** Proveerá una descripción breve del puesto, incluyendo responsabilidades y habilidades técnicas requeridas.

**Pasos a seguir:**
1. Identifica el stack tecnológico que domina el profesional según lo reflejado en el texto del CV-linkedin.
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

  user_message = f"""Genera la evaluación para el siguiente Puesto Laboral y el CV-Linekdin de la persona:
**Descripción del Puesto Laboral:**
{vacante}

**Texto CV-Linkedin**:
{cv_text}
"""

  response = client.chat.completions.create(
      model=MODEL,
      messages=[
          {"role": "system", "content": system_message},
          {"role": "user", "content": user_message}
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

def estudios_eval(cv_text, vacante, api_key):
  client = OpenAI(api_key = api_key)

  MODEL="gpt-4o"

  system_message = """Eres un especialista en evaluación de perfiles académicos. Tu tarea consiste en evaluar qué tan bien se ajusta la formación académica y los cursos de una persona, según lo reflejado en su CV-linkedin, con los requisitos de estudio necesarios para un puesto específico. La evaluación debe calificar el ajuste como Mal, Regular, Bien, Muy Bien o Excelente y proporcionar una justificación.

**Datos que recibirás:**
- **Texto del CV-linkedin:** Incluyen toda la infromacion profesional existente en el perfil de linkedin de la persona, experiencia laboral, educación, habilidades técnicas y certificaciones. Debes enfocarte únicamente en la experiencia laboral.
- **Descripción del Puesto Laboral:** Proveerá una descripción breve del puesto, incluyendo requisitos de estudio y habilidades necesarias.

**Pasos a seguir:**
1. Examina únicamente la formación académica y los cursos adicionales del candidato según lo indicado en las imágenes de su CV-linkedin.
2. Compara la formación y los cursos del candidato con los requisitos de estudio y las habilidades necesarias en la **Descripción del Puesto Laboral**.
3. Evalúa qué tan bien se ajusta la formación y los cursos del candidato con los requisitos de estudio del puesto requerido utilizando los siguientes criterios:
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


  user_message = f"""Genera la evaluación para el siguiente Puesto Laboral y el CV-Linekdin de la persona:
**Descripción del Puesto Laboral:**
{vacante}

**Texto CV-Linkedin**:
{cv_text}
"""

  response = client.chat.completions.create(
      model=MODEL,
      messages=[
          {"role": "system", "content": system_message},
          {"role": "user", "content":  user_message}
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