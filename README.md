# Kystindex.dk 🎣

En automatiseret løsning til overvågning af fynske kyst- og vejrforhold for havets lystfiskere. 

Henter live-data fra DMI, analyserer kystforholdene (vind, vandstand og vandtemperatur) og genererer en opdateret oversigt med grafer.

## 🚀 Hvordan det virker
* **Data-fetch & Generering:** Et Python-script (`generate_html.py`) henter data via DMI Open Data og bygger `index.html`.
* **Automatisering:** Workflowet trigges eksternt via et eksternt cron-job eller manuelt (`workflow_dispatch`).
* **Udgivelse:** Siden udgives automatisk via **GitHub Pages**, og ændringer committes direkte til `main`-branchen.
