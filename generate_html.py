import json
from datetime import datetime
from zoneinfo import ZoneInfo
import requests

MET_URL = "https://opendataapi.dmi.dk/v2/metObs/collections/observation/items"
OCEAN_URL = "https://opendataapi.dmi.dk/v2/oceanObs/collections/observation/items"

SPOTS = {
    "Helnæs Fyr og Torø (Sydvestfyn)": {
        "coords": "55.142° N, 9.998° E",
        "met_station": "06123",      # Vind: Assens/Torø 
        "ocean_level_st": "9020201", # Vandstand: Assens Havn I
        "ocean_temp_st": "23289",    # Temp: Fredericia Havn II
        "lae_vinde": ["Ø", "SØ", "NØ"]
    },
    "Kerteminde (Østfyn)": {
        "coords": "55.466° N, 10.658° E",
        "met_station": "06120",      # Vind: Odense Lufthavn
        "ocean_level_st": "9020401", # Vandstand: Kerteminde Havn I (bruger sea_reg)
        "ocean_temp_st": "9020401",  # Temp: Kerteminde Havn I
        "lae_vinde": ["V", "SV", "NV"]
    },
    "Nyborg Knudshoved og Slipshavn (Østfyn)": {
        "coords": "55.297° N, 10.853° E",
        "met_station": "06126",      # Vind: Årslev
        "ocean_level_st": "28234",   # Vandstand: Slipshavn
        "ocean_temp_st": "28231",    # Temp: Slipshavn II
        "lae_vinde": ["V", "SV", "NV", "S"]
    },
    "Flyvesandet (Nordfyn)": {
        "coords": "55.615° N, 10.297° E",
        "met_station": "06120",      # Vind: Odense Lufthavn
        "ocean_level_st": "9020101", # Vandstand: Bogense Havn I
        "ocean_temp_st": "23289",    # Temp: Fredericia Havn II
        "lae_vinde": ["S", "SØ", "SV"]
    }
}

# --- SKUDSIKKER CSS VARIABEL ---
CSS = """
html { scroll-behavior: smooth; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f172a; color: #f8fafc; max-width: 750px; margin: 0 auto; padding: 15px; }

.header-container { text-align: center; margin-top: 15px; margin-bottom: 5px; }

.logo { 
    width: 100%;
    max-width: 520px;
    height: auto;
    display: block;
    margin: 0 auto;
}

.timestamp-top { 
    text-align: center; 
    color: #94a3b8; 
    font-size: 0.9em; 
    margin-bottom: 20px; 
    margin-top: 10px; 
    line-height: 1.4;
}
.timestamp-top p {
    margin: 0 0 5px 0;
}
.timestamp-top strong {
    color: #f8fafc;
    font-weight: 500;
}

.quick-overview {
    background: #1e293b;
    border-radius: 12px;
    padding: 15px 20px;
    margin-bottom: 25px;
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.3);
    border: 1px solid rgba(255, 255, 255, 0.05);
}
.quick-overview h3 {
    margin-top: 0;
    margin-bottom: 15px;
    font-size: 1.05em;
    color: #f8fafc; 
    font-weight: 600;
    letter-spacing: 0.3px;
}
.quick-list {
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.quick-item {
    display: flex;
    flex-direction: column; 
    align-items: flex-start;
    background: #0f172a;
    padding: 12px 14px;
    border-radius: 8px;
    text-decoration: none;
    color: #f8fafc;
    transition: background 0.2s, transform 0.1s;
    border-left: 4px solid #64748b;
}
.quick-item:hover {
    background: #162032;
    transform: translateX(3px);
}
.quick-item.optimal { border-left-color: #22c55e; }
.quick-item.moderate { border-left-color: #eab308; }
.quick-item.warning { border-left-color: #f97316; }
.quick-item.bad { border-left-color: #ef4444; }

.quick-spot-name { 
    font-weight: 600; 
    font-size: 0.95em; 
    margin-bottom: 4px; 
    line-height: 1.3;
}
.quick-spot-status { 
    font-size: 0.9em; 
    color: #94a3b8; 
}

.card { background: #1e293b; border-radius: 12px; padding: 20px; margin-bottom: 20px; border-left: 6px solid #64748b; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.3); scroll-margin-top: 20px; }
.card h2 { margin-top: 0; margin-bottom: 2px; font-size: 1.4em; }

.coords { color: #94a3b8; font-size: 0.85em; font-family: monospace; margin-bottom: 15px; }

.card.optimal { border-left-color: #22c55e; }
.card.moderate { border-left-color: #eab308; }
.card.warning { border-left-color: #f97316; }
.card.bad { border-left-color: #ef4444; }

.info-list { background: #0f172a; padding: 12px; border-radius: 8px; margin: 15px 0; }
.info-list p { margin: 6px 0; font-size: 1em; }

.trend { color: #94a3b8; font-size: 0.9em; margin-left: 5px; }

.chart-container { position: relative; height: 125px; margin: 15px 0; background: #0f172a; border-radius: 8px; padding: 8px; }

.status { font-size: 1.1em; margin-top: 10px; }
.note { color: #94a3b8; font-style: italic; font-size: 0.95em; line-height: 1.4; }

/* Flexbox-footer med copyright og DMI-link */
.footer-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100%;
    padding: 15px 0;
    font-size: 0.85rem;
    color: #64748b;
    border-top: 1px solid rgba(255, 255, 255, 0.05);
    margin-top: 30px;
    margin-bottom: 20px;
}
.footer-container .footer-left {
    font-weight: 400;
}
.footer-container .dmi-link a {
    color: #38bdf8;
    text-decoration: none;
}
.footer-container .dmi-link a:hover {
    text-decoration: underline;
}

/* Back to Top Knap - Skubbet fri af kassen */
#scrollToTopBtn {
    display: none; 
    position: fixed; 
    bottom: 20px; 
    z-index: 99; 
    border: none; 
    outline: none; 
    background-color: #38bdf8; 
    color: #0f172a; 
    cursor: pointer; 
    width: 45px;
    height: 45px;
    border-radius: 50%; 
    font-size: 20px; 
    font-weight: bold;
    box-shadow: 0 4px 6px rgba(0,0,0,0.4);
    transition: background-color 0.2s, transform 0.2s;
    
    /* PC: Skubbet helt uden for den 750px brede max-width container */
    left: 50%;
    margin-left: 400px; 
}
#scrollToTopBtn:hover {
    background-color: #0284c7; 
    transform: scale(1.05);
}
/* Mobil / Tablets under 900px: Låser knappen til skærmens kant, så den ikke ryger uden for skærmen */
@media (max-width: 900px) {
    #scrollToTopBtn {
        left: auto;
        right: 20px;
        margin-left: 0;
    }
}
"""

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
    except requests.RequestException as e:
        print(f"Fejl ved hentning af vejr for {station_id}: {e}")
    return None

def hent_dmi_ocean_historik(station_id, limit=50):
    params = {"stationId": station_id, "limit": limit}
    try:
        res = requests.get(OCEAN_URL, params=params, timeout=10)
        if res.status_code == 200:
            features = res.json().get("features", [])
            vals = []
            times = []
            
            tilgaengelige_params = set(item["properties"]["parameterId"] for item in features if "parameterId" in item["properties"])
            target_param = "sea_reg" if "sea_reg" in tilgaengelige_params else "sealev_ln"

            for item in features:
                props = item["properties"]
                if props["parameterId"] == target_param:
                    val = props.get("value")
                    ts = props.get("observed") or props.get("time") or props.get("timeStamp") or ""
                    
                    if val is not None and ts:
                        try:
                            if "T" in ts and "Z" in ts:
                                ts_clean = ts.replace("Z", "")
                                dt_utc = datetime.fromisoformat(ts_clean)
                                dt_utc_aware = dt_utc.replace(tzinfo=ZoneInfo("UTC"))
                                dt_dk = dt_utc_aware.astimezone(ZoneInfo("Europe/Copenhagen"))
                                t_str = dt_dk.strftime("%H:%M")
                            elif "T" in ts:
                                t_str = ts.split("T")[1][:5]
                            else:
                                t_str = ""
                            
                            if t_str:
                                vals.append(val)
                                times.append(t_str)
                        except (TypeError, ValueError):
                            continue
            return vals, times
    except requests.RequestException as e:
        print(f"Fejl ved hentning af hav-historik for {station_id}: {e}")
    return [], []

def hent_dmi_ocean_val(station_id, target_param):
    params = {"stationId": station_id, "limit": 10}
    try:
        res = requests.get(OCEAN_URL, params=params, timeout=10)
        if res.status_code == 200:
            for item in res.json().get("features", []):
                props = item["properties"]
                if props["parameterId"] == target_param:
                    val = props.get("value")
                    if val is not None:
                        return val
    except requests.RequestException:
        pass
    return "N/A"

def evaluer_kyst(spot_navn, coords, met_data, vandstand_vals, vandstand_tider, temp, lae_vinde):
    hastighed = met_data.get("wind_speed", 0) if met_data else 0
    stod = met_data.get("wind_max", 0) if met_data else 0
    grader = met_data.get("wind_dir", 0) if met_data else 0
    kompas = grader_til_kompas(grader) if met_data else "N/A"
    
    vandstand = vandstand_vals[0] if vandstand_vals else 0
    
    trend_symbol, trend_tekst = "→", "Uændret"
    if isinstance(vandstand, (int, float)) and len(vandstand_vals) >= 6:
        gammel_vaerdi = vandstand_vals[5]
        diff = vandstand - gammel_vaerdi
        if diff > 0.8:
            trend_symbol, trend_tekst = "↑", "Stigende"
        elif diff < -0.8:
            trend_symbol, trend_tekst = "↓", "Faldende"

    if hastighed > 10:
        status, css_class, score = "❌ DÅRLIG (For kraftig vind)", "bad", 4
        note = f"Vind på {hastighed} m/s (stød op til {stod} m/s) skaber for meget uro, opslået bund og løsrevet tang. Det bliver svært at fiske effektivt her."
    elif kompas in lae_vinde:
        status, css_class, score = "🔥 OPTIMAL (Læ / Sidevind)", "optimal", 1
        note = f"Vind fra {kompas} ({hastighed} m/s) giver fine, rolige kasteforhold. "
        if trend_tekst == "Stigende":
            note += f"Vandstanden er {vandstand:+.1f} cm og **stigende**, hvilket ofte presser havørreden helt tæt på kysten. Optimalt til at sende en 14-16g line-thru (f.eks. en motoroil Zerling) afsted over det lave vand!"
        elif trend_tekst == "Faldende":
            note += f"Vandstanden er {vandstand:+.1f} cm og **faldende**. Fisken kan søge med ud mod rev og dybere kanten, så affisk skrænterne grundigt."
        else:
            note += f"Vandstanden er stabilt omkring {vandstand:+.1f} cm. Gode betingelser for at afsøge strækket med en 14-16g line-thru."
    elif hastighed <= 3:
        status, css_class, score = "⚠️ NOGENLUNDE (Blikstille)", "warning", 3
        note = f"Næsten blikstille ({hastighed} m/s). Vandet er sandsynligvis meget klart, hvilket kan gøre havørreden sky. Sørg for at liste langs kanten og kaste langt."
        if isinstance(vandstand, (int, float)):
            note += f" Vandstand: {vandstand:+.1f} cm ({trend_tekst})."
    else:
        status, css_class, score = "🟡 MODERAT (Pålandsvind)", "moderate", 2
        note = f"Vind fra {kompas} ({hastighed} m/s) står direkte ind på kysten og skaber god sløring og fødeemner i vandet."
        if trend_tekst == "Stigende":
            note += f" Da vandet samtidig er **stigende** (+{vandstand:.1f} cm), er der gode chancer for fisk på det nære vand, selvom modvinden kan gøre kastene tunge."
        else:
            note += f" Vandstand er {vandstand:+.1f} cm ({trend_tekst}). Gode betingelser, men vær opmærksom på eventuelle bølger."

    graf_data = list(reversed(vandstand_vals)) if vandstand_vals else []
    graf_tider = list(reversed(vandstand_tider)) if vandstand_tider else []

    return {
        "spot": spot_navn, "coords": coords, "hastighed": hastighed, "stod": stod,
        "kompas": kompas, "vandstand": vandstand, "trend_symbol": trend_symbol, "trend_tekst": trend_tekst,
        "temp": temp, "status": status, "css_class": css_class, "note": note, "score": score, 
        "graf_data": graf_data, "graf_tider": graf_tider
    }

def main():
    results = []
    
    for spot_navn, info in SPOTS.items():
        met_data = hent_dmi_met(info["met_station"])
        vals, times = hent_dmi_ocean_historik(info["ocean_level_st"], limit=50)
        temp = hent_dmi_ocean_val(info["ocean_temp_st"], "tw")
        
        vurdering = evaluer_kyst(spot_navn, info["coords"], met_data, vals, times, temp, info["lae_vinde"])
        results.append(vurdering)

    results.sort(key=lambda x: x["score"])

    overview_html = ""
    cards_html = ""
    chart_scripts = ""
    
    for i, r in enumerate(results):
        chart_id = f"waterChart{i}"
        anchor_id = f"spot-{i}"
        
        overview_html += f"""
        <a href="#{anchor_id}" class="quick-item {r['css_class']}">
            <span class="quick-spot-name">📍 {r['spot']}</span>
            <span class="quick-spot-status">{r['status']}</span>
        </a>
        """

        json_tider = json.dumps(r['graf_tider'])
        json_data = json.dumps(r['graf_data'])

        cards_html += f"""
        <div id="{anchor_id}" class="card {r['css_class']}">
            <h2>{r['spot']}</h2>
            <div class="coords">📍 {r['coords']}</div>
            <div class="info-list">
                <p><strong>Vind:</strong> {r['hastighed']} m/s (stød {r['stod']} m/s) fra {r['kompas']}</p>
                <p><strong>Vandstand:</strong> {r['vandstand']} cm <span class="trend">({r['trend_symbol']} {r['trend_tekst']})</span></p>
                <p><strong>Vandtemp:</strong> {r['temp']} °C</p>
            </div>
            <div class="chart-container">
                <canvas id="{chart_id}"></canvas>
            </div>
            <p class="status"><strong>Status:</strong> {r['status']}</p>
            <p class="note">{r['note']}</p>
        </div>
        """
        
        chart_scripts += f"""
        const ctx{i} = document.getElementById('{chart_id}').getContext('2d');

        new Chart(ctx{i}, {{
            type: 'line',
            data: {{
                labels: {json_tider},
                datasets: [{{
                    data: {json_data},
                    borderColor: '#38bdf8',
                    borderWidth: 2,
                    pointRadius: 0,
                    pointBackgroundColor: '#38bdf8',
                    tension: 0.3,
                    fill: true,
                    backgroundColor: 'rgba(56, 189, 248, 0.05)'
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{ legend: {{ display: false }}, tooltip: {{ enabled: true }}}},
                scales: {{
                    x: {{ 
                        display: true,
                        grid: {{ display: false }},
                        ticks: {{ 
                            color: '#64748b', 
                            font: {{ size: 9 }},
                            autoSkip: true,
                            maxTicksLimit: 6
                        }}
                    }},
                    y: {{ 
                        grid: {{ color: 'rgba(255, 255, 255, 0.05)' }},
                        ticks: {{ 
                            color: '#64748b', 
                            font: {{ size: 9 }}
                        }}
                    }}
                }}
            }}
        }});
        """

    nu = datetime.now(ZoneInfo("Europe/Copenhagen")).strftime("%d-%m-%Y kl. %H:%M")

    full_html = f"""
    <!DOCTYPE html>
    <html lang="da">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta http-equiv="refresh" content="900">
        <title>ErKystenKlar.dk</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
{CSS}
        </style>
    </head>
    <body>
        <div class="header-container">
            <img src="logo.png?v={nu}" alt="ErKystenKlar.dk" class="logo">
        </div>
        
        <div class="timestamp-top">
            <p>Data hentes automatisk hvert 10. minut, direkte i takt med DMI's live-opdateringer.</p>
            <strong>Seneste opdatering: {nu}</strong>
        </div>

        <div class="quick-overview">
            <h3>Aktuelle vejr- og havdata fra DMI – tilpasset til de fynske kyststræk.</h3>
            <div class="quick-list">
                {overview_html}
            </div>
        </div>
        
        {cards_html}

        <div class="footer-container">
            <div class="footer-left">© 2026 ErKystenKlar.dk</div>
            <div class="dmi-link">Data leveret af <a href="https://www.dmi.dk/" target="_blank">DMI Open Data</a></div>
        </div>

        <button id="scrollToTopBtn" onclick="window.scrollTo({{top: 0, behavior: 'smooth'}})" title="Gå til toppen">&#8593;</button>

        <script>
            {chart_scripts}

            let mybutton = document.getElementById("scrollToTopBtn");
            window.onscroll = function() {{
                if (document.body.scrollTop > 300 || document.documentElement.scrollTop > 300) {{
                    mybutton.style.display = "block";
                }} else {{
                    mybutton.style.display = "none";
                }}
            }};
        </script>
    </body>
    </html>
    """

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(full_html)
    
    print(f"Succes! index.html blev genereret med rettet placering af pil op ({nu}).")

if __name__ == "__main__":
    main()