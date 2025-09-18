from flask import Flask, request, jsonify, render_template
import google.generativeai as genai

genai.configure(api_key="AIzaSyBML2vnnrmeHk-xGh4xx1XUiGE2JQ-66pk")
model = genai.GenerativeModel("gemini-1.5-flash")

app = Flask(__name__)
historial = []

def chat_con_memoria(mensaje_usuario):
    global historial
    historial.append(("user", mensaje_usuario))
    contexto = "\n".join([f"Usuario: {m}" if r == "user" else f"Asistente: {m}" for r, m in historial])
    response = model.generate_content(contexto)
    respuesta = response.text
    historial.append(("assistant", respuesta))
    return respuesta

@app.route("/")
def index():
    return render_template("index.html")  # el HTML está en /templates/index.html

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    mensaje = data.get("mensaje", "")
    respuesta = chat_con_memoria(mensaje)
    return jsonify({"respuesta": respuesta})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")