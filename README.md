# API Flask - FastApi

Esta API proporciona los endpoints para analizar datos de LinkedIn, CVs y pruebas de Gorila. Está desarrollada en Flask y utiliza modelos externos para procesar los datos.

## Estructura del Proyecto

```
├── cv_module/  
│   └──  cv_score_utils.py  
│   └──  cv_score.py  
|  
├── test_module/  
│   └──  test_score_utils.py  
│   └──  test_score.py  
|  
├── linkedin_module/  
│   └──  linkedin_score_utils.py  
│   └──  linkedin_score.py  
| 
├── data_module/
│   └──  get_data_utils.py
│   └──  get_data.py  
|
├── data_user_module/
│   └──  get_data_user_utils.py
│   └──  get_data_user.py
|
├── json_module/
│   └──  get_json_utils.py
│   └──  get_json.py    
| 
├── main.py  
|  
├── main_fast_api.py
|
├── .env  
|
├── requirements.txt 
|  
└── README.md  

```

## Variables de Entorno

Tener un archivo `.env` en el directorio raíz de tu proyecto con el siguiente contenido:

```
API_KEY_AUTH = "level1234"
API_KEY_MODEL = api_key_OpenAi
```

## Pre-Requisitos

- Python 3.10.5

- Asegurarse de tener instalado Chrome para el caso del endpoint de Linkedin

## Endpoints

### 1. Analizar LinkedIn: linkedin_module

**URL**: `/analizar_linkedin`

**Método**: `POST`

**Puerto**: 8000

**Headers**:
- `Content-Type: application/json`
- `api-key-auth: level1234`

**Body**:
```json
{
  "json_data": { "key1": "value1" },
  "url_perfil": "https://linkedin.com/in/perfil"
}
```

**Comando CURL**:
```sh
curl -X POST http://127.0.0.1:8000/analizar_linkedin \
    -H "Content-Type: application/json" \
    -H "api-key-auth: level1234" \
    -d '{
          "json_data": { "key1": "value1" },
          "url_perfil": "https://linkedin.com/in/perfil"
        }'
```

**Ejemplo de uso**
```sh
curl -X POST http://127.0.0.1:8000/analizar_linkedin \
    -H "Content-Type: application/json" \
    -H "api-key-auth: level1234" \
    -d '{
          "json_data": {
  "json_data": {
    "id": 1717300579247,
    "salario": [
        {
            "min": "1.800.000",
            "max": "2.600.000",
            "moneda": "CLP"
        }
    ],
    "fechaFin": "",
    "plazo": "9",
    "prioridad": "Nuevo colaborador",
    "fechaInicio": "2024-05-29T03:56:19.000Z",
    "rol": [
        "Full Stack"
    ],
    "estado": "Abierto",
    "descripcion": "<p><strong>Misión del cargo</strong></p><ul><li><br></li></ul><p><strong>Principales funciones</strong></p><ul><li><br></li></ul><p><strong>Logros esperados</strong></p><ul><li><br></li></ul><p><strong>Stack o herramientas</strong></p><ul><li><br></li></ul><p><strong>Habilidades blandas</strong></p><ul><li><br></li></ul>",
    "nivel": "Senior",
    "stack": [
        "JavaScript",
        "TypeScript",
        "React",
        "Node.js",
        "AWS"
    ],
    "fechaEstimadaFin": "2024-06-07T03:56:19.000Z",
    "empresa": "Cencosud",
    "responsable": "Pedro Stankovsky",
    "equipo": "IT ",
    "modalidad": "Mixta",
    "postulantes": [],
    "solicitante": "Pedro Stankovsky",
    "reclutadores": [],
    "managerEmail": "",
    "managerPhone": "",
    "responsibleEmail": "",
    "responsiblePhone": ""
},
  "url_perfil": "https://www.linkedin.com/in/sa%C3%BAl-d%C3%ADaz-matos-7190971bb"
}'
```

**Salida**

```json
{
    "resultado": {
        "score": 0.9,
        "seniority": {
            "nota": 1.0,
            "nivel": "Especialista",
            "justificacion": "..."
        },
        "stack": {
            "nota": 0.8
            "nivel": "Muy Bien",
            "justificacion": "..."
        },
        "estudio": {
            "nota": 0.8
            "nivel": "Muy Bien",
            "justificacion": "..."
        }
    }
}
```

- El score representa la calificación general del Linkedin del candidato respecto a la vacante.
- La sección seniority detalla la evaluación de la experiencia laboral del candidato y su correspondencia con el nivel de seniority requerido.
- La sección stack evalúa la adecuación del stack tecnológico del candidato con el requerido para la vacante.
- La sección estudio evalúa el nivel de estudios y formación académica del candidato.


### 2. Analizar CV: cv_module

**URL**: `/analizar_cv`

**Método**: `POST`

**Puerto**: 8000

**Headers**:
- `Content-Type: application/json`
- `api-key-auth: level1234`

**Body**:
```json
{
  "json_data": { "key1": "value1" },
  "pdf_url": "https://example.com/cv.pdf"
}
```

**Comando CURL**:
```sh
curl -X POST http://127.0.0.1:8000/analizar_cv \
    -H "Content-Type: application/json" \
    -H "api-key-auth: level1234" \
    -d '{
          "json_data": { "key1": "value1" },
          "pdf_url": "https://example.com/cv.pdf"
        }'
```

**Ejemplo de uso**:
```sh
curl -X POST http://0.0.0.0:8000/analizar_cv \
-H "Content-Type: application/json" \
-H "api-key-auth: level1234" \
-d '{
  "json_data": {
    "id": 1717300579247,
    "salario": [
        {
            "min": "1.800.000",
            "max": "2.600.000",
            "moneda": "CLP"
        }
    ],
    "fechaFin": "",
    "plazo": "9",
    "prioridad": "Nuevo colaborador",
    "fechaInicio": "2024-05-29T03:56:19.000Z",
    "rol": [
        "Full Stack"
    ],
    "estado": "Abierto",
    "descripcion": "<p><strong>Misión del cargo</strong></p><ul><li><br></li></ul><p><strong>Principales funciones</strong></p><ul><li><br></li></ul><p><strong>Logros esperados</strong></p><ul><li><br></li></ul><p><strong>Stack o herramientas</strong></p><ul><li><br></li></ul><p><strong>Habilidades blandas</strong></p><ul><li><br></li></ul>",
    "nivel": "Senior",
    "stack": [
        "JavaScript",
        "TypeScript",
        "React",
        "Node.js",
        "AWS"
    ],
    "fechaEstimadaFin": "2024-06-07T03:56:19.000Z",
    "empresa": "Cencosud",
    "responsable": "Pedro Stankovsky",
    "equipo": "IT ",
    "modalidad": "Mixta",
    "postulantes": [],
    "solicitante": "Pedro Stankovsky",
    "reclutadores": [],
    "managerEmail": "",
    "managerPhone": "",
    "responsibleEmail": "",
    "responsiblePhone": ""
},
  "pdf_url": "https://hunterapp-back-sa.s3.sa-east-1.amazonaws.com/cv56931299991.pdf"
}'
```


**Salida:**

```json
{
    "resultado": {
        "score": 0.9,
        "seniority": {
            "nota": 1.0,
            "nivel": "Especialista",
            "justificacion": "..."
        },
        "stack": {
            "nota": 0.8
            "nivel": "Muy Bien",
            "justificacion": "..."
        },
        "estudio": {
            "nota": 0.8
            "nivel": "Muy Bien",
            "justificacion": "..."
        },
        "cv": {
            "nota": 1.0
            "nivel": "Excelente",
            "justificacion": "..."
        }
    }
}
```

- El score representa la calificación general del CV del candidato.
- La sección seniority detalla la evaluación de la experiencia laboral del candidato y su correspondencia con el nivel de seniority requerido.
- La sección stack evalúa la adecuación del stack tecnológico del candidato con el requerido para la vacante.
- La sección estudio evalúa el nivel de estudios y formación académica del candidato.
- La sección cv evalúa la presentación y estructura del CV del candidato.

### 3. Analizar Test: test_module

**URL**: `/analizar_test`

**Método**: `POST`

**Puerto**: 8000

**Headers**:
- `Content-Type: application/json`
- `api-key-auth: level1234`

**Body**:
```json
{
  "pdf_url": "https://example.com/test.pdf"
}
```

**Comando CURL**:
```sh
curl -X POST http://127.0.0.1:8000/analizar_test \
    -H "Content-Type: application/json" \
    -H "api-key-auth: level1234" \
    -d '{
          "pdf_url": "https://example.com/test.pdf"
        }'
```

**Ejemplo de uso**:

```sh
curl -X POST http://127.0.0.1:8000/analizar_test \
    -H "Content-Type: application/json" \
    -H "api-key-auth: level1234" \
    -d '{"pdf_url": "https://hunterapp-back-sa.s3.sa-east-1.amazonaws.com/Test%20Kandio56979962612.pdf"}'
```

**Salida:**
```json
{
    "resultado": {
        "evaluaciones": {
            "AWS": 62,
            "Node.js": 66,
            "Pensamiento crítico": 41,
            "Razonamiento espacial": 87,
            "React": 33
        },
        "justificacion": "El candidato obtuvo un puntaje promedio del 58%, lo que refleja un desempeño variado en las diferentes áreas evaluadas. Destacó en Razonamiento espacial con un 87%, demostrando una fuerte capacidad para analizar objetos tridimensionales y espaciales, lo cual es crucial para roles que requieren habilidades analíticas. También tuvo un buen desempeño en Node.js con un 66%, indicando un conocimiento sólido en el desarrollo y buenas prácticas con esta tecnología. Sin embargo, el candidato mostró áreas de mejora en React con un 33% y Pensamiento crítico con un 41%, lo que sugiere que podría beneficiarse de una mayor formación en estas áreas. En AWS, obtuvo un 62%, lo que indica una competencia razonable en la administración de recursos en la nube. Cabe destacar que en algunas evaluaciones, como en React, el candidato dejó preguntas sin responder, lo cual podría haber afectado su puntaje final.",
        "puntaje_promedio": 58,
        "score": 0.58
    }
}
```

- El score es una calificación global ajustada del desempeño del candidato y el que se debe tener en cuenta coomo resultado final.
- La justificacion proporciona un análisis cualitativo del desempeño del candidato basado en los resultados obtenidos.
- El puntaje_promedio representa la calificación general del candidato en todas las áreas evaluadas extraida del PDF.
- La sección evaluaciones detalla la evaluación de cada área de competencia.

### 4. Extraer Datos pdf version Yamil: data_module

**URL**: `/extract-data-pdf`

**Método**: `POST`

**Puerto**: 8000

**Headers**:
- `Content-Type: application/json`
- `api-key-auth: level1234`

**Body**:
```json
{
  "pdf_url": "https://example.com/test.pdf"
}
```

**Comando CURL**:
```sh
curl -X POST http://127.0.0.1:8000/extract-data-pdf \
    -H "Content-Type: application/json" \
    -H "api-key-auth: level1234" \
    -d '{
          "pdf_url": "https://example.com/cv.pdf"
        }'
```

**Salida**
```json
{
    "resultado": {
        "competencias": [
            {
                "nombre": "Fortalezas",
                "valor": [
                    "Cooperatividad",
                    "Flexibilidad",
                    "Automotivación",
                    "Responsabilidad",
                    "Planeación",
                    "Creatividad"
                ]
            },
            {
                "nombre": "Debilidades",
                "valor": []
            },
            {
                "nombre": "Hobbies",
                "valor": []
            },
            {
                "nombre": "Motivación",
                "valor": ""
            }
        ],
        "datos": [
            {
                "id": "name",
                "nombre": "Nombre",
                "valor": "Abdel Mejia"
            },
            {
                "id": "email",
                "nombre": "Correo",
                "valor": "bhalut.bear@gmail.com"
            },
            {
                "nombre": "Fuente",
                "privado": true,
                "valor": []
            },
            {
                "nombre": "Rol",
                "valor": [
                    "Desarrollador de Software"
                ]
            },
            {
                "nombre": "Que Rol deseas Desempeñar en 1 a 2 años",
                "privado": true,
                "valor": []
            },
            {
                "nombre": "Nivel",
                "valor": []
            },
            {
                "nombre": "Modalidad",
                "valor": []
            },
            {
                "nombre": "Edad",
                "valor": ""
            },
            {
                "nombre": "Años de Experiencia",
                "valor": ""
            },
            {
                "id": "linkedIn",
                "nombre": "Linkedin",
                "type": "url",
                "valor": "linkedin.com/in/bhalut"
            }
        ],
        "default": {
            "footer": [
                {
                    "nombre": "Resumen",
                    "valor": "Soy un autodidacta apasionado por la tecnología, ciencia ficción y videojuegos. Con una sólida trayectoria en el desarrollo de software, me especializo en crear soluciones que van desde simuladores educativos hasta plataformas educativas de vanguardia. Mi experiencia incluye roles clave en desarrollo y dirección técnica, donde he liderado optimizaciones significativas en AWS, integrado inteligencia artificial con modelos de OpenAI y potenciado equipos para desarrollar soluciones innovadoras y eficientes."
                }
            ]
        },
        "nombre": "Abdel Mejia",
        "profileImgUrl": "",
        "skills": [
            "Javascript",
            "Typescript",
            "NodeJS",
            "React",
            "Webpack",
            "Git",
            "Docker",
            "Linux",
            "Bash",
            "MySQL",
            "PostgreSQL",
            "Python",
            "Django",
            "AWS"
        ],
        "telefono": "+57 320 460 1864",
        "timestamp": "2024-06-27T05:48:37.233093Z"
    }
}
```
- La salida es un JSON con la estructura previamente definida, que incluye los datos extraídos del CV. En caso de que ocurra algún fallo, la salida será nula.


### 5. Extraer datos del json: json_module

**URL**: `/extract-data-json`

**Método**: `POST`

**Puerto**: 8000

**Headers**:
- `Content-Type: application/json`
- `api-key-auth: level1234`

**Body**:
```json
{"json_entrada": {}
}
```

**Comando CURL**:
```sh
curl -X POST http://127.0.0.1:8000/extract-data-json \
    -H "Content-Type: application/json" \
    -H "api-key-auth: level1234" \
    -d '{
          "json_entrada": {}
        }'
```

**Salida**
- Mismma salida que en el del CV


### 6. Extraer Datos CV version Gustavo: data_user_module

**URL**: `/cv/information/extract`

**Método**: `POST`

**Puerto**: 8000

**Headers**:
- `Content-Type: application/json`
- `api-key-auth: level1234`

**Body**:
```json
{
  "pdf_url": "https://example.com/test.pdf"
}
```

**Comando CURL**:
```sh
curl -X POST http://127.0.0.1:8000/cv/information/extract \
    -H "Content-Type: application/json" \
    -H "api-key-auth: level1234" \
    -d '{
          "pdf_url": "https://example.com/cv.pdf"
        }'
```

**Ejemplo de uso**:

```sh
curl -X POST http://127.0.0.1:8000/analizar_test \
    -H "Content-Type: application/json" \
    -H "api-key-auth: level1234" \
    -d '{"pdf_url": "https://hunterapp-back-sa.s3.sa-east-1.amazonaws.com/CV51910534820.pdf"}'
```

**Salida**


