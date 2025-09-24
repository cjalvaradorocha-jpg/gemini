# authorize.py
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/drive.file"]  # permiso para crear/editar archivos que la app crea

def main():
    flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
    creds = flow.run_local_server(port=0)  # abre navegador para autorizar
    with open("token.json", "w") as f:
        f.write(creds.to_json())
    print("token.json creado. Úsalo en tu servidor / despliegue.")

if __name__ == "__main__":
    main()
