# MyIcorip — Log di progetto

---

## GitHub: come lavorare con il repo privato

**Clona il progetto** (solo la prima volta su un nuovo PC):

```bash
git clone https://github.com/andrealep62/myicorip.git myicorip
cd myicorip
```

**Aggiorna il codice** (ogni volta che riapri per lavorare):

```bash
git pull
```

**Salva modifiche locali:**

```bash
git add .
git commit -m "Descrizione breve della modifica"
```

**Invia modifiche su GitHub:**

```bash
git push
```

### Note importanti

- Il file `.env` NON va mai su Git (è escluso da `.gitignore`).
- Copia manualmente l'`.env` da backup nella cartella `myicorip` su ogni PC nuovo.
- Per vedere lo stato dei file: `git status`
- Se appare la richiesta di password, usa il **TOKEN GitHub** (non la password dell'account).

---

## Riattivare l'ambiente myicorip

Ogni volta che apri un nuovo terminale lancia questi comandi:

**Sul Mac:**

```bash
cd /Users/andrea/Progetti/myicorip
source .venv_mac/bin/activate
```

**Sul PC:**

```bash
cd Progetti/myicorip
```

**Avvia l'app:**

```bash
python myicorip.py
```

### Accessi all'app

| Dove | URL | Utente | Password |
|---|---|---|---|
| In ufficio (DB reale) | `https://192.168.0.41:5001` | Andrea / Alice | test |
| Da casa su Mac (MOCK) | `https://127.0.0.1:5001` | Andrea / Alice | test |

### Note ambiente

- Se vedi il prompt che inizia con `(myicorip)`, l'ambiente è attivo.
- Il server parte sulla porta definita nel file `.env` (attualmente `5001`).
- Per uscire dal venv: `deactivate`

### MOCK vs DB reale

Nel file `.env` modifica la riga `USE_REAL_DB`:

| Valore | Comportamento |
|---|---|
| `USE_REAL_DB=0` | Usa dati di test (MOCK) dal CSV preso dalla vista |
| `USE_REAL_DB=1` | Usa il DB reale (solo in ufficio, rete LAN disponibile) |

---

## Log delle lavorazioni

### 09/09/2025

Inseriti nella query della vista articoli i campi:

- **Prodotto, Colore, Formato** — per ordinare meglio gli articoli dello stesso prodotto e stesso colore secondo formati decrescenti.
- **Gruppo** — per fare delle macro search con un click, tipo scorciatoie.
- **S_Gruppo** — per fare uno switch per filtrare Bianchi (1) / Basi_edi (2) / Convertitori industria (3) / Trasparenti inc (6), come pacchetto prodotti per facilitare un tintometrista.

---

### 10/09/2025 — Stato attuale (scanner e UI)

- Debug Flask attivo, auto-reload template ON.
- Pagina scanner: rimosso titolo; niente "Scanner attivo"; messaggi errore ripuliti automaticamente.
- Lettura EAN: beep opzionale; stop immediato dopo lettura valida; bottone mostra "Riprendi".
- Aggiungi all'ordine: via AJAX su `/api/cart/add`, badge conteggio in alto a destra aggiornato.
- Dopo Aggiungi: nasconde il box e lo scanner riparte automaticamente.
- Info pack: mostra solo warning quando `pack=0`.
- Terminologia: "Carrello" sostituito con "Ordine" in tutta l'app.
- I dati Mock vengono presi dal CSV articoli di ICORIP (risultato stampato in ufficio della vista) in modo da avere comunque dati reali; i fittizi sono rimasti nel codice `myicorip.py`.

---

### 12/09/2025 — Log lavorazioni principali

- **Ordinamento articoli**: ora usa i campi certi Prodotto, Colore e Formato (discendente). Niente più deduzioni dalla descrizione, salvo come ultima spiaggia quando i campi non sono presenti.
- **Query DB aggiornate**: SELECT include anche Prodotto, Colore, Formato, UM; stessa cosa nell'endpoint scanner per barcode.
- **UI ricerca (B2B style)**:
  - Rimossa colonna EAN13; aggiunta colonna Note (input) e controlli quantità con bottoni −/+ e pulsante "Ordina".
  - Quantità: interi, max 3 cifre, rispetta pack come min/step, campo compatto.
  - Evidenziazione: le righe già in ordine sono verdi e mostrano badge "In ordine".
  - Testata risultati fissa: creata intestazione esterna sticky (Codice, Descrizione, Note, Q.tà) allineata con i dati; rimosse sovrapposizioni e spazio inutile.
- **Carrello**:
  - Rimossa colonna EAN; aggiunta colonna Note editabile.
  - Logica righe: chiave "codice + nota". Stesso codice e stessa nota si sommano; note diverse creano righe separate. In aggiornamento, se due righe diventano uguali, vengono unite sommando le quantità.
  - Bottone "Aggiorna quantità" rinominato in "Aggiorna".
- **Esportazione ordine**: CSV con colonne `"codart; quantita; descrizione; note"`. Il codice esportato è quello puro (senza la nota nella chiave).
- **Codici articolo con virgola**: normalizzazione a monte. Ovunque a video e negli export i codici mostrano la virgola (la vista/CSV che usa `_` viene riconvertita). La ricerca gestisce entrambi i casi.
- **Messaggi ridondanti**: rimossi i flash "Aggiunto… / Articolo già in ordine…" in fase di aggiunta dalla ricerca.
- **Note**: lunghezza massima 30 caratteri, sanificate (niente `||`), placeholder tolto sia in ricerca sia in carrello.
- **CSV articoli normalizzato**: script dedicato per sovrascrivere `mock_articoli.csv` (decimali col punto, pack come intero, NULL→vuoto). Il runtime gestisce comunque i formati locali.

> Commenti e testi nel codice sono stati portati in italiano nelle parti modificate.

---

### 14/09/2025 — Log aggiornamenti recenti

- **Badge "In ordine"**: arancione e allineato a destra nella colonna Descrizione.
- **Riga articoli**: controlli quantità con pulsanti -/+ e bottone "Ordina" inline; qty compatta (48px), solo interi, max 999; campo Note senza placeholder.
- **Intestazioni risultati**: header esterno sticky allineato con i dati; rimosso spazio eccessivo; larghezze coerenti (Codice 140px, Note 160px, Q.tà 220px).
- **Codici articolo**: riconversione `_` → `,` in UI, export, API e ricerca; LIKE DB adeguato.
- **Invio ordine**: bottone "Invia Ordine" (ex "Esporta CSV"); download CSV in background; carrello svuotato lato server; modale centrale "Ordine Inviato" con bottone "Continua" che torna alla Ricerca.
- **Carrello**: Note senza placeholder.
- **Branding**: rinominata l'app in "MyIcorip"; logo aziendale in alto a sinistra (file atteso: `static/logo.png`) su Ricerca, Ordine, Login e Scanner.
- **Utenti di prova**: aggiunti account "Andrea" e "Alice" (password: `test`) per verificare carrelli separati multi-device.
- **Persistenza carrello**: su file JSON per utente con TTL 20 giorni (`CART_TTL_DAYS`) e merge automatico al login.
- **Sincronizzazione multi-sessione**: con un semplice refresh su Ricerca/Ordine il carrello si allinea agli aggiornamenti fatti da altri device (merge basato su `updated_at` vs `cart_synced_at`).

---

### 16/09/2025 — Aggiornamento vista DMZ

Aggiornata la vista `vw_AND_webappordini_articoli` rigenerandola da produzione:

```sql
USE [ICOSHOP];
GO

DROP VIEW IF EXISTS [dbo].[vw_AND_webappordini_articoli];
GO

CREATE VIEW [dbo].[vw_AND_webappordini_articoli] AS
SELECT *
FROM [192.168.0.226].[ICORIP].[dbo].[vw_AND_webappordini_articoli];
GO
```

> I server produzione e mock ora espongono tutti i campi necessari; per cambiare la provenienza dati usare `REAL_DB=1/0` nel file `.env`.

---

### 19/09/2025 — Configurazione macOS

- Percorso progetto: `/Users/andrea/Progetti/myicorip`
- Virtualenv: `source .venv_mac/bin/activate`

---

### 28/03/2026 — Ripresa del progetto

Dopo lungo periodo di inattività riprendo il progetto per presentarlo e farlo provare.

**Attività svolte:**

- **Ripristino Ambiente di Sviluppo**: rigenerato l'ambiente virtuale (`.venv_mac`) su MacBook Air M2. Risolti i conflitti di librerie (Flask, pyodbc) e configurato correttamente l'interprete Python in VS Code.
- **Configurazione Ibrida Locale/Cloud**: configurato il file `.env` per permettere lo switch tra database reale (SQL Server aziendale via DMZ/VPN) e database simulato (MOCK tramite file CSV).
- **Implementazione Logica Gestionale (Status N)**: aggiornata la funzione di esportazione ordini. Il file CSV generato ora include la colonna `"status"` valorizzata a `"N"` per la compatibilità con l'importazione automatica del gestionale Icosan.
- **Analisi Infrastruttura VPS**: valutata la migrazione su VPS Hostinger (Linux) per test beta pubblici. Obiettivo: sfruttare le tabelle database del VPS (limite 50MB) per rendere l'app accessibile agli agenti via mobile.

**Analisi strategica — visione futura:**

L'applicazione si evolverà in una piattaforma con gestione differenziata degli accessi basata sul profilo utente:

| Profilo | Funzione | Workflow |
|---|---|---|
| **Agente / Ufficio commerciale** (interno) | "Invia ordine per conto di" | Login → Dashboard Agente → Selezione Cliente → Inserimento ordine |
| **Cliente diretto** (esterno) | Autogestione ordini | Login → Dashboard Cliente (catalogo e storico personale) → Invio ordine diretto |

Il sistema non sarà solo un "prendi-ordini", ma una piattaforma più ampia che comprenderà consultazione dati, documenti e statistiche.

**Prossimi step operativi:**

1. Implementazione dello "Split Login": logica che riconosce il tipo di utente e apre la dashboard corretta.
2. Creazione anagrafica relazionale: file `clienti_mock.csv` per mappare l'associazione tra ogni agente e i suoi specifici clienti.
3. Miglioramento UI Carrello: inserimento tasti +/- per gestione quantità rapida.
4. Test di Deploy su VPS Hostinger per l'avvio della fase Beta.

**Fine giornata — Deploy su Hostinger:**

- **Diagnosi**: Porta 5001 aperta con successo. L'applicazione riceve la chiamata ma non invia dati (timeout interno).
- **Causa probabile**: L'app si blocca nel tentativo di inizializzare componenti (DB o percorsi file) non presenti sul server.
- **Strategia**: Migrazione a stack **Nginx + Gunicorn** per garantire stabilità e compatibilità mobile.

---

### 31/03/2026 — Configurazione Nginx su VPS

- **Configurazione Nginx**: spostata la configurazione dal file `sites-available` direttamente nel cuore di `/etc/nginx/nginx.conf` per evitare conflitti con file predefiniti.
- **Server Block**: impostato `server_name _;` (universale) e configurato come `default_server` sulla porta 80.
- **Proxy Pass**: collegato Nginx all'app Flask su `127.0.0.1:5001`.
- **Permessi cartella**: sbloccati i permessi di `/root` con `chmod 755`.
- **Headers di sicurezza**: configurato il protocollo `X-Forwarded-Proto: https` per Cloudflare.
- **Debug Cloudflare**: testate le modalità SSL Flexible e Full e svuotata la cache ("Purge Everything").

> Problema: page not found persiste su `https://myicorip.solverstudio.cloud/login`.

---

### 01/04/2026 — Produzione / Stabile

**Dominio:** `myicorip.solverstudio.cloud`

#### 1. Architettura del sistema (Reverse Proxy a tre livelli)

| Livello | Componente | Ruolo |
|---|---|---|
| Edge | **Cloudflare** | DNS + protezione SSL (Modalità: Full Strict) |
| Web Server | **Nginx** | Ricezione su porta 443, gestione certificati SSL, forward a Flask |
| App | **Gunicorn/Flask** | Applicazione Python su porta 5001 |

#### 2. Configurazione Nginx (`/etc/nginx/nginx.conf`)

- **Blocco Porta 80**: redirect 301 permanente verso HTTPS.
- **Blocco Porta 443**:
  - Certificati emessi da Certbot (Let's Encrypt).
  - Traffico inoltrato a `http://127.0.0.1:5001`.
  - Header `X-Forwarded-Proto: https` e `X-Forwarded-For` per integrità dei dati utente.

#### 3. Gestione del servizio (systemd)

File: `/etc/systemd/system/myicorip.service`

```bash
sudo systemctl restart myicorip   # aggiornare dopo un git pull
sudo systemctl status myicorip    # verificare che sia "active"
journalctl -u myicorip -f         # vedere i log dell'app in tempo reale
```

#### 4. Modifiche al codice (`myicorip.py`)

Aggiunto il middleware `ProxyFix` di Werkzeug:

```python
from werkzeug.middleware.proxy_fix import ProxyFix
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
```

> Da cellulare la fotocamera funziona. Da migliorare la UX per l'aggiunta articoli.

---

### 02/04/2026 — Sincronizzazione, Refactoring e UX

- **Sincronizzazione cloud**: implementata funzione `maybe_sync_cart_from_persisted()`. Il carrello viene ricaricato dal server a ogni accesso alla pagina `/cart`. Aggiunto tasto manuale "Sincronizza" nella navbar.
- **Refactoring templates**: rimossi tutti i template HTML dal file `myicorip.py` (~150 righe eliminate). Configurato `FileSystemLoader` per usare esclusivamente la cartella fisica `templates/`.
- **Miglioramento UX Carrello**:
  - Inseriti tasti [+] e [-] laterali per la quantità.
  - I tasti rispettano lo step (confezione) dell'articolo.
  - Nascondere freccine native del browser tramite CSS `webkit-spin-button`.
  - Sistemato bug grafico dei cestini (icone rimozione) fuori tabella.
  - Allineamento verticale `align-middle` per una lettura più pulita della riga.
- **Navigazione**: tasto "Continua acquisti" rinominato in "Aggiungi altri articoli". Implementata memoria dell'ultima ricerca.
- **Multi-utente**: ampliato dizionario `TEST_USERS` (aggiunti Roberto, Samantha, Sinergia). Confermata separazione dei carrelli tramite cartelle dedicate in `EXPORT_DIR/carts/`.

---

## TODO — Fine sviluppo (per produzione)

Da completare quando il progetto verrà approvato e finanziato:

- [ ] Migrazione a DB per persistenza/storico: tabelle `OrdersCart`/`OrdersCartItem` e storico ordini + clienti; sostituire il salvataggio JSON con upsert/select su SQL Server. Prevedere anche storico ordini inviati.
- [ ] Reimpostare `debug=False` in `myicorip.py` (`app.run`).
- [ ] Disattivare/condizionare `TEMPLATES_AUTO_RELOAD` (usare `FLASK_DEBUG`).
- [ ] Riavviare il server per applicare le impostazioni.

---

## Task

### A breve/medio termine

- [ ] Allineare il layout del carrello alla search (colonna quantità con i + e -).
- [ ] Ottimizzare UI da tablet e telefono con i +/- pack e lo scanner impreciso.
- [ ] Aggiungere il campo NOTE generali di ordine nel carrello in Testata.
- [ ] Aggiungere un campo nell'output CSV `Status` valorizzato sempre ad `N` (serve al gestionale per rilevare gli ordini da importare).
- [ ] Impostare uno switch per tutti gli articoli (per sostituire la magagna del CSV).
- [ ] Impostare le macro categorie con bottoni secondo i gruppi.
- [ ] Impostare ARCHIVIO ORDINI per utente (id_ord interno?).
- [ ] Creare una HOME di piattaforma friendly con dashboard: bottoni grossi (ORDINA / ARCHIVIO ORDINI / CATALOGO / ANAGRAFICA / STATISTICHE).
- [ ] Gestione anagrafiche Clienti/Agenti:
  - Tipologie e gruppi per gestire Agenti che inviano ordini per conto di...
  - Uso clienti che possano vedere i propri listini privatamente.
- [ ] Definire il logo MyIcorip.

### A lungo termine

- [ ] Integrazione tracking ordini dei corrieri.
- [ ] Chatbot AI interno (OpenAI) per risposte rapide ai clienti, eventualmente addestrato su consigli tecnici.
- [ ] Statistiche in dashboard.
- [ ] Situazione finanziaria.

---

## Snippet utili (copia/incolla veloce)

**Logo aziendale in alto a sinistra:**
- Mettere il logo in `static/logo.png` (altezza consigliata 28–32 px).

**Aggiungere un utente di prova (`myicorip.py`):**

```python
TEST_USERS = {"Andrea": "test", "Alice": "test", "Marco": "test"}
```

**Modificare TTL di salvataggio carrello (default 20 giorni):**

```bash
# macOS/Linux
export CART_TTL_DAYS=30
```

```powershell
# Windows PowerShell
$env:CART_TTL_DAYS = "30"
```

**Dove vengono salvati i carrelli per utente:**

```
exports/carts/<utente>.json   (salvataggio/merge automatici al login e alle modifiche)
```
