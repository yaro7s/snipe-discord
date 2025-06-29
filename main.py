import threading
import time
import requests
import os
from flask import Flask

app = Flask(__name__)

# Récupère les tokens et le webhook via Render > Environment
TOKENS = [
    os.getenv("TOKEN_1"),
    os.getenv("TOKEN_2")
]

WEBHOOK_URL = os.getenv("WEBHOOK")

# Charge les pseudos depuis le fichier
def load_watchlist(file_path="watchlist.txt"):
    try:
        with open(file_path, "r") as f:
            return [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"[!] Erreur lors du chargement de la watchlist : {e}")
        return []

# Teste si un pseudo est disponible
def is_available(pseudo, token):
    url = "https://discord.com/api/v9/users/@me"
    headers = {
        "Authorization": token,
        "Content-Type": "application/json"
    }
    payload = {
        "username": pseudo,
        "discriminator": "0"
    }
    try:
        response = requests.patch(url, json=payload, headers=headers)
        if response.status_code == 200:
            return True
        elif response.status_code == 400:
            if "username" in response.json().get("errors", {}):
                return False
        elif response.status_code == 401:
            print(f"[!] Erreur 401 : token invalide")
    except Exception as e:
        print(f"[!] Erreur réseau : {e}")
    return False

# Envoie un message au webhook Discord si dispo
def send_to_webhook(pseudo):
    data = {
        "content": f"✅ **Pseudo dispo** : `{pseudo}`"
    }
    try:
        requests.post(WEBHOOK_URL, json=data)
    except Exception as e:
        print(f"[!] Erreur envoi webhook : {e}")

# Paramètres et boucle principale
watchlist = []
index = 0
lock = threading.Lock()
DELAY = 8  # secondes entre chaque test

def checker_loop():
    global index
    while True:
        with lock:
            if index >= len(watchlist):
                index = 0
            pseudo = watchlist[index]
            index += 1
        print(f"[~] Vérification @{pseudo}")
        for token in TOKENS:
            if token is None:
                print("[!] Token manquant ou non chargé.")
                continue
            if is_available(pseudo, token):
                print(f"[✅] DISPONIBLE : @{pseudo}")
                send_to_webhook(pseudo)
                break
            else:
                print(f"[✘] Indisponible : @{pseudo}")
        time.sleep(DELAY)

# Petit serveur web pour Render
@app.route("/")
def home():
    return "Sniper Discord actif !"

# Point d'entrée Render
if __name__ == "__main__":
    watchlist = load_watchlist()
    if not watchlist:
        print("[!] Aucune watchlist trouvée ou vide.")
    else:
        print(f"[✓] {len(watchlist)} pseudos chargés.")
    thread = threading.Thread(target=checker_loop)
    thread.daemon = True
    thread.start()
    app.run(host="0.0.0.0", port=10000)
