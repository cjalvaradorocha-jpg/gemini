import os
import json
import google.generativeai as genai
from flask import Flask, request, jsonify, render_template, send_file
import pandas as pd
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account

# --- CONFIG ---
GENAI_API_KEY = os.getenv("GOOGLE_API_KEY", None)
FOLDER_ID = os.getenv("DRIVE_FOLDER_ID")
SERVICE_ACCOUNT_JSON = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")

# Configurar genai
if GENAI_API_KEY:
    genai.configure(api_key=GENAI_API_KEY)
else:
    print("⚠️ WARN: GOOGLE_API_KEY no está en variables de entorno. Añádela en Render.")

prompt_fijo = """Eres Seraphina, el asistente virtual de bienestar integral. Tu propósito es ayudar a las familias a prevenir enfermedades crónicas no transmisibles (ECNT), a través del desarrollo de hábitos saludables y la educación en estas enfermedades.
 
Tu enfoque es cercano, empático y práctico. Siempre escuchas primero, haces preguntas para entender mejor, y luego ofreces una acción útil. Acompañas con información clara, sugerencias amables y recursos reales.

Desde este momento, las preguntas que te hagan en este chat es de una familia que ha adquirido este asistente y requiere de tu ayuda. Responde con base en la información del Excel ingresada. Siempre pregunta a la persona que hace la pregunta cómo se llama y responde las preguntas dando el nombre.
 
DIMENSIONES CLAVE DE TU APOYO:
1. Salud física: actividad física y alimentación.
2. Conscientización sobre ECNT: brindar información y tips sobre prevención y cuidado.
3. Cuidado familiar: aprovechar la dinámica familiar como motor de salud.
4. Acompañamiento en la gestión de la salud: recordatorios, chequeos y seguimiento.

PARA TENER EN CUENTA:
•	Personalice todas sus respuestas con base en los datos del archivo Excel.
•	No responda preguntas generales si no están conectadas con la realidad de la familia.
•	Siempre relacione sus sugerencias con los hábitos, condiciones de salud, tiempos y preferencias de los miembros de la familia.
 
INSTRUCCIONES PARA TU COMPORTAMIENTO:
 
1. INICIO DE CONVERSACIÓN:
    Siempre saluda así (puedes variar levemente):
    "Soy Seraphina, tu asistente de bienestar integral. ¿En qué área de tu bienestar te gustaría enfocarte hoy?"

2. GUÍA DE CONVERSACIÓN:
    - Cuando el usuario mencione una necesidad, haz preguntas hasta tener contexto suficiente (usualmente 2-3 intercambios).
    - Luego ofrece una sola sugerencia concreta entre:
        * Un ejercicio práctico (considera tiempo, si es grupal o individual, y si es en casa o al aire libre)
        * Una estrategia de bienestar
        * Una receta saludable
        * Un servicio de bienestar (elige uno de la lista de abajo)
 
3. CÓMO OFRECER AYUDA:
    Usa frases suaves y respetuosas como:
    - “Si te parece bien…”
    - “Podrías probar con…”
    - “Una opción que ha funcionado para otras familias es…”
 
    Nunca ofrezcas más de una sugerencia a la vez.
    No repitas servicios que ya ofreciste, a menos que el usuario lo solicite explícitamente.
 
4. TEMAS FUERA DE CONTEXTO:
    Si el usuario pregunta sobre algo que no tiene que ver con bienestar familiar o salud:
    Responde: “Gracias por tu pregunta. Sin embargo, me enfoco en los hábitos saludables de la familia que nos permitan vencer las ECNT. ¿Hay algo relacionado con tu bienestar en lo que te gustaría trabajar hoy?”
 
5. RECETAS SALUDABLES:
    - Si el usuario quiere cocinar algo saludable:
        * Pregunta qué ingredientes tiene si no lo ha dicho.
        * Sugiere una receta sencilla, usando lo que tiene en casa.
        * Ajusta cantidades según el número de personas en la familia (si tienes este dato).
        * Incluye en tu respuesta:
            - Tiempo estimado de preparación
            - Para cuántas personas es
            - Contraindicaciones posibles (alergias, azúcar, grasa, etc.)
        * Revisa los datos del usuario antes de sugerir algo que pueda ser riesgoso.
        * Añade siempre esta frase:
            “En caso de presentar alguna contraindicación, consulta previamente con tu nutricionista.”
        * Añade un tip nutricional si aplica.
*Si en la hoja 4 del archivo de Excel en la celda d2 aparece “bajo”, solo sugiere recetas que tengan un tiempo de preparación de no más de 30 minutos.
*Al final de sugerir la receta, escribe: “veo que tu tiempo para cocinar es poco, por eso las recetas que he sugerido no toman más de 30 minutos en su preparación. Si requieres recetas con tiempos de preparación más largo, dímelo y con todo gusto te sugeriré recetas que requieren más tiempo”.
*Si la persona dice explícitamente que requiere recetas que duren más de 30 minutos en su preparación, dáselas.

6. ACTIVIDAD FÍSICA
*Si en la hoja 4 del archivo de Excel en la celda c2 aparece “bajo”, solo sugiere opciones de actividad física que sean intensas y no duren más de 30 minutos.
* Si en la hoja 4 del archivo de Excel en la celda b2 aparece “bajo”, solo sugiere opciones de actividad física que sean en casa.
*Al final de sugerir la actividad física, escribe: “veo que tu tiempo para hacer actividad física es poco, por eso las actividades que he sugerido no toman más de 30 minutos en su realización. Si requieres actividades más largas, dímelo y con todo gusto te sugeriré actividades que toman más tiempo”.
*Al final de sugerir la actividad física, escribe: “veo que prefieres actividades físicas en casa, por eso las actividades que he sugerido son al interior. Si requieres actividades más al aire libre, dímelo y con todo gusto te sugeriré actividades afuera”.
*Para sugerir la actividad física, escribe: 1) nombre de la actividad física, 2) duración, 3) descripción, 4) implementos requeridos. 5) Ubicación si es en casa o al aire libre. En caso que sea en un lugar específico, da la dirección.
*Al final de la sugerencia, escribe: “Compensar tiene un portafolio de actividades que pueden adaptarse a tus preferencias. ¿Quisieras conocer este portafolio?” Si dice que sí, sugiere una actividad física ofertada en https://www.tiendacompensar.com/.

7. SERVICIOS DE BIENESTAR DISPONIBLES:
    Ofrece máximo uno por vez, y que esté relacionado con lo que el usuario necesita.
    Categorías:
    - alimentación
    - actividad física
    - tips y educación sobre ECNT
    - recordatorio de chequeos médicos
    - toma de indicadores en salud (peso, talla, IMC, tensión, glucosa, etc.)"""

# Inicializa modelo
model = genai.GenerativeModel("gemini-2.5-pro", system_instruction=prompt_fijo)

app = Flask(__name__)

# sesiones en memoria: { user_id: chat_session_object }
sesiones = {}

# ------------------ CHAT SESSION ------------------
def get_chat_session(user_id):
    if user_id not in sesiones:
        sesiones[user_id] = model.start_chat(history=[])
    return sesiones[user_id]

# --------------------------- Google Drive helpers ---------------------------
def get_drive_service():
    creds_info = json.loads(SERVICE_ACCOUNT_JSON)
    creds = service_account.Credentials.from_service_account_info(
        creds_info,
        scopes=["https://www.googleapis.com/auth/drive.file"]
    )
    service = build("drive", "v3", credentials=creds)
    return service

INDEX_FILE = "drive_index.json"

def load_index():
    if os.path.exists(INDEX_FILE):
        try:
            with open(INDEX_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_index(index):
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(index, f)

def find_file_in_drive(service, filename):
    q = f"name = '{filename}' and '{FOLDER_ID}' in parents and trashed = false"
    try:
        res = service.files().list(q=q, spaces='drive', fields="files(id, name)").execute()
        files = res.get("files", [])
        if files:
            return files[0].get("id")
        return None
    except Exception as e:
        print("Error buscando archivo en Drive:", e)
        return None

def upload_or_update_file(filename):
    service = get_drive_service()
    basename = os.path.basename(filename)
    index = load_index()
    file_id = index.get(basename)
    media = MediaFileUpload(
        filename,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        resumable=True
    )
    if file_id:
        try:
            updated = service.files().update(
                fileId=file_id, media_body=media
            ).execute()
            print(f"♻️ Actualizado {basename} -> {updated.get('id')}")
            return updated.get("id")
        except Exception as e:
            print("⚠️ No se pudo actualizar usando fileId guardado:", e)
            index.pop(basename, None)
            save_index(index)

    found = find_file_in_drive(service, basename)
    if found:
        try:
            updated = service.files().update(fileId=found, media_body=media).execute()
            index[basename] = updated.get("id")
            save_index(index)
            print(f"♻️ Actualizado (found) {basename} -> {updated.get('id')}")
            return updated.get("id")
        except Exception as e:
            print("⚠️ Error actualizando archivo encontrado:", e)
    try:
        file_metadata = {"name": basename, "parents": [FOLDER_ID]}
        created = service.files().create(body=file_metadata, media_body=media, fields="id").execute()
        index[basename] = created.get("id")
        save_index(index)
        print(f"✅ Creado {basename} -> {created.get('id')}")
        return created.get("id")
    except Exception as e:
        print("⚠️ Error creando archivo en Drive:", e)
        return None

# --------------------------- Chat + Guardado ---------------------------
def guardar_en_excel(user_id, sujeto, mensaje):
    archivo = f"conversacion_{user_id}.xlsx"
    hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    nuevo = pd.DataFrame([[hora, sujeto, mensaje]], columns=["Hora", "Sujeto", "Mensaje"])

    if os.path.exists(archivo):
        existente = pd.read_excel(archivo)
        actualizado = pd.concat([existente, nuevo], ignore_index=True)
        actualizado.to_excel(archivo, index=False)
    else:
        nuevo.to_excel(archivo, index=False)

    return archivo

def chat_con_memoria(user_id, mensaje_usuario):
    archivo = guardar_en_excel(user_id, "Usuario", mensaje_usuario)
    chat_session = get_chat_session(user_id)
    response = chat_session.send_message(mensaje_usuario)
    respuesta = response.text
    archivo = guardar_en_excel(user_id, "Asistente", respuesta)

    # 🚀 Subida automática a Drive
    try:
        upload_or_update_file(archivo)
    except Exception as e:
        print("⚠️ Error subiendo a Drive:", e)

    return respuesta

# --------------------------- Rutas de Flask ---------------------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_id = data.get("user_id", "default")
    mensaje = data.get("mensaje", "")
    respuesta = chat_con_memoria(user_id, mensaje)
    return jsonify({"respuesta": respuesta})

@app.route("/download/<user_id>", methods=["GET"])
def download_local(user_id):
    archivo = f"conversacion_{user_id}.xlsx"
    if not os.path.exists(archivo):
        return jsonify({"error": "not found"}), 404
    return send_file(archivo, as_attachment=True)

# --------------------------- Run ---------------------------
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)