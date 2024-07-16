"""
    Api para actualizar el scroe
    run local: python main.py
    run prod: gunicorn -w 4 -t 230 main:app
    PORT: 8000
"""
import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from flask_cors import CORS

from cv_module.cv_score import cv_score
from test_module.test_score import test_score
from linkedin_module.linkedin_score import linkedin_score
from data_module.get_data import get_data
from json_module.get_json import get_json
from data_user_module.get_data_user import get_data_user

load_dotenv()

app = Flask(__name__)
CORS(app)

API_KEY_AUTH = os.getenv('API_KEY_AUTH')

if API_KEY_AUTH is None:
    raise ValueError("API_KEY_AUTH not configured in .env file")


def get_api_key():
    """ definition of api key"""
    api_key_auth = request.headers.get('api_key_auth')
    if api_key_auth != API_KEY_AUTH:
        return False
    return True




# EndPoint Linkedin
@app.route("/analizar_linkedin", methods=["POST"])
def analizar_linkedin():
    """ definition of endpoint linkedin"""
    if not get_api_key():
        return jsonify({"detail": "Unauthorized"}), 403

    try:
        data = request.get_json()
        json_data = data['json_data']
        url_perfil = data['url_perfil']

        resultado = linkedin_score(
            url_perfil, json_data, api_key=os.getenv('API_KEY_MODEL'))

        return jsonify({"resultado": resultado}), 200
    except Exception as e:
        return jsonify({"detail": str(e)}), 500




# EndPoint CV
@app.route("/analizar_cv", methods=["POST"])
def analizar_cv():
    """ definition of endpoint cv"""
    if not get_api_key():
        return jsonify({"detail": "Unauthorized"}), 403

    try:
        data = request.get_json()
        json_data = data['json_data']
        pdf_url = data['pdf_url']

        resultado = cv_score(pdf_url, json_data,
                             api_key=os.getenv('API_KEY_MODEL'))

        return jsonify({"resultado": resultado}), 200
    except Exception as e:
        return jsonify({"detail": str(e)}), 500




# EndPoint Test Gorila

@app.route("/analizar_test", methods=["POST"])
def analizar_test():
    """ definition of endpoint test"""
    if not get_api_key():
        return jsonify({"detail": "Unauthorized"}), 403

    try:
        data = request.get_json()
        pdf_url = data['pdf_url']

        resultado = test_score(pdf_url, api_key=os.getenv('API_KEY_MODEL'))

        return jsonify({"resultado": resultado}), 200

    except Exception as e:
        return jsonify({"detail": str(e)}), 500
    



    
# EndPoint Extraer Datos
# analizar_data
@app.route("/extract-data-pdf", methods=["POST"])
def analizar_data():
    if not get_api_key():
        return jsonify({"detail": "Unauthorized"}), 403
    
    try:
        data = request.get_json()
        pdf_url = data['pdf_url']

        resultado = get_data(pdf_url, api_key=os.getenv('API_KEY_MODEL'))

        return jsonify({"resultado": resultado}), 200
    except Exception as e:
        return jsonify({"detail": str(e)}), 500
    




# EndPoint Extraer Datos para Gustavo                       Aqui Gustavo
# analizar_data
@app.route("/cv/information/extract", methods=["POST"])
def analizar_data_user():
    if not get_api_key():
        return jsonify({"detail": "Unauthorized"}), 403
    
    try:
        data = request.get_json()
        pdf_url = data['pdf_url']

        resultado = get_data_user(pdf_url, api_key=os.getenv('API_KEY_MODEL'))

        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({"detail": str(e)}), 500



    
# extraer datos del json
@app.route("/extract-data-json", methods=["POST"])
def analizar_json():
    if not get_api_key():
        return jsonify({"detail": "Unauthorized"}), 403
    
    try:
        data = request.get_json()
        json_entrada = data['json_entrada']

        resultado = get_json(json_entrada, api_key=os.getenv('API_KEY_MODEL'))

        return jsonify({"resultado": resultado}), 200
    except Exception as e:
        return jsonify({"detail": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
