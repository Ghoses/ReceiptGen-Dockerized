from flask import Flask, render_template, request, send_file, jsonify, url_for, redirect, flash, send_from_directory, session
from datetime import datetime, timedelta
import os
import random
import json
import tempfile
import shutil
import zipfile
import io
from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
# Kommentiere die folgende Zeile aus, da wir den lokalen ChromeDriver verwenden werden
# from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'generated')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default_secret_key_for_development')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload

# Stelle sicher, dass der Upload-Ordner existiert
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Kontext-Prozessor, um die aktuelle Zeit und timedelta in allen Templates verfügbar zu machen
@app.context_processor
def inject_now():
    """Make datetime objects available in all templates."""
    return {
        'now': datetime.now(),
        'timedelta': timedelta
    }

def resource_path(relative_path):
    """Returns the absolute path to a resource."""
    base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def load_json(filename):
    """Loads a JSON file from the given relative path."""
    json_path = resource_path(filename)
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"File not found: {json_path}")
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)

# Load configuration (logo and store data) from stores.json
config = load_json("stores.json")
logo_path = config["logo"]
stores = config["stores"]

# Load the product list from list.json
available_items = load_json("list.json")

def generate_random_barcode_html(bar_count=35):
    """Generates an HTML barcode."""
    barcode_parts = []
    barcode_parts.append(
        '<div style="text-align:center; margin-top:10px;">'
        '<div style="display:inline-block; white-space:nowrap; font-size:0; line-height:0;">'
    )
    for _ in range(bar_count):
        black_width = random.randint(1, 4)
        space_width = random.randint(1, 3)
        barcode_parts.append(
            f'<span style="display:inline-block; vertical-align:top; width:{black_width}px; height:60px; background-color:black;"></span>'
        )
        barcode_parts.append(
            f'<span style="display:inline-block; vertical-align:top; width:{space_width}px; height:60px; background-color:#fff;"></span>'
        )
    barcode_parts.append('</div></div>')
    return "".join(barcode_parts)

def generate_receipt_text(fixed_date):
    """Generates the complete HTML text for a receipt with items, barcode, and date."""
    today_date = datetime.now().strftime("%d.%m.%Y")
    if fixed_date == today_date:
        fixed_time = f"{random.randint(7, 8):02d}:{random.randint(0, 59):02d}:{random.randint(0, 59):02d}"
    else:
        fixed_time = f"{random.randint(7, 22):02d}:{random.randint(0, 59):02d}:{random.randint(0, 59):02d}"
    
    time_obj = datetime.strptime(fixed_time, "%H:%M:%S")
    random_seconds = random.randint(4, 28)
    fixed_time_pay = (time_obj + timedelta(seconds=random_seconds)).strftime("%H:%M:%S")
    fixed_date_time = f"{fixed_date} {fixed_time}"
    fixed_date_time_pay = f"{fixed_date} {fixed_time_pay}"
    
    # Select a random store from the loaded list
    store = random.choice(stores)
    address_str = store['address'].replace('\n', '<br>')
    
    tse_number = random.randint(100000, 999999)
    kasse_number = f"{random.randint(100, 999)}-{random.randint(1000, 9999)}"
    pruefwert = ''.join(random.choices("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+/", k=30))
    pruefwertt = ''.join(random.choices("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+/", k=40))
    signature_counter = random.randint(100000, 999999)
    serial_number = f"{random.randint(1000, 9999)} {random.randint(100000, 999999)}/{random.randint(1, 99)}"
    ust_id = store['ust_id']
    
    total_amount = 0
    items = []
    while total_amount < 6.91 or total_amount > 23.00:
        items = random.sample(available_items, random.randint(3, 6))
        total_amount = sum(price for _, price in items)
    
    vat = total_amount * 0.07
    net = total_amount - vat
    
    receipt_lines = []
    receipt_lines.append("                           EUR")
    for item, price in items:
        line = f"{item:30}{price:8.2f} A"
        receipt_lines.append(line)
    
    receipt_lines.append("-" * 40)
    receipt_lines.append(f"zu zahlen                     {total_amount:8.2f}")
    receipt_lines.append("MWST%       MWST      Netto     Brutto")
    line_vat = f"A  7%{vat:11.2f}{net:11.2f}{total_amount:11.2f}"
    receipt_lines.append(line_vat)
    receipt_lines.append(f"TSE Transaktionsnummer: {tse_number}")
    receipt_lines.append(f"Seriennr. Kasse: {kasse_number}")
    receipt_lines.append(f"Prüfwert: {pruefwert}")
    receipt_lines.append(f"{pruefwertt}")
    receipt_lines.append(f"Signaturzähler: {signature_counter}")
    receipt_lines.append(f"{serial_number}   {fixed_date_time}")
    receipt_lines.append(f"UST-ID-NR: {ust_id}")
    receipt_lines.append("-" * 40)
    
    receipt_text = "\n".join(receipt_lines)
    bottom_text = f"""
    <div class="centered-info">K-U-N-D-E-N-B-E-L-E-G</div>
    <div class="centered-info">Bezahlung: Bar</div>
    <div class="centered-info">Datum {fixed_date_time_pay}</div>
    """
    bottom_block = f"""
    {bottom_text}
    {generate_random_barcode_html(bar_count=100)}
    """
    
    # Absoluter Pfad zum Logo für die HTML-Einbettung
    logo_absolute_path = os.path.abspath(os.path.join("static", logo_path))
    logo_path_formatted = logo_absolute_path.replace('\\', '/')
    
    html_content = f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="utf-8" />
    <title>Kassenzettel {fixed_date_time}</title>
    <style>
    body {{
        margin: 0 auto;
        font-family: "Inconsolata", "Consolas", monospace;
        font-size: 21.5px;
        font-weight: bolder;
        line-height: 1.8;
        text-align: center;
    }}
    .receipt-wrapper {{
        white-space: pre;
        text-align: left;
        max-width: 90%;
        margin: 0 auto;
    }}
    .container-wrapper {{
        display: flex; 
        justify-content: center; 
        align-items: center;
    }}
    .logo {{
        margin-bottom: 20px;
        margin-top: 30px;
        text-align: center;
    }}
    .store-address {{
        text-align: center;
        font-weight: bold;
        margin: 1em 0;
    }}
    .centered-info {{
        text-align: center;
        margin: 0.3em 0;
    }}
    </style>
</head>
<body>
    <div class="logo">
        <img src="file:///{logo_path_formatted}" alt="Logo" style="max-width: 150px;" />
    </div>
    <div class="store-address">
        {address_str}
    </div>
    <div class="container-wrapper">
        <div class="receipt-wrapper">
        {receipt_text}
        </div>
    </div>
    {bottom_block}
</body>
</html>
"""
    return html_content, fixed_date_time.replace('.', '_').replace(' ', '_').replace(':', '-')

def take_screenshot_of_html(html_content, filename_prefix, width=561, height=1700):
    """Creates a screenshot of the generated HTML receipt from the HTML content."""
    screenshot_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{filename_prefix}.png")
    
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".html", encoding="utf-8") as temp_html_file:
        temp_html_file.write(html_content)
        temp_html_path = temp_html_file.name
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument(f"--window-size={width},{height}")
    
    try:
        # Verwende den vorinstallierten ChromeDriver für Raspberry Pi
        if os.path.exists('/usr/lib/chromium-browser/chromedriver'):
            service = Service('/usr/lib/chromium-browser/chromedriver')
            driver = webdriver.Chrome(service=service, options=chrome_options)
        elif os.path.exists('/usr/bin/chromedriver'):
            service = Service('/usr/bin/chromedriver')
            driver = webdriver.Chrome(service=service, options=chrome_options)
        else:
            # Fallback für den Fall, dass kein ChromeDriver gefunden wird
            raise Exception("ChromeDriver nicht gefunden. Bitte installieren Sie chromium-chromedriver mit 'sudo apt install chromium-chromedriver'")
        
        driver.get("file:///" + temp_html_path.replace('\\', '/'))
        driver.save_screenshot(screenshot_path)
        driver.quit()
    finally:
        # Remove the temporary HTML file after the screenshot
        try:
            os.remove(temp_html_path)
        except:
            pass
    
    return screenshot_path

def generate_receipt_for_date(date_str):
    """Generates a receipt for a single date and returns the path to the image."""
    try:
        receipt_html, filename_prefix = generate_receipt_text(date_str)
        screenshot_path = take_screenshot_of_html(receipt_html, filename_prefix)
        return screenshot_path, None
    except Exception as e:
        return None, str(e)

def generate_receipts_for_period(start_date_str, end_date_str):
    """Generates receipts for the specified period using multithreading."""
    try:
        start_date = datetime.strptime(start_date_str, "%d.%m.%Y")
        end_date = datetime.strptime(end_date_str, "%d.%m.%Y")
    except ValueError:
        raise ValueError("Invalid date. Please use the format DD.MM.YYYY.")
    
    dates_to_generate = [(start_date + timedelta(days=i)).strftime("%d.%m.%Y")
                         for i in range((end_date - start_date).days + 1)]
    
    results = []
    errors = []
    
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(generate_receipt_for_date, date) for date in dates_to_generate]
        for future in as_completed(futures):
            path, error = future.result()
            if error:
                errors.append((dates_to_generate[futures.index(future)], error))
            else:
                results.append(path)
    
    return results, errors

def create_zip_from_files(files):
    """Create a zip file containing the provided list of files."""
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w') as zf:
        for f in files:
            if os.path.exists(f):
                zf.write(f, os.path.basename(f))
    memory_file.seek(0)
    return memory_file

@app.route('/')
def index():
    current_date = datetime.now().strftime("%d.%m.%Y")
    return render_template('index.html', current_date=current_date)

@app.route('/generate_single', methods=['POST'])
def generate_single():
    date_str = request.form.get('date')
    if not date_str:
        flash('Bitte geben Sie ein Datum ein.', 'error')
        return redirect(url_for('index'))
    
    try:
        # Convert date from HTML format (YYYY-MM-DD) to app format (DD.MM.YYYY)
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        formatted_date = date_obj.strftime('%d.%m.%Y')
        
        path, error = generate_receipt_for_date(formatted_date)
        if error:
            flash(f'Fehler bei der Generierung des Kassenzettels: {error}', 'error')
            return redirect(url_for('index'))
        
        filename = os.path.basename(path)
        return render_template('result.html', receipts=[filename], single=True)
    except Exception as e:
        flash(f'Fehler: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/generate_period', methods=['POST'])
def generate_period():
    start_date_str = request.form.get('start_date')
    end_date_str = request.form.get('end_date')
    
    if not start_date_str or not end_date_str:
        flash('Bitte geben Sie Start- und Enddatum ein.', 'error')
        return redirect(url_for('index'))
    
    try:
        # Convert dates from HTML format (YYYY-MM-DD) to app format (DD.MM.YYYY)
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        
        if start_date > end_date:
            flash('Das Startdatum muss vor dem Enddatum liegen.', 'error')
            return redirect(url_for('index'))
        
        delta = end_date - start_date
        if delta.days > 14:
            flash('Der Zeitraum darf maximal 14 Tage betragen.', 'warning')
            end_date = start_date + timedelta(days=14)
        
        paths, errors = generate_receipts_for_period(start_date.strftime('%d.%m.%Y'), end_date.strftime('%d.%m.%Y'))
        
        if errors:
            error_messages = ", ".join([f"{date}: {error}" for date, error in errors])
            flash(f'Einige Kassenzettel konnten nicht generiert werden: {error_messages}', 'warning')
        
        if not paths:
            flash('Es konnten keine Kassenzettel generiert werden.', 'error')
            return redirect(url_for('index'))
        
        filenames = [os.path.basename(path) for path in paths]
        return render_template('result.html', receipts=filenames, single=False)
    except Exception as e:
        flash(f'Fehler: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/generate_selected_days', methods=['POST'])
def generate_selected_days():
    """Generate receipts for selected days of the current month."""
    selected_days = request.form.getlist('selected_days')
    
    if not selected_days:
        flash('Bitte wählen Sie mindestens einen Tag aus.', 'warning')
        return redirect(url_for('index'))
    
    try:
        # Aktuelles Jahr und Monat
        current_date = datetime.now()
        year = current_date.year
        month = current_date.month
        
        # Konvertiere ausgewählte Tage in vollständige Datumsangaben
        formatted_dates = []
        for day_str in selected_days:
            try:
                day = int(day_str)
                # Stelle sicher, dass das Datum gültig ist und nicht in der Zukunft liegt
                date_obj = datetime(year, month, day)
                if date_obj <= current_date:
                    formatted_dates.append(date_obj.strftime('%d.%m.%Y'))
            except ValueError:
                # Ungültiger Tag, überspringen
                continue
        
        if not formatted_dates:
            flash('Keine gültigen Tage ausgewählt.', 'warning')
            return redirect(url_for('index'))
        
        # Sortiere die Daten chronologisch
        formatted_dates.sort(key=lambda x: datetime.strptime(x, '%d.%m.%Y'))
        
        # Generiere Kassenzettel für jedes ausgewählte Datum
        receipt_files = []
        errors = []
        
        for date_str in formatted_dates:
            try:
                path, error = generate_receipt_for_date(date_str)
                if error:
                    errors.append((date_str, error))
                else:
                    filename = os.path.basename(path)
                    receipt_files.append(filename)
            except Exception as e:
                errors.append((date_str, str(e)))
        
        if errors:
            error_messages = ", ".join([f"{date}: {error}" for date, error in errors])
            flash(f'Einige Kassenzettel konnten nicht generiert werden: {error_messages}', 'warning')
        
        if not receipt_files:
            flash('Es konnten keine Kassenzettel generiert werden.', 'error')
            return redirect(url_for('index'))
        
        # Speichere die Liste der generierten Kassenzettel in der Session für den ZIP-Download
        session['receipt_files'] = receipt_files
        
        return render_template('result.html', receipts=receipt_files, single=False)
    
    except Exception as e:
        flash(f'Fehler: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@app.route('/download_all', methods=['POST'])
def download_all():
    filenames = request.form.getlist('receipts')
    
    if not filenames:
        flash('Keine Dateien zum Herunterladen ausgewählt.', 'error')
        return redirect(url_for('index'))
    
    file_paths = [os.path.join(app.config['UPLOAD_FOLDER'], filename) for filename in filenames]
    zip_buffer = create_zip_from_files(file_paths)
    
    return send_file(
        zip_buffer,
        mimetype='application/zip',
        as_attachment=True,
        download_name='kassenbons.zip'
    )

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
