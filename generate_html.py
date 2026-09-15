import requests
from datetime import datetime

MET_URL = "https://opendataapi.dmi.dk/v2/metObs/collections/observation/items"
OCEAN_URL = "https://opendataapi.dmi.dk/v2/oceanObs/collections/observation/items"

SPOTS = {
    "Helnæs Fyr (Sydvestfyn)": {
        "coords": "55.142° N, 9.998° E",
        "met_station": "06120",
        "ocean_level_st": "23293",
        "ocean_temp_st": "23289",
        "lae_vinde": ["Ø", "SØ", "NØ"]
    },
    "Kerteminde Nordstrand (Østfyn)": {
        "coords": "55.466° N, 10.658° E",
        "met_station": "06120",
        "ocean_level_st": "28234",
        "ocean_temp_st": "28231",
        "lae_vinde": ["V", "SV", "NV"]
    },
    "Knudshoved / Nyborg (Østfyn)": {
        "coords": "55.297° N, 10.853° E",
        "met_station": "06120",
        "ocean_level_st": "28234",
        "ocean_temp_st": "28231",
        "lae_vinde": ["V", "SV", "NV", "S"]
    },
    "Flyvesandet (Nordfyn)": {
        "coords": "55.615° N, 10.297° E",
        "met_station": "06126",
        "ocean_level_st": "28234",
        "ocean_temp_st": "23131",
        "lae_vinde": ["S", "SØ", "SV"]
    }
}

def grader_til_kompas(grader):
    retninger = ["N", "NØ", "Ø", "SØ", "S", "SV", "V", "NV"]
    idx = int((grader + 22.5) // 45) % 8
    return retninger[idx]

def hent_dmi_met(station_id):
    params = {"stationId": station_id, "limit": 30}
    try:
        res = requests.get(MET_URL, params=params, timeout=10)
        if res.status_code == 200:
            features = res.json().get("features", [])
            data = {}
            for item in features:
                props = item["properties"]
                param = props["parameterId"]
                if param in ["wind_speed", "wind_dir", "wind_max"] and param not in data:
                    data[param] = props["value"]
            return data
    except Exception as e:
        print(f"Fejl ved hentning af vejr for {station_id}: {e}")
    return None

def hent_dmi_ocean_val(station_id, target_param):
    params = {"stationId": station_id, "limit": 30}
    try:
        res = requests.get(OCEAN_URL, params=params, timeout=10)
        if res.status_code == 200:
            features = res.json().get("features", [])
            for item in features:
                props = item["properties"]
                param = props["parameterId"]
                if param == target_param:
                    return props["value"]
    except Exception as e:
        print(f"Fejl ved hentning af havdata for {station_id}: {e}")
    return "N/A"

def evaluer_kyst(spot_navn, coords, met_data, vandstand, temp, lae_vinde):
    hastighed = met_data.get("wind_speed", 0) if met_data else 0
    stod = met_data.get("wind_max", 0) if met_data else 0
    grader = met_data.get("wind_dir", 0) if met_data else 0
    kompas = grader_til_kompas(grader) if met_data else "N/A"
    
    if hastighed > 10:
        status, css_class, score = "❌ DÅRLIG (For kraftig vind)", "bad", 4
        note = f"Vind på {hastighed} m/s giver for meget opslået vand og løsrevet tang. Svært at fiske effektivt."
    elif kompas in lae_vinde:
        status, css_class, score = "🔥 OPTIMAL (Læ / Sidevind)", "optimal", 1
        note = f"Vind fra {kompas} giver gode kasteforhold. Perfekt vind til at sende en 14-16g line-thru (f.eks. en motoroil Zerling) afsted!"
    elif hastighed <= 3:
        status, css_class, score = "⚠️ NOGENLUNDE (Blikstille)", "warning", 3
        note = "Næsten blikstille. Vandet er sandsynligvis meget klart, hvilket kan gøre havørreden sky på det lave vand."
    else:
        status, css_class, score = "🟡 MODERAT (Pålandsvind)", "moderate", 2
        note = f"Vind fra {kompas} direkte ind på kysten. Skaber god sløring i vandet, men modvind kan gøre kastene tunge."
        
    if isinstance(vandstand, (int, float)):
        if vandstand > 15:
            note += f" Høj vandstand (+{vandstand} cm): Fisken kan trække helt ind på det lave vand."
        elif vandstand < -15:
            note += f" Lav vandstand ({vandstand} cm): Søg ud mod dybere pynter, rev og skrænter."

    return {
        "spot": spot_navn, "coords": coords, "hastighed": hastighed, "stod": stod,
        "kompas": kompas, "vandstand": vandstand, "temp": temp,
        "status": status, "css_class": css_class, "note": note, "score": score
    }

def main():
    results = []
    
    for spot_navn, info in SPOTS.items():
        met_data = hent_dmi_met(info["met_station"])
        vandstand = hent_dmi_ocean_val(info["ocean_level_st"], "sealev_ln")
        temp = hent_dmi_ocean_val(info["ocean_temp_st"], "tw")
        
        vurdering = evaluer_kyst(spot_navn, info["coords"], met_data, vandstand, temp, info["lae_vinde"])
        results.append(vurdering)

    # HER ER MAGIEN! Vi sorterer results-listen, så det laveste 'score'-tal kommer først (1 = OPTIMAL, osv.)
    results.sort(key=lambda x: x["score"])

    cards_html = ""
    for r in results:
        cards_html += f"""
        <div class="card {r['css_class']}">
            <h2>{r['spot']}</h2>
            <div class="coords">📍 {r['coords']}</div>
            <div class="info-list">
                <p><strong>Vind:</strong> {r['hastighed']} m/s (stød {r['stod']} m/s) fra {r['kompas']}</p>
                <p><strong>Vandstand:</strong> {r['vandstand']} cm</p>
                <p><strong>Vandtemp:</strong> {r['temp']} °C</p>
            </div>
            <p class="status"><strong>Status:</strong> {r['status']}</p>
            <p class="note">{r['note']}</p>
        </div>
        """

    nu = datetime.now().strftime("%d-%m-%Y kl. %H:%M")

    full_html = f"""
    <!DOCTYPE html>
    <html lang="da">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Fynsk Kystfiske-Analyzer</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f172a; color: #f8fafc; max-width: 750px; margin: 0 auto; padding: 15px; }}
            h1 {{ text-align: center; color: #38bdf8; margin-bottom: 5px; font-size: 1.8em; }}
            .timestamp {{ text-align: center; color: #64748b; font-size: 0.9em; margin-bottom: 25px; }}
            
            .card {{ background: #1e293b; border-radius: 12px; padding: 20px; margin-bottom: 20px; border-left: 6px solid #64748b; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.3); }}
            .card h2 {{ margin-top: 0; margin-bottom: 2px; font-size: 1.4em; }}
            
            .coords {{ color: #94a3b8; font-size: 0.85em; font-family: monospace; margin-bottom: 15px; }}
            
            .card.optimal {{ border-left-color: #22c55e; }}
            .card.moderate {{ border-left-color: #eab308; }}
            .card.warning {{ border-left-color: #f97316; }}
            .card.bad {{ border-left-color: #ef4444; }}
            
            .info-list {{ background: #0f172a; padding: 12px; border-radius: 8px; margin: 15px 0; }}
            .info-list p {{ margin: 6px 0; font-size: 1em; }}
            
            .status {{ font-size: 1.1em; margin-top: 10px; }}
            .note {{ color: #94a3b8; font-style: italic; font-size: 0.95em; line-height: 1.4; }}
        </style>
    </head>
    <body>
        <h1>🎣 Kystfiske-Analyzer</h1>
        <div class="timestamp">Opdateret: {nu}</div>
        
        {cards_html}
        
    </body>
    </html>
    """

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(full_html)
    
    print(f"Succes! index.html blev genereret {nu} - Spots er nu sorteret!")

if __name__ == "__main__":
    main()