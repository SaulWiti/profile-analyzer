from .cv_score_utils import pdf_to_image_message, procesar_json, seniority_eval, stack_eval, estudios_eval, cv_format_eval
from concurrent.futures import ThreadPoolExecutor

def cv_score(pdf_url, json_vacante, api_key):

  try:
    image_urls = pdf_to_image_message(pdf_url)
  
    vacante = procesar_json(json_vacante)

    with ThreadPoolExecutor(max_workers=4) as executor:
        # Programar las funciones para que se ejecuten en paralelo
        nota_seniority = executor.submit(seniority_eval, image_urls, vacante, api_key)
        nota_stack = executor.submit(stack_eval, image_urls, vacante, api_key)
        nota_estudio = executor.submit(estudios_eval, image_urls, vacante, api_key)
        nota_cv = executor.submit(cv_format_eval, image_urls, api_key)

        # Esperar a que las funciones terminen y obtener sus resultados
        nota_seniority = nota_seniority.result()
        nota_stack = nota_stack.result()
        nota_estudio = nota_estudio.result()
        nota_cv = nota_cv.result()
  except Exception as e:
    nota_seniority = {'nivel': 'Indefinido', 'justificacion': f'Error cv_score: {e}', 'nota':0.0}
    nota_stack = {'nivel': 'Indefinido', 'justificacion': f'Error cv_score: {e}', 'nota':0.0}
    nota_estudio = {'nivel': 'Indefinido', 'justificacion': f'Error cv_score: {e}', 'nota':0.0}
    nota_cv = {'nivel': 'Indefinido', 'justificacion': f'Error cv_score: {e}', 'nota':0.0}
  
  nota_promedio = round((nota_seniority['nota'] * 0.4 + nota_stack['nota'] * 0.35 + nota_estudio['nota'] * 0.15 + nota_cv['nota'] * 0.1), 2)

  nota_promedio = int(round(nota_promedio * 5, 0))

  return {'score': nota_promedio, 'seniority': nota_seniority, 'stack': nota_stack, 'estudio': nota_estudio, 'cv': nota_cv}