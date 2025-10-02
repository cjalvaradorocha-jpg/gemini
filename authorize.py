# authorize.py
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/drive.file"]
CLIENT_SECRETS_FILE = "client_secret.json"

def main():
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    creds = flow.run_local_server(port=0)
    # Guarda token.json (contendrá refresh_token si diste permiso 'offline' en la primera autorización)
    with open("token.json", "w", encoding="utf-8") as f:
        f.write(creds.to_json())
    print("✅ token.json creado. NO lo subas a repos públicos.")

if __name__ == "__main__":
    main()
