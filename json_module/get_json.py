from .get_json_utils import json_to_json

def get_json(json_general, api_key):
    try:
        json_respuesta = json_to_json(json_general, api_key)
        return json_respuesta
    except:
        return None
