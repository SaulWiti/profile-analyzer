from .get_data_utils import pdf_to_image_message, cv_get_data

def get_data(pdf_url, api_key):
  try:
    image_urls = pdf_to_image_message(pdf_url)

    respuesta = cv_get_data(image_urls, api_key)

    return respuesta
  except:
    return None