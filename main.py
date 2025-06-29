import threading
import time
import requests
import os
from flask import Flask

app = Flask(__name__)

# Mets tes tokens dans les variables d'environnement Render ou remplace ici en dur (non recommandé)
TOKENS = [
    os.getenv("TOKEN_1"),  # remplace ou mets tes tokens en variables d'env
    os.getenv("TOKEN_2")
]

WEBHOOK_URL = os.getenv("WEBHOOK")

RED = "\033[91m"
GREEN = "\033[92m"
BLUE = "\033[94m"
RESET = "\033[0m"

# Ta watchlist dans un fichier txt (met à jour 'watchlist.txt' sur Render/GitHub)
def load_watchlist(file_path="watchlist.txt"):
    with open(file_path, "r") as f:
        return [line.strip() for line in f if line.strip()]

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
            print(RED + f"[!] Erreur 401 : token invalide" + RESET)
    except Exception as e:
        print(RED + f"[!] Erreur réseau : {e}" + RESET)
    return False

def send_to_webhook(pseudo):
    data = {
        "content": f"✅ **Pseudo dispo** : `{pseudo}`"
    }
    try:
        requests.post(WEBHOOK_URL, json=data)
    except Exception as e:
        print(RED + f"[!] Erreur envoi webhook : {e}" + RESET)

watchlist = []
index = 0
lock = threading.Lock()
DELAY = 8

def checker_loop():
    global index
    while True:
        with lock:
            if index >= len(watchlist):
                index = 0
            pseudo = watchlist[index]
            index += 1
        print(BLUE + f"[~] Vérification @{pseudo}" + RESET)
        for token in TOKENS:
            if token is None:
                print(RED + "[!] Token manquant ou non chargé." + RESET)
                continue
            if is_available(pseudo, token):
                print(GREEN + f"[✅] DISPONIBLE : @{pseudo}" + RESET)
                send_to_webhook(pseudo)
                break
            else:
                print(RED + f"[✘] Indisponible : @{pseudo}" + RESET)
        time.sleep(DELAY)

@app.route("/")
def home():
    return "Sniper Discord actif !"

if __name__ == "__main__":
    watchlist = load_watchlist()
    thread = threading.Thread(target=checker_loop)
    thread.daemon = True
    thread.start()
    app.run(host="0.0.0.0", port=10000)

