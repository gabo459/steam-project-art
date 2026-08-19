import os
import json
import urllib.request
import base64

API_KEY = os.environ.get("STEAM_API_KEY")
USER_INPUT = os.environ.get("STEAM_ID")

if not API_KEY or not USER_INPUT:
    print("Error: Faltan las variables de entorno STEAM_API_KEY o STEAM_ID.")
    exit(1)

def resolve_steam_id(input_val):
    val = input_val.strip().rstrip("/")
    if "/profiles/" in val:
        val = val.split("/profiles/")[1].split("/")[0]
    elif "/id/" in val:
        val = val.split("/id/")[1].split("/")[0]
    
    if val.isdigit() and len(val) == 17:
        return val

    # Consultar ResolveVanityURL
    url = f"https://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?key={API_KEY}&vanityurl={val}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as res:
        data = json.loads(res.read().decode('utf-8'))
        if data.get('response', {}).get('success') == 1:
            return data['response']['steamid']
    return val

try:
    steam_id = resolve_steam_id(USER_INPUT)
    print(f"Procesando Steam ID: {steam_id}")

    # Obtener juegos
    games_url = f"https://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={API_KEY}&steamid={steam_id}&format=json&include_appinfo=true"
    req = urllib.request.Request(games_url, headers={'User-Agent': 'Mozilla/5.0'})
    
    with urllib.request.urlopen(req) as res:
        data = json.loads(res.read().decode('utf-8'))

    games = data.get('response', {}).get('games', [])
    games.sort(key=lambda x: x.get('playtime_forever', 0), reverse=True)
    top_games = games[:24]

    output = []
    for g in top_games:
        appid = g['appid']
        img_url = f"https://shared.cloudflare.steamstatic.com/store_item_assets/steam/apps/{appid}/header.jpg"
        b64_img = None
        
        try:
            img_req = urllib.request.Request(img_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(img_req) as img_res:
                b64_img = "data:image/jpeg;base64," + base64.b64encode(img_res.read()).decode('utf-8')
        except Exception as e:
            print(f"Advertencia: No se pudo descargar la imagen para AppID {appid}: {e}")

        output.append({
            "appid": appid,
            "name": g.get("name", f"App {appid}"),
            "playtime_forever": g.get("playtime_forever", 0),
            "imageBase64": b64_img
        })

    with open("steam_games.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print("¡steam_games.json generado con éxito!")

except Exception as e:
    print(f"Error durante la ejecución: {e}")
    exit(1)
