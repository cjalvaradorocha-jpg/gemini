import google.generativeai as genai

genai.configure(api_key="AIzaSyAJCKizgv4TqMaAHZYzLqHRY-EaihMCV58")

model = genai.GenerativeModel("gemini-2.5-pro")

response = model.generate_content("Escribe un haiku sobre los atardeceres en la playa")
print(response.text)
