# upload.py
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

# --- CONFIG ---
TOKEN_JSON = "token.json"
SCOPES = ["https://www.googleapis.com/auth/drive.file"]

def main():
    # Cargar credenciales desde token.json
    creds = Credentials.from_authorized_user_file(TOKEN_JSON, SCOPES)

    # Crear servicio de Drive
    service = build("drive", "v3", credentials=creds)

    # Archivo que quieres subir
    file_metadata = {
        "name": "archivo.xlsx",
        "parents": ["1y8FBTOq3ocW4JsTmB3fgiJRQI50Zckkv"],
    }
    media = MediaFileUpload("test_oauth.txt", mimetype="text/plain")

    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id"
    ).execute()

    print(f"✅ Archivo subido con éxito. ID: {file.get('id')}")

if __name__ == "__main__":
    main()
