import threading
import time
import requests

# === CONFIG ===
TOKENS = [
    "TOKEN_1",
    "TOKEN_2"
]

WEBHOOK_URL = "https://discord.com/api/webhooks/1389013099729653865/NFVE591oGbqd7-XEFw-48Z35xHIOcP4B8DPJapPZLfIeacYj7B3sMw8u4JSOInUANOGj"
DELAY = 8

# === Couleurs ANSI ===
RED = "\033[91m"
GREEN = "\033[92m"
BLUE = "\033[94m"
RESET = "\033[0m"

# === Variables globales ===
watchlist = []
index = 0
lock = threading.Lock()

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

def worker(token):
    global index
    while True:
        with lock:
            if index >= len(watchlist):
                index = 0
            pseudo = watchlist[index]
            index += 1
        print(BLUE + f"[~] Token {token[:6]} vérifie @{pseudo}" + RESET)
        if is_available(pseudo, token):
            print(GREEN + f"[✅] DISPONIBLE : @{pseudo}" + RESET)
            send_to_webhook(pseudo)
        else:
            print(RED + f"[✘] Indisponible : @{pseudo}" + RESET)
        time.sleep(DELAY)

def main():
    global watchlist
    watchlist = load_watchlist()
    threads = []
    for token in TOKENS:
        t = threading.Thread(target=worker, args=(token,))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()

if __name__ == "__main__":
    main()
