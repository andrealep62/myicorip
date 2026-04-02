# myicorip.py
r"""
WebApp Ordini – VERSIONE UNIFICATA
- Template Jinja: priorità a file su disco (templates/), fallback in memoria
- Ricerca prodotti: MOCK (default) o SQL Server se USE_REAL_DB=1 e pyodbc disponibile
- Pack: min/step/value basati su Pack (0 => fallback a 1 e warning)
- Carrello: memorizza anche pack; pulsante rimozione singolo item
- API scanner: /api/products/by-ean/<ean> (ritorna anche pack)
- Export CSV: separatore ';' e progressivo giornaliero per utente
- Healthcheck: /healthz e /healthz/db
- Avvio: HTTPS se presenti certificati, altrimenti HTTP

.env (esempio):
FLASK_SECRET_KEY=metti-una-chiave-lunga
USE_REAL_DB=0
SQL_SERVER=172.16.0.10\NTS
SQL_DATABASE=ICOSHOP
SQL_USERNAME=sa
SQL_PASSWORD=********
SQL_VIEW=dbo.vw_AND_webappordini_articoli
SQL_DRIVER=ODBC Driver 18 for SQL Server
EXPORT_DIR=exports
PORT=5001
CERT_PATH=certs/127.0.0.1+2.pem
KEY_PATH=certs/127.0.0.1+2-key.pem

Dipendenze principali:
- Flask
- python-dotenv
- pyodbc (opzionale, solo per DB reale)
"""

import os
import csv
from io import StringIO
from datetime import datetime, timedelta
from pathlib import Path
from flask import (
    Flask, request, session, redirect, url_for,
    render_template, make_response, flash, jsonify
)
from werkzeug.middleware.proxy_fix import ProxyFix
from jinja2 import FileSystemLoader

# =========================
# ENV & OPTIONAL pyodbc
# =========================
try:
    from dotenv import load_dotenv  # type: ignore[import]
    load_dotenv()
except Exception:
    pass

try:
    import pyodbc  # type: ignore[import]
    HAS_PYODBC = True
except Exception:
    pyodbc = None
    HAS_PYODBC = False

USE_REAL_DB = os.environ.get("USE_REAL_DB", "0") == "1" and HAS_PYODBC
SQL_SERVER   = os.environ.get("SQL_SERVER", "172.16.0.10\\NTS")
SQL_DATABASE = os.environ.get("SQL_DATABASE", "ICOSHOP")
SQL_USERNAME = os.environ.get("SQL_USERNAME", "sa")
SQL_PASSWORD = os.environ.get("SQL_PASSWORD", "Sipi1Business")
SQL_DRIVER   = os.environ.get("SQL_DRIVER", "ODBC Driver 18 for SQL Server")
SQL_VIEW     = os.environ.get("SQL_VIEW",   "dbo.vw_AND_webappordini_articoli")

# Parametri di cifratura/timeout per ODBC 18 (sicuri per DMZ/lab)
SQL_ENCRYPT  = os.environ.get("SQL_ENCRYPT", "yes")  # yes/no
SQL_TRUST    = os.environ.get("SQL_TRUST_SERVER_CERT", "yes")  # yes/no
SQL_TIMEOUT  = int(os.environ.get("SQL_TIMEOUT", "5"))

# =========================
# APP BASE
# =========================
app = Flask(__name__)

# Questa è la riga fondamentale per gestire il "ponte" con Nginx
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-change-me")
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=30)
# Abilita auto-reload dei template Jinja in sviluppo
app.config['TEMPLATES_AUTO_RELOAD'] = True
try:
    app.jinja_env.auto_reload = True
except Exception:
    pass

def _cart_counts():
    cart = session.get('cart') or {}
    lines = len(cart)
    qty = sum(int(v.get('qty', 0) or 0) for v in cart.values())
    return lines, qty

def _cart_code_set():
    """Ritorna l'insieme dei codici articolo presenti nel carrello (ignorando le note)."""
    cart = session.get('cart') or {}
    codes = set()
    for k, v in cart.items():
        try:
            cod = (v.get('codart') or str(k)).split('||', 1)[0]
        except Exception:
            cod = str(k).split('||', 1)[0]
        if cod:
            codes.add(cod)
    return codes

# Utenti di prova (multi‑utente per test carrelli)
TEST_USERS = {"Andrea": "test", "Alice": "test", "Renato": "test"}
EXPORT_DIR = Path(os.environ.get("EXPORT_DIR", "exports"))
EXPORT_DIR.mkdir(parents=True, exist_ok=True)
# Cartelle per la persistenza del carrello per utente
CARTS_DIR = EXPORT_DIR / "carts"
CARTS_DIR.mkdir(parents=True, exist_ok=True)
# TTL in giorni per considerare scaduti i carrelli persistiti
CART_TTL_DAYS = int(os.environ.get("CART_TTL_DAYS", "20"))

# Percorso opzionale del CSV MOCK (usato quando USE_REAL_DB=0)
MOCK_CSV_PATH = os.environ.get("MOCK_CSV_PATH", "mock_articoli.csv")

# Carica i template esclusivamente dalla cartella fisica templates/
templates_path = str((Path(__file__).parent / "templates").resolve())
app.jinja_loader = FileSystemLoader(templates_path)

# Nascondi le freccie native per i campi numerici su Chrome/Safari
CSS_FIX = """
<style>
  input::-webkit-outer-spin-button,
  input::-webkit-inner-spin-button {
    -webkit-appearance: none;
    margin: 0;
  }
</style>
"""

# Iniettiamo lo stile nel contesto di ogni template
@app.context_processor
def inject_css_fix():
    return dict(css_fix=CSS_FIX)

# =========================
# MOCK (fallback quando DB OFF)
# =========================
MOCK_DATA = [
    {"codart": "A001", "descrizione": "GIOCHIAMO CON I CIBI", "ean13": "9788855063258", "pack": 6},
    {"codart": "B002", "descrizione": "Prodotto Beta",  "ean13": "2345678901234", "pack": 4},
    {"codart": "C003", "descrizione": "Prodotto Gamma", "ean13": "3456789012345", "pack": 2},
    {"codart": "C004", "descrizione": "Prodotto Delta", "ean13": "3456789012388", "pack": 12},
]

# =========================
# DB LAYER
# =========================
def _conn():
    # Connection string con ODBC 18 e opzioni di sicurezza configurabili
    enc = "yes" if str(SQL_ENCRYPT).lower() in ("1","true","yes") else "no"
    trc = "yes" if str(SQL_TRUST).lower()   in ("1","true","yes") else "no"
    conn_str = (
        f"DRIVER={{{SQL_DRIVER}}};"
        f"SERVER={SQL_SERVER};"
        f"DATABASE={SQL_DATABASE};"
        f"UID={SQL_USERNAME};PWD={SQL_PASSWORD};"
        f"Encrypt={enc};TrustServerCertificate={trc};"
        f"Connection Timeout={SQL_TIMEOUT}"
    )
    return pyodbc.connect(conn_str)

# =========================
# LETTORE CSV MOCK (quando il DB è DISATTIVATO)
# =========================
_MOCK_CACHE = {"path": None, "mtime": None, "data": None}

def _resolve_path(p: str) -> Path:
    base = Path(__file__).parent
    path = Path(p)
    return path if path.is_absolute() else (base / path)

def _to_int(val, default=None):
    """Converte valori numerici in interi gestendo formati locali.
    Esempi supportati: "2", "2,0", "2.000", "2.000.000.000", "6,00".
    Utile per colonne come Pack esportate con separatori delle migliaia.
    """
    try:
        if val is None:
            return default
        s = str(val).strip()
        if s == "":
            return default
        # Rimuovi separatori delle migliaia (.) e normalizza la virgola
        s_norm = s.replace('.', '').replace(',', '.')
        return int(float(s_norm))
    except Exception:
        return default

def _norm_key(k: str) -> str:
    k = (k or '').strip().lower()
    aliases = {
        'codice articolo': 'codart', 'codart': 'codart', 'codice': 'codart',
        'descrizione': 'descrizione', 'descr': 'descrizione',
        'ean13': 'ean13', 'ean': 'ean13',
        'pack': 'pack',
        'formato': 'formato',
        'prodotto': 'prodotto',
        'colore': 'colore',
        'gruppo': 'gruppo',
        's_gruppo': 's_gruppo', 'sgruppo': 's_gruppo', 's-gruppo': 's_gruppo',
    }
    return aliases.get(k, k)

def _fix_codart(code: str) -> str:
    """Normalizza il codice articolo sostituendo gli underscore con virgole.
    In alcune esportazioni la virgola è stata transcodificata in '_'.
    """
    try:
        s = str(code or '')
        return s.replace('_', ',')
    except Exception:
        return code

def _parse_formato_value(s: str) -> float:
    """Prova a convertire una stringa Formato in un volume numerico per l'ordinamento.
    Supporta pattern come 'ML750', 'LT2,5', 'LT1', '0,75L', ecc.
    Ritorna litri come float; valori sconosciuti/vuoti ritornano -1.0 (finiscono in fondo in desc).
    """
    try:
        import re
        if s is None:
            return -1.0
        t = str(s).strip().upper().replace(' ', '')
        if not t:
            return -1.0
        # Pattern comuni: unità prima (ML750 / LT2,5) o numero prima (0,75L)
        m = re.match(r"^(ML|LT|L|KG|G)([0-9]+(?:[\.,][0-9]+)?)$", t)
        unit = None
        num = None
        if m:
            unit, num = m.group(1), m.group(2)
        else:
            m = re.match(r"^([0-9]+(?:[\.,][0-9]+)?)(ML|LT|L|KG|G)$", t)
            if m:
                num, unit = m.group(1), m.group(2)
        if unit is None or num is None:
            # Prova numero da solo: tratta come litri (es. '2,5')
            m = re.match(r"^[0-9]+(?:[\.,][0-9]+)?$", t)
            if m:
                return float(t.replace(',', '.'))
            return -1.0
        val = float(num.replace(',', '.'))
        if unit == 'ML':
            return val / 1000.0
        if unit in ('L', 'LT'):
            return val
        # Fallback: tratta KG≈L e G≈ML solo ai fini dell'ordinamento
        if unit == 'KG':
            return val
        if unit == 'G':
            return val / 1000.0
        return -1.0
    except Exception:
        return -1.0

def _derive_from_descr(descr: str):
    """Euristica: prova a derivare prodotto, colore e formato testuale dalla descrizione.
    Esempio: 'NORDICA BIANCO LT14' -> ('NORDICA', 'BIANCO', 'LT14').
    Ritorna una tupla (prodotto, colore, formato_text); se non ricava, usa stringa vuota.
    """
    try:
        import re
        if not descr:
            return ('', '', '')
        d = str(descr).strip().upper()
        # Estrai il formato finale tipo LT2,5 / LT5 / ML750
        m = re.search(r"\s(ML|LT)\s*([0-9]+(?:[\.,][0-9]+)?)$", d)
        fmt_txt = ''
        base = d
        if m:
            fmt_txt = m.group(1) + m.group(2)
            base = d[:m.start()].rstrip()
        parts = base.split()
        if len(parts) >= 2:
            colore = parts[-1]
            prodotto = ' '.join(parts[:-1])
        else:
            prodotto = base
            colore = ''
        return (prodotto, colore, fmt_txt)
    except Exception:
        return ('', '', '')

def load_mock_data():
    """Carica articoli MOCK dal CSV se presente; altrimenti usa i dati interni MOCK_DATA.
    Mantiene una cache in memoria semplice invalidata al variare del mtime del file.
    """
    path = _resolve_path(MOCK_CSV_PATH)
    if not path.exists():
        return MOCK_DATA

    try:
        mtime = path.stat().st_mtime
        if _MOCK_CACHE["path"] == str(path) and _MOCK_CACHE["mtime"] == mtime and _MOCK_CACHE["data"] is not None:
            return _MOCK_CACHE["data"]

        text = path.read_text(encoding='utf-8-sig')
        import csv as _csv
        # Prova a riconoscere il delimitatore tra i più comuni
        try:
            sample = '\n'.join(text.splitlines()[:2])
            dialect = _csv.Sniffer().sniff(sample, delimiters=",;\t")
            delim = dialect.delimiter
        except Exception:
            delim = ','
        reader = _csv.DictReader(text.splitlines(), delimiter=delim)
        rows = []
        for row in reader:
            r = { _norm_key(k): v for k, v in (row or {}).items() }
            item = {
                'codart': _fix_codart((r.get('codart') or '').strip()),
                'descrizione': (r.get('descrizione') or '').strip(),
                'ean13': (str(r.get('ean13') or '').strip()),
                'pack': _to_int(r.get('pack'), 0) or 0,
            }
            # Il formato può essere in 'formato' o 'um'; preferisci 'formato', fallback su 'um'
            fmt = (r.get('formato') or r.get('um') or '')
            if fmt not in (None, ''):
                item['formato'] = str(fmt).strip()
            # Campi opzionali che possiamo usare dopo
            for opt in ('prodotto','colore','gruppo'):
                if r.get(opt) not in (None, ''):
                    item[opt] = str(r.get(opt)).strip()
            sgv = _to_int(r.get('s_gruppo'), None)
            if sgv is not None:
                item['s_gruppo'] = sgv

            # Se mancano, prova a derivarli dalla descrizione (solo come ultima spiaggia)
            if not item.get('formato') or not item.get('prodotto') or not item.get('colore'):
                dprod, dcol, dfmt = _derive_from_descr(item.get('descrizione'))
                if not item.get('prodotto') and dprod:
                    item['prodotto'] = dprod
                if not item.get('colore') and dcol:
                    item['colore'] = dcol
                if not item.get('formato') and dfmt:
                    item['formato'] = dfmt

            if item['codart'] or item['descrizione'] or item['ean13']:
                rows.append(item)

        _MOCK_CACHE.update({"path": str(path), "mtime": mtime, "data": rows})
        return rows
    except Exception:
        return MOCK_DATA

def search_products(q: str):
    q = (q or '').strip()
    if not q:
        return []

    results = []
    if USE_REAL_DB:
        with _conn() as conn:
            cur = conn.cursor()
            if q.isdigit() and len(q) >= 6:
                sql = f"""
                    SELECT TOP 50
                        [Codice Articolo] AS codart,
                        [Descrizione]     AS descrizione,
                        CAST([EAN13] AS VARCHAR(20)) AS ean13,
                        ISNULL(TRY_CONVERT(INT,[Pack]),0) AS pack,
                        -- Campi certi per l'ordinamento: non deriviamo dalla descrizione
                        CAST([Prodotto] AS VARCHAR(255)) AS prodotto,
                        CAST([Colore]   AS VARCHAR(255)) AS colore,
                        CAST([Formato]  AS VARCHAR(50))  AS formato,
                        CAST([UM]       AS VARCHAR(50))  AS um
                    FROM {SQL_VIEW}
                    WHERE CAST([EAN13] AS VARCHAR(20)) = ?
                """
                cur.execute(sql, (q,))
            else:
                # Nei codici articolo la virgola può essere salvata come underscore nella vista
                q_db = q.replace(',', '_')
                like = f"%{q_db}%"
                sql = f"""
                    SELECT TOP 50
                        [Codice Articolo] AS codart,
                        [Descrizione]     AS descrizione,
                        CAST([EAN13] AS VARCHAR(20)) AS ean13,
                        ISNULL(TRY_CONVERT(INT,[Pack]),0) AS pack,
                        -- Campi certi per l'ordinamento: non deriviamo dalla descrizione
                        CAST([Prodotto] AS VARCHAR(255)) AS prodotto,
                        CAST([Colore]   AS VARCHAR(255)) AS colore,
                        CAST([Formato]  AS VARCHAR(50))  AS formato,
                        CAST([UM]       AS VARCHAR(50))  AS um
                    FROM {SQL_VIEW}
                    WHERE [Descrizione] LIKE ? OR [Codice Articolo] LIKE ?
                """
                cur.execute(sql, (like, like))
            rows = cur.fetchall()
            results = [{
                "codart": _fix_codart(r.codart),
                "descrizione": r.descrizione,
                "ean13": (str(r.ean13) if r.ean13 is not None else ""),
                "pack": int(r.pack) if r.pack is not None else 0,
                # Usiamo i campi certi per ordinare; 'formato' cade su 'um' se vuoto
                "prodotto": (str(r.prodotto).strip() if hasattr(r, 'prodotto') and r.prodotto is not None else ""),
                "colore":   (str(r.colore).strip()   if hasattr(r, 'colore')   and r.colore   is not None else ""),
                "formato":  (str(r.formato).strip()  if hasattr(r, 'formato')  and r.formato  not in (None, "") else (str(r.um).strip() if hasattr(r, 'um') and r.um not in (None, "") else "")),
            } for r in rows]
    else:
        # Fallback MOCK (usa CSV se disponibile)
        data = load_mock_data()
        if q.isdigit():
            results = [x for x in data if str(x.get("ean13", "")) == q]
        else:
            ql = q.lower()
            ql_cod = ql.replace('_', ',')
            results = [x for x in data if ql in (x.get("descrizione", "")).lower() or ql_cod in (x.get("codart", "")).lower()]

    # Garantisci i campi per l'ordinamento (deriva solo se mancanti)
    for it in results:
        if not it.get('formato') or not it.get('prodotto') or not it.get('colore'):
            dprod, dcol, dfmt = _derive_from_descr(it.get('descrizione'))
            if not it.get('prodotto') and dprod:
                it['prodotto'] = dprod
            if not it.get('colore') and dcol:
                it['colore'] = dcol
            if not it.get('formato') and dfmt:
                it['formato'] = dfmt

    # Regola di ordinamento: a parità di Prodotto+Colore, ordina Formato in DESC
    def _norm(s):
        return (s or '').strip().lower()

    def _sort_key(item):
        prodotto = _norm(item.get('prodotto'))
        colore   = _norm(item.get('colore'))
        fmt_val  = _parse_formato_value(item.get('formato'))
        return (prodotto, colore, -fmt_val, _norm(item.get('descrizione')), _norm(item.get('codart')))

    results.sort(key=_sort_key)
    return results

@app.get('/api/debug/search')
def debug_search():
    """Strumento di debug: mostra i campi usati per l'ordinamento per una data ricerca.
    Esempio: /api/debug/search?q=nordica
    """
    q = request.args.get('q','')
    data = search_products(q)
    def _s(x):
        return (x or '')
    out = []
    for it in data:
        out.append({
            'codart': _s(it.get('codart')),
            'descrizione': _s(it.get('descrizione')),
            'prodotto': _s(it.get('prodotto')),
            'colore': _s(it.get('colore')),
            'formato': _s(it.get('formato')),
            'fmt_liters': _parse_formato_value(it.get('formato'))
        })
    return jsonify(out)

@app.get('/api/debug/mock')
def debug_mock_info():
    """Mostra informazioni sul CSV mock usato per la ricerca.
    Restituisce percorso risolto, esistenza, intestazioni rilevate e un record esempio.
    """
    info = {}
    try:
        p = _resolve_path(MOCK_CSV_PATH)
        info['resolved_path'] = str(p)
        info['exists'] = p.exists()
        if p.exists():
            info['size_bytes'] = p.stat().st_size
            info['mtime'] = p.stat().st_mtime
            text = p.read_text(encoding='utf-8-sig')
            import csv as _csv
            # Riconosci il delimitatore
            try:
                sample = '\n'.join(text.splitlines()[:2])
                dialect = _csv.Sniffer().sniff(sample, delimiters=",;\t")
                delim = dialect.delimiter
            except Exception:
                delim = ','
            info['delimiter'] = delim
            rdr = _csv.DictReader(text.splitlines(), delimiter=delim)
            info['headers_raw'] = list(rdr.fieldnames or [])
            # Normalizza le intestazioni usando la nostra mappa
            info['headers_norm'] = [_norm_key(h) for h in (rdr.fieldnames or [])]
            # Prima riga di dati
            row = next(iter(rdr), None)
            if row is not None:
                norm = { _norm_key(k): v for k, v in row.items() }
                # Estrai i campi che ci interessano
                sample_item = {
                    'codart': (norm.get('codart') or '').strip(),
                    'descrizione': (norm.get('descrizione') or '').strip(),
                    'ean13': (str(norm.get('ean13') or '').strip()),
                    'formato': (str((norm.get('formato') or norm.get('um') or '')).strip()),
                    'prodotto': (str(norm.get('prodotto') or '').strip()),
                    'colore': (str(norm.get('colore') or '').strip()),
                    'pack': (norm.get('pack') or ''),
                }
                info['first_row_sample'] = sample_item
        else:
            info['note'] = 'File non trovato; verranno usati i dati MOCK interni'
    except Exception as e:
        info['error'] = str(e)
    return jsonify(info)

def db_check_sqlserver():
    """Ritorna (True, None) se SELECT 1 va a buon fine, altrimenti (False, errore)."""
    if not HAS_PYODBC:
        return (False, "pyodbc non installato")
    try:
        with _conn() as cn:
            cur = cn.cursor()
            cur.execute("SELECT 1")
            row = cur.fetchone()
            return (row and row[0] == 1, None)
    except Exception as e:
        return (False, str(e))

# =========================
# UTIL
# =========================
def _get_cart():
    if 'cart' not in session:
        session['cart'] = {}
    return session['cart']

# =========================
# PERSISTENZA CARRELLO (JSON per utente)
# =========================
def _cart_path_for_user(username: str) -> Path:
    safe = ''.join(ch for ch in str(username) if ch.isalnum() or ch in ('.','-','_')) or 'noname'
    return CARTS_DIR / f"{safe}.json"

def load_persisted_cart(username: str) -> dict:
    """Carica il carrello persistito (JSON) per l'utente, oppure {} se mancante/errore."""
    try:
        p = _cart_path_for_user(username)
        if not p.exists():
            return {}
        import json
        data = json.loads(p.read_text(encoding='utf-8'))
        # TTL: se troppo vecchio, considera vuoto e prova a rimuovere
        try:
            ts = data.get('updated_at')
            if ts:
                dt = datetime.fromisoformat(ts)
            else:
                dt = datetime.fromtimestamp(p.stat().st_mtime)
            if datetime.now() - dt > timedelta(days=CART_TTL_DAYS):
                try:
                    p.unlink(missing_ok=True)  # type: ignore[arg-type]
                except Exception:
                    pass
                return {}
        except Exception:
            pass
        items = data.get('items') or {}
        # Garantisce che le quantità siano int
        for k, v in list(items.items()):
            try:
                v['qty'] = int(v.get('qty', 0) or 0)
            except Exception:
                v['qty'] = 0
        return items
    except Exception:
        return {}

def save_persisted_cart(username: str, cart: dict) -> None:
    """Salva il carrello come JSON per l'utente (scrittura atomica)."""
    try:
        import json, tempfile, os as _os
        p = _cart_path_for_user(username)
        nowiso = datetime.now().isoformat(timespec='seconds')
        payload = {
            'version': 1,
            'updated_at': nowiso,
            'items': cart or {}
        }
        tmp_fd, tmp_path = tempfile.mkstemp(prefix='.cart_', suffix='.json', dir=str(CARTS_DIR))
        with _os.fdopen(tmp_fd, 'w', encoding='utf-8') as f:
            json.dump(payload, f, ensure_ascii=False)
        Path(tmp_path).replace(p)
    except Exception:
        # Non bloccare il flusso in caso di problemi IO
        pass

def merge_carts(base: dict, incoming: dict) -> dict:
    """Unisce due carrelli: se un articolo esiste in entrambi, prevale la quantità dell'incoming."""
    result = dict(base or {})
    for k, v in (incoming or {}).items():
        # Invece di sommare, sovrascriviamo o aggiungiamo il nuovo
        result[k] = dict(v)
    return result
 
def load_persisted_cart_meta(username: str):
    """Ritorna (items_dict, updated_at_iso) oppure ({}, None) in caso di errori."""
    try:
        p = _cart_path_for_user(username)
        if not p.exists():
            return {}, None
        import json
        data = json.loads(p.read_text(encoding='utf-8'))
        ts = data.get('updated_at')
        items = data.get('items') or {}
        for k, v in list(items.items()):
            try:
                v['qty'] = int(v.get('qty', 0) or 0)
            except Exception:
                v['qty'] = 0
        return items, ts
    except Exception:
        return {}, None

def _iso_to_dt(s: str):
    try:
        return datetime.fromisoformat(s)
    except Exception:
        return None

def maybe_sync_cart_from_persisted():
    try:
        if 'user' not in session:
            return
        username = session['user']['username']
        persisted_items = load_persisted_cart(username)
        session['cart'] = persisted_items
        session.modified = True
    except Exception:
        pass

# =========================
# MOBILE DETECTION
# =========================
def _is_mobile():
    ua = (request.headers.get('User-Agent') or '').lower()
    # euristica semplice che copre i casi più comuni
    keywords = ['iphone', 'ipad', 'android', 'mobile', 'windows phone']
    return any(k in ua for k in keywords)

# =========================
# ROUTES
# =========================
@app.route('/export')
def export_csv():
    if 'user' not in session:
        return redirect(url_for('login'))
    username = session['user']['username']
    today = datetime.now().strftime('%Y%m%d')
    key = f'prog_{username}_{today}'
    prog = session.get(key, 0) + 1
    session[key] = prog
    session.modified = True
    filename = f"{username}_{today}_{prog:03d}.csv"

    cart = _get_cart()
    rows = []
    for c, i in cart.items():
        # c è la chiave composita: "CODART||NOTE"
        cod = c.split('||', 1)[0]
        # Aggiungiamo 'N' come quinto elemento della riga (Status)
        rows.append([cod, i.get('qty', 0), i.get('descr', ''), (i.get('note','') or ''), 'N'])

    sio = StringIO()
    w = csv.writer(sio, delimiter=';')
    # Aggiunta 'status' nell'intestazione
    w.writerow(['codart','quantita','descrizione','note','status'])
    w.writerows(rows)

    (EXPORT_DIR / filename).write_text(sio.getvalue(), encoding='utf-8')

    # Svuota il carrello dopo l'esportazione
    session['cart'] = {}
    session.modified = True
    try:
        save_persisted_cart(username, {})
    except Exception:
        pass

    resp = make_response(sio.getvalue())
    resp.headers['Content-Disposition'] = f'attachment; filename={filename}'
    resp.headers['Content-Type'] = 'text/csv; charset=utf-8'
    return resp

@app.route('/logout')
def logout():
    session.clear()
    flash('Logout effettuato', 'info')
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # Verifica basata sui TEST_USERS a riga 112 del tuo file
        if username in TEST_USERS and TEST_USERS[username] == password:
            session.permanent = True
            session['user'] = {'username': username}
            flash(f'Benvenuto {username}', 'success')
            return redirect(url_for('home'))
        else:
            flash('Credenziali non valide', 'danger')
    return render_template('login.html', title='Login')

@app.route('/')
def home():
    if 'user' not in session:
        return redirect(url_for('login'))
    maybe_sync_cart_from_persisted()
    return render_template('home.html', title='Ricerca', q=None, results=None, is_mobile=_is_mobile(), codes_in_cart=_cart_code_set())

@app.route('/search', methods=['GET','POST'])
def search():
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Arriva dalla form: salvo la query e faccio PRG → redirect su GET
        q = request.form.get('q','').strip()
        session['last_q'] = q
        return redirect(url_for('search', q=q))

    # GET: prendo dalla querystring o, se manca, dall'ultima ricerca salvata
    q = (request.args.get('q') or session.get('last_q') or '').strip()
    maybe_sync_cart_from_persisted()
    results = search_products(q) if q else []
    return render_template('home.html', title='Ricerca', q=q, results=results, is_mobile=_is_mobile(), codes_in_cart=_cart_code_set())

@app.route('/add', methods=['POST'])
def add_to_cart():
    if 'user' not in session:
        return redirect(url_for('login'))
    codart = request.form.get('codart')
    descr  = request.form.get('descr')
    ean    = request.form.get('ean','')
    note   = (request.form.get('note','') or '').strip().replace('||','|')[:30]
    qty    = int(request.form.get('qty','1') or '1')
    pack   = int(request.form.get('pack','0') or '0')  # fallback 0 per segnalare pack mancante

    cart = _get_cart()
    # Chiave composita: stesso codice ma note diverse devono creare righe distinte
    key = f"{codart}||{note}"
    already = key in cart
    if already:
        cart[key]['qty'] += qty
    else:
        cart[key] = {'codart': codart, 'descr': descr, 'ean': ean, 'qty': qty, 'pack': pack, 'note': note}
    session.modified = True
    # Salva persistenza
    try:
        save_persisted_cart(session['user']['username'], _get_cart())
    except Exception:
        pass

    # Messaggi di conferma rimossi per evitare ridondanza in fase di ricerca

    # Se esiste una ricerca attiva, torna a /search?q=...
    q_last = session.get('last_q')
    if q_last:
        return redirect(url_for('search', q=q_last))
    return redirect(url_for('home'))

@app.route('/cart')
def cart():
    # Forza il caricamento dal server PRIMA di mostrare la pagina
    maybe_sync_cart_from_persisted() 
    return render_template('cart.html', title='Ordine', cart=_get_cart())

@app.route('/update', methods=['POST'])
def update_cart():
    # Aggiorna quantità e note; se la nota cambia, unifica righe con stessa chiave (codice+nota)
    cart = _get_cart()
    new_cart = {}
    for key, item in list(cart.items()):
        # Leggi nuova quantità
        newq_raw = request.form.get(f'qty_{key}')
        try:
            newq = int(newq_raw) if newq_raw is not None else int(item.get('qty', 0) or 0)
        except Exception:
            newq = int(item.get('qty', 0) or 0)
        if newq <= 0:
            continue  # riga eliminata

        # Leggi nuova nota (può essere assente → usa la precedente)
        new_note = request.form.get(f'note_{key}')
        if new_note is None:
            new_note = item.get('note', '')
        new_note = (new_note or '').strip().replace('||', '|')[:30]

        # Determina codice puro e nuova chiave composita
        cod_puro = (item.get('codart') or str(key).split('||', 1)[0])
        new_key = f"{cod_puro}||{new_note}"

        # Unisci se già presente una riga identica
        if new_key in new_cart:
            new_cart[new_key]['qty'] += newq
        else:
            clone = dict(item)
            clone['qty'] = newq
            clone['note'] = new_note
            clone['codart'] = cod_puro
            new_cart[new_key] = clone

    session['cart'] = new_cart
    session.modified = True
    try:
        save_persisted_cart(session['user']['username'], new_cart)
    except Exception:
        pass
    flash('Ordine aggiornato', 'success')
    return redirect(url_for('cart'))

@app.route('/clear')
def clear_cart():
    session.pop('cart', None)
    flash('Ordine svuotato', 'info')
    try:
        if 'user' in session:
            save_persisted_cart(session['user']['username'], {})
    except Exception:
        pass
    return redirect(url_for('home'))

@app.route('/remove', methods=['POST'])
def remove_item():
    cart = _get_cart()
    codart = request.form.get('codart')
    if codart:
        item = cart.get(codart)  # <— prendo i dati prima di rimuovere
        descr = item.get('descr') if item else ''
        cart.pop(codart, None)
        session.modified = True
        if descr:
            flash(f'Rimosso {codart} — {descr}', 'info')
        else:
            flash(f'Rimosso {codart}', 'info')
    try:
        save_persisted_cart(session['user']['username'], _get_cart())
    except Exception:
        pass
    return redirect(url_for('cart'))

@app.route('/scan')
def scan():
    # Usa templates/scan.html se presente sul disco; altrimenti crea tu il file.
    lines, qty = _cart_counts()
    resp = make_response(render_template('scan.html', title='Scanner EAN', cart_lines=lines, cart_qty=qty))
    # Evita cache del browser per vedere subito le modifiche ai template
    resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0, private'
    resp.headers['Pragma'] = 'no-cache'
    resp.headers['Expires'] = '0'
    return resp

@app.post('/api/cart/add')
def api_cart_add():
    if 'user' not in session:
        return jsonify({"ok": False, "error": "UNAUTHORIZED"}), 401
    codart = request.form.get('codart')
    descr  = request.form.get('descr')
    ean    = request.form.get('ean','')
    note   = (request.form.get('note','') or '').strip().replace('||','|')[:30]
    try:
        qty    = int(request.form.get('qty','1') or '1')
    except ValueError:
        qty = 1
    try:
        pack   = int(request.form.get('pack','0') or '0')
    except ValueError:
        pack = 0

    cart = _get_cart()
    key = f"{codart}||{note}"
    already = key in cart
    if already:
        cart[key]['qty'] += qty
    else:
        cart[key] = {'codart': codart, 'descr': descr, 'ean': ean, 'qty': qty, 'pack': pack, 'note': note}
    session.modified = True
    try:
        save_persisted_cart(session['user']['username'], _get_cart())
    except Exception:
        pass

    lines, total_qty = _cart_counts()
    return jsonify({
        "ok": True,
        "codart": codart,
        "qty_added": qty,
        "already": already,
        "cart_lines": lines,
        "cart_qty": total_qty
    })

@app.get("/api/products/by-ean/<ean>")
def api_get_by_ean(ean):
    """Endpoint per lo scanner: ritorna anche pack (0 se mancante)
    e i campi certi per l'ordinamento (prodotto, colore, formato).
    """
    if USE_REAL_DB:
        with _conn() as conn:
            cur = conn.cursor()
            sql = f"""
                SELECT TOP 1
                    [Codice Articolo] AS codart,
                    [Descrizione]     AS descrizione,
                    CAST([EAN13] AS VARCHAR(20)) AS ean13,
                    ISNULL(TRY_CONVERT(INT,[Pack]),0) AS pack,
                    CAST([Prodotto] AS VARCHAR(255)) AS prodotto,
                    CAST([Colore]   AS VARCHAR(255)) AS colore,
                    CAST([Formato]  AS VARCHAR(50))  AS formato,
                    CAST([UM]       AS VARCHAR(50))  AS um
                FROM {SQL_VIEW}
                WHERE CAST([EAN13] AS VARCHAR(20)) = ?
            """
            cur.execute(sql, (ean,))
            r = cur.fetchone()
            if not r:
                return jsonify({"code":"NOT_FOUND","message":"Articolo non trovato"}), 404
            return jsonify({
                "codart": _fix_codart(r.codart),
                "descrizione": r.descrizione,
                "ean": str(r.ean13) if r.ean13 else "",
                "pack": int(r.pack) if r.pack is not None else 0,
                "prodotto": (str(r.prodotto).strip() if hasattr(r, 'prodotto') and r.prodotto is not None else ""),
                "colore":   (str(r.colore).strip()   if hasattr(r, 'colore')   and r.colore   is not None else ""),
                "formato":  (str(r.formato).strip()  if hasattr(r, 'formato')  and r.formato  not in (None, "") else (str(r.um).strip() if hasattr(r, 'um') and r.um not in (None, "") else ""))
            })
    # Fallback MOCK: usa i dati da CSV se possibile (altrimenti MOCK_DATA)
    m = next((x for x in load_mock_data() if str(x.get("ean13","")) == str(ean)), None)
    if not m:
        return jsonify({"code":"NOT_FOUND","message":"Articolo non trovato"}), 404
    return jsonify({
        "codart": _fix_codart(m.get("codart","")),
        "descrizione": m.get("descrizione",""),
        "ean": m.get("ean13",""),
        "pack": int(m.get("pack",0) or 0),
        "prodotto": m.get("prodotto") or _derive_from_descr(m.get("descrizione"))[0],
        "colore":   m.get("colore")   or _derive_from_descr(m.get("descrizione"))[1],
        "formato":  (m.get("formato") or m.get("um") or _derive_from_descr(m.get("descrizione"))[2])
    })

@app.get("/healthz")
def healthz():
    return "OK", 200

@app.get("/healthz/db")
def healthz_db():
    ok, err = db_check_sqlserver()
    if ok:
        return jsonify({"db": "ok"}), 200
    return jsonify({"db": "fail", "error": err}), 500

# =========================
# AVVIO SERVER
# =========================
if __name__ == '__main__':
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "5001"))

    # HTTPS se trovati certs (da env o default in cartella certs/)
    cert_path = os.environ.get("CERT_PATH", "certs/127.0.0.1+2.pem")
    key_path  = os.environ.get("KEY_PATH",  "certs/127.0.0.1+2-key.pem")
    use_ssl = Path(cert_path).exists() and Path(key_path).exists()

    #if use_ssl:
    #    app.run(host=host, port=port, debug=True, ssl_context=(cert_path, key_path))
    #else:
app.run(host=host, port=port, debug=True)
  