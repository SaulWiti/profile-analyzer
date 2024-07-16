from .test_score_utils import pdf_to_image_message, puntaje_eval

def test_score(pdf_url, api_key):

  try:
    image_urls = pdf_to_image_message(pdf_url)

    respuesta = puntaje_eval(image_urls, api_key)
  except Exception as e:
    respuesta = {'puntaje_promedio': 50, 'evaluaciones': {}, 'justificacion': f'Error test_score: {e}', 'score': 0.5}
    
  return respuesta