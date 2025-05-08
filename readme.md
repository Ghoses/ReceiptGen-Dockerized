🛒 Lidl Kassenzettel Generator 🧾 - Web-App Edition

Erstelle realistische Lidl-Kassenzettel als Screenshots – vollautomatisch mit Python, Flask und Selenium!
Dieses Projekt generiert zufällige Kassenzettel mit authentisch wirkenden Artikeln, Preisen, Mehrwertsteuer-Berechnung, Barcode und weiteren typischen Informationen. Dabei wird sichergestellt, dass der Gesamtbetrag immer innerhalb eines realistischen Rahmens liegt – ab einem Mindestbetrag von ca. 6,90 € bis maximal 23,00 €.

🚀 Features
Realistische Einkaufsbons:
Zufällige Artikel aus einer konfigurierbaren Warenliste inklusive Preisberechnung.
Mindestbetrag:
Es werden ausschließlich Kassenzettel mit einem Gesamtbetrag zwischen ca. 6,90 € und 23,00 € generiert.
Screenshot-Speicherung:
Ausgabe der Kassenzettel als Bilddateien (Screenshot) mittels Selenium & ChromeDriver.
Dynamische Preisberechnung:
Automatische Berechnung von Mehrwertsteuer, Nettobetrag und Gesamtpreis.
Einstellbarer Zeitraum:
Möglichkeit, Kassenzettel für einen beliebigen Zeitraum (mehrere Tage) zu generieren.
Web-Interface:
Modernes, benutzerfreundliches Web-Interface mit Flask zur einfachen Bedienung.
Download-Funktionen:
Möglichkeit, einzelne oder mehrere Kassenzettel als Bilder oder ZIP-Archiv herunterzuladen.
White-Label-Fähigkeit:
Alle relevanten Informationen (Warenliste, Filialdaten, Logo-Pfad) werden über externe JSON-Dateien konfiguriert und sind somit leicht anpassbar.

🔧 Installation & Einrichtung
1️⃣ Voraussetzungen
Python 3.x (getestet mit 3.8+)
Google Chrome (aktuelle Version)
ChromeDriver für Selenium
(Wird automatisch installiert, falls nicht vorhanden – dank webdriver_manager.)

2️⃣ Python-Abhängigkeiten installieren
Öffne eine Konsole und führe folgenden Befehl aus:

```bash
pip install -r requirements.txt
```

3️⃣ Konfiguration anpassen (optional)
- Artikelliste: Passe die Artikelliste und Preise in der Datei `list.json` an.
- Filialdaten & Logo: Ändere in der Datei `stores.json` die Informationen zu den Filialen (Adresse, USt-ID etc.) sowie den Pfad zum Logo-Bild.

4️⃣ Anwendung starten
Starte die Web-App mit:

```bash
python app.py
```

Die Web-App ist dann unter http://localhost:5000 erreichbar.

🎯 Nutzung
1. Web-Interface:
   - Öffne die Web-App in deinem Browser unter http://localhost:5000
   - Wähle zwischen der Generierung eines einzelnen Kassenzettels oder mehrerer Kassenzettel für einen Zeitraum
   - Nach der Generierung werden die Kassenzettel angezeigt und können heruntergeladen werden

2. Ergebnis:
   - Die generierten Kassenzettel werden als PNG-Screenshots im Ordner `static/generated` gespeichert
   - Einzelne Kassenzettel können direkt heruntergeladen werden
   - Mehrere Kassenzettel können als ZIP-Archiv heruntergeladen werden

📋 Deployment auf einem Webserver
1. Übertrage alle Dateien per FTP auf deinen Webserver
2. Installiere die Abhängigkeiten: `pip install -r requirements.txt`
3. Konfiguriere den Webserver, um die WSGI-Anwendung auszuführen (z.B. mit gunicorn)
4. Starte die Anwendung im Produktionsmodus: `gunicorn wsgi:app`

⚠️ Hinweis zur Produktionsumgebung
Diese Anwendung nutzt Selenium und ChromeDriver. Stelle sicher, dass dein Webserver:
- Chrome oder Chromium installiert hat
- Headless-Browser-Operationen unterstützt
- Ausreichende Berechtigungen zum Erstellen temporärer Dateien hat