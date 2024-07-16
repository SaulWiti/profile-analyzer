from openai import OpenAI

import json

import datetime

import re

import random

def json_to_json(text_json, api_key):

  client = OpenAI(api_key = api_key)

  MODEL="gpt-4o"

  system_message = f"""Eres un especialista extrayendo informacion relevante de un json para con ello poder construir un nuevo json resumido.
**Objetivo:**
Se te dara un json que contiene varios datos sobre un persona, tu objetivo es extraer los datos re;evantes que se necesitan los cuales puedes ver en la nueva estructura de json resumido que busca construir a partir del json que tiene toda la informacion

**Materiales Proveídos:**
- **JSON GeneraL:** Este contienen todo tipo de informacion de la persona incluida la informacion que se busca extraer y representar en un nuevo josn.

### Estructura del Json resumido
{{
  "competencias": [
    {{
      "nombre": "Fortalezas",
      "valor": []
    }},
    {{
      "nombre": "Debilidades",
      "valor": []
    }},
    {{
      "nombre": "Hobbies",
      "valor": []
    }},
    {{
      "nombre": "Motivación",
      "valor": ""
    }}
  ],
  "datos": [
    {{
      "id": "name",
      "nombre": "Nombre",
      "valor": ""
    }},
    {{
      "id": "email",
      "nombre": "Correo",
      "valor": ""
    }},
    {{
      "nombre": "Fuente",
      "privado": true,
      "valor": []
    }},
    {{
      "nombre": "Rol",
      "valor": []
    }},
    {{
      "nombre": "Que Rol deseas Desempeñar en 1 a 2 años",
      "privado": true,
      "valor": []
    }},
    {{
      "nombre": "Nivel",
      "valor": []
    }},
    {{
      "nombre": "Modalidad",
      "valor": []
    }},
    {{
      "nombre": "Edad",
      "valor": ""
    }},
    {{
      "nombre": "Años de Experiencia",
      "valor": ""
    }},
    {{
      "id": "linkedIn",
      "nombre": "Linkedin",
      "type": "url",
      "valor": ""
    }}
  ],
  "default": {{
    "footer": [
      {{
        "nombre": "Resumen",
        "valor": ""
      }}
    ]
  }},

  "nombre": "",
  "profileImgUrl": "",
  "skills": [],
  "telefono": null,
  "timestamp": ""
}}
```

### Ejemplo de JSON Relleno

Ejemplo de Datos extraidos del json general(Ejemplo):
- Nombre: Juan Pérez
- Correo: juan.perez@example.com
- Edad: 30
- Años de Experiencia: 8
- Linkedin: https://linkedin.com/in/juanperez
- Fortalezas: Trabajo en equipo, Liderazgo
- Debilidades: Perfeccionismo
- Hobbies: Lectura, Ciclismo
- Motivación: Crecimiento profesional
- Fuente: Referencia interna
- Rol: Desarrollador de Software
- Que Rol deseas Desempeñar en 1 a 2 años: Gerente de Proyectos
- Nivel: Senior
- Modalidad: Remoto
- Resumen: Profesional con más de 8 años de experiencia en desarrollo de software.
- Habilidades: Python, JavaScript, Gestión de proyectos
- Teléfono: 555-1234
- Timestamp: 2024-06-25

Json resumido Relleno:
{{
  "competencias": [
    {{
      "nombre": "Fortalezas",
      "valor": ["Trabajo en equipo", "Liderazgo"]
    }},
    {{
      "nombre": "Debilidades",
      "valor": ["Perfeccionismo"]
    }},
    {{
      "nombre": "Hobbies",
      "valor": ["Lectura", "Ciclismo"]
    }},
    {{
      "nombre": "Motivación",
      "valor": "Crecimiento profesional"
    }}
  ],
  "datos": [
    {{
      "id": "name",
      "nombre": "Nombre",
      "valor": "Juan Pérez"
    }},
    {{
      "id": "email",
      "nombre": "Correo",
      "valor": "juan.perez@example.com"
    }},
    {{
      "nombre": "Fuente",
      "privado": true,
      "valor": ["Referencia interna"]
    }},
    {{
      "nombre": "Rol",
      "valor": ["Desarrollador de Software"]
    }},
    {{
      "nombre": "Que Rol deseas Desempeñar en 1 a 2 años",
      "privado": true,
      "valor": ["Gerente de Proyectos"]
    }},
    {{
      "nombre": "Nivel",
      "valor": ["Senior"]
    }},
    {{
      "nombre": "Modalidad",
      "valor": ["Remoto"]
    }},
    {{
      "nombre": "Edad",
      "valor": "30"
    }},
    {{
      "nombre": "Años de Experiencia",
      "valor": "8"
    }},
    {{
      "id": "linkedIn",
      "nombre": "Linkedin",
      "type": "url",
      "valor": "https://linkedin.com/in/juanperez"
    }}
  ],
  "default": {{
    "footer": [
      {{
        "nombre": "Resumen",
        "valor": "Profesional con más de 8 años de experiencia en desarrollo de software."
      }}
    ]
  }},

  "nombre": "Juan Pérez",
  "profileImgUrl": "",
  "skills": ["Python", "JavaScript", "Gestión de proyectos"],
  "telefono": "555-1234",
  "timestamp": ""
}}

No incluyas etiquetas de Json ni nada similar, solo responde con la estructura especificada y tampoco argumentes ni des niguna explicacion, responde unicamente con la estrutura definida.
"""


  user_message = f"""Genera el json resumido del siguiente json:
{text_json}
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

      respuesta = json.loads(respuesta)
      
      try:
        now_utc = datetime.datetime.now(datetime.timezone.utc)

        iso_format_z = now_utc.isoformat().replace('+00:00', 'Z')

        respuesta['timestamp'] = iso_format_z
      except:
        pass

      try:
        if 'skills' in respuesta:
          respuesta['skills'] = []
        else:
          respuesta['skills'] = []
      except:
        pass


      try:
        if 'telefono' in  respuesta:
          telefono = respuesta['telefono']

          if type(telefono) is str and len(telefono):
            numeros = re.findall(r'\d+', telefono)
            numero_limpio = ''.join(numeros)
            respuesta['telefono'] = int(numero_limpio)

          elif type(telefono) is int:
            pass

          else:
            respuesta['telefono'] = int(''.join([str(random.randint(1,9)) for i in range(0,8)]) + '0000')

            if 'nombre' in respuesta:
              respuesta['nombre'] += '--SIN TELEFONO IDENTIFICADO'
      except:
        pass

      try:
        respuesta["estado"] = "Carga Candidato"
      except:
        pass


      try:
        respuesta['profileImgUrl'] = ''
      except:
        pass


      return respuesta
    except:
      con -= 1

  return None