from .get_data_user_utils import pdf_to_image_message, cv_get_data, proces_info

def get_data_user(pdf_url:str, api_key:str) -> dict:

  try:
    image_urls = pdf_to_image_message(pdf_url)

    info_dict = cv_get_data(image_urls, api_key)

    dict_resp = proces_info(info_dict)

    return dict_resp

  except Exception as e:
    
    return {
          'nombre': '',
          'telefono': '',
          'datos':[{'nombre':'Correo', 'valor':''}, {'nombre': 'Linkedin','valor': ''}],
          'workflow':[{ 'nombre': 'Carga Candidato','feedback': f'Error al extraer los datos del candidato: {e}'}]
          }