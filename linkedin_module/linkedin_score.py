from .linkedin_score_utils import procesar_json, seniority_eval, stack_eval, estudios_eval, get_cv_text_linkedin
from concurrent.futures import ThreadPoolExecutor


def linkedin_score(url_perfil, json_vacante, api_key):
    try:
        cv_text = get_cv_text_linkedin(url_perfil, api_key)

        vacante = procesar_json(json_vacante)

        with ThreadPoolExecutor(max_workers=3) as executor:
            # Programar las funciones para que se ejecuten en paralelo
            nota_seniority = executor.submit(seniority_eval, cv_text, vacante, api_key)
            nota_stack = executor.submit(stack_eval, cv_text, vacante, api_key)
            nota_estudio = executor.submit(estudios_eval, cv_text, vacante, api_key)
            
            # Esperar a que las funciones terminen y obtener sus resultados
            nota_seniority = nota_seniority.result()
            nota_stack = nota_stack.result()
            nota_estudio = nota_estudio.result()
    except Exception as e:
        nota_seniority = {'nivel': 'Indefinido', 'justificacion': f'Error linkedin_score: {e}', 'nota':0.0}
        nota_stack = {'nivel': 'Indefinido', 'justificacion': f'Error linkedin_score: {e}', 'nota':0.0}
        nota_estudio = {'nivel': 'Indefinido', 'justificacion': f'Error linkedin_score: {e}', 'nota':0.0}

    nota_promedio = round((nota_seniority['nota'] * 0.4 + nota_stack['nota'] * 0.4 + nota_estudio['nota'] * 0.2), 2)

    nota_promedio = int(round(nota_promedio * 5, 0))

    return {'score': nota_promedio, 'seniority': nota_seniority, 'stack': nota_stack, 'estudio': nota_estudio}