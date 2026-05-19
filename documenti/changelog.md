# CHANGELOG — MyIcorip

---

## 19/05/2026 — Vista articoli: tracciato completo

- Aggiunta query SQL `documenti/vista articoli.sql` per generare il CSV mock da SSMS
- Esteso tracciato: Pack (INT), Prodotto, Colore (da tabhhca), Formato, Gruppo, S_Gruppo, cod_catalogo, desc_catalogo (da tabhhcg)
- Cast tipi numerici: Pack e Dispnetta come INT, pesotassabile/Prezzo/PrezzoNoIva/Iva come DECIMAL(10,2)
- Aggiornato `mock_articoli.csv` con il tracciato completo

---

## 19/05/2026 — Dashboard e CSV export

- Dashboard: bottone "NOTA SPESE" rinominato in "ARCHIVIO ORDINI" (icona `clock-history`); visibile a tutti gli utenti incluso Sinergia
- CSV export ordini: tracciato ridotto a 2 colonne `codart;quantita` (rimossi descrizione, note, status)

---

## 02/04/2026 — Sincronizzazione, Refactoring e UX

- Implementata funzione `maybe_sync_cart_from_persisted()` — il carrello viene ricaricato dal server a ogni accesso a `/cart`
- Aggiunto tasto manuale "Sincronizza" nella navbar
- Refactoring templates: rimossi tutti i template HTML inline da `myicorip.py` (~150 righe); configurato `FileSystemLoader` per usare esclusivamente la cartella `templates/`
- Carrello: inseriti tasti [+] e [-] laterali per la quantità, con rispetto dello step (confezione)
- Carrello: risolto bug grafico cestini fuori tabella; allineamento verticale `align-middle`
- Nascondere freccine native del browser tramite CSS `webkit-spin-button`
- Tasto "Continua acquisti" rinominato in "Aggiungi altri articoli"
- Implementata memoria dell'ultima ricerca: tornando dal carrello i risultati precedenti vengono ripristinati
- Ampliato `TEST_USERS`: aggiunti Roberto, Samantha, Sinergia
- Confermata separazione carrelli per utente tramite cartelle dedicate in `EXPORT_DIR/carts/`

---

## 01/04/2026 — Produzione stabile

Dominio: `myicorip.solverstudio.cloud`

- Architettura reverse proxy a tre livelli: Cloudflare (Full Strict) → Nginx (443) → Gunicorn/Flask (5001)
- Nginx: blocco porta 80 con redirect 301 verso HTTPS; blocco porta 443 con certificati Let's Encrypt
- Header `X-Forwarded-Proto: https` e `X-Forwarded-For` configurati per integrità sessioni
- Aggiunto middleware `ProxyFix` di Werkzeug in `myicorip.py` per gestione HTTPS dietro proxy
- Fotocamera scanner funzionante da mobile

---

## 31/03/2026 — Configurazione Nginx su VPS Hostinger

- Configurazione spostata da `sites-available` a `/etc/nginx/nginx.conf` per evitare conflitti
- `server_name _;` universale, `default_server` su porta 80
- Proxy pass verso `127.0.0.1:5001`
- Permessi `/root` sbloccati con `chmod 755`
- Header `X-Forwarded-Proto: https` configurato per Cloudflare
- Testate modalità SSL Flexible e Full; cache Cloudflare svuotata

---

## 28/03/2026 — Ripresa del progetto dopo periodo di inattività

- Rigenerato ambiente virtuale `.venv_mac` su MacBook Air M2; risolti conflitti Flask e pyodbc
- File `.env` configurato per switch MOCK/DB reale (sviluppo fuori ufficio senza errori di connessione)
- Funzione di esportazione ordini aggiornata: colonna `status` valorizzata a `N` per compatibilità importazione gestionale Icosan
- Avviata analisi migrazione su VPS Hostinger per fase beta pubblica
- Prima diagnosi deploy: porta 5001 aperta, app in timeout — strategia Nginx + Gunicorn definita

---

## 19/09/2025 — Configurazione ambiente macOS

- Percorso progetto definito: `/Users/andrea/Progetti/myicorip`
- Virtualenv: `source .venv_mac/bin/activate`

---

## 16/09/2025 — Aggiornamento vista SQL Server

- Rigenerata la vista `vw_AND_webappordini_articoli` su `[ICOSHOP]` puntando al server di produzione `[192.168.0.226].[ICORIP]`
- Tutti i campi necessari ora esposti sia in produzione che in MOCK

---

## 14/09/2025 — Branding, persistenza e UX carrello

- Badge "In ordine" arancione, allineato a destra nella colonna Descrizione
- Controlli quantità -/+ e bottone "Ordina" inline; campo qty compatto (48px), solo interi, max 999
- Intestazioni risultati: header esterno sticky con larghezze coerenti (Codice 140px, Note 160px, Q.tà 220px)
- Riconversione `_` → `,` nei codici articolo in UI, export, API e ricerca; LIKE DB adeguato
- Bottone "Invia Ordine" (ex "Esporta CSV"): download CSV in background, carrello svuotato lato server, modale "Ordine Inviato" con bottone "Continua"
- App rinominata in "MyIcorip"; logo aziendale in `static/logo.png` su tutte le pagine
- Aggiunti utenti di prova "Andrea" e "Alice" (password: `test`) per test multi-device
- Persistenza carrello su file JSON per utente con TTL 20 giorni (`CART_TTL_DAYS`) e merge automatico al login
- Sincronizzazione multi-sessione via refresh: merge basato su `updated_at` vs `cart_synced_at`

---

## 12/09/2025 — UI ricerca B2B, logica carrello e normalizzazione dati

- Ordinamento articoli via campi certi Prodotto → Colore → Formato (discendente); derivazione dalla descrizione solo come fallback
- Query DB aggiornate: SELECT include Prodotto, Colore, Formato, UM anche nell'endpoint scanner barcode
- Ricerca: rimossa colonna EAN13; aggiunta colonna Note e controlli -/+; badge "In ordine" verde
- Testata risultati sticky (Codice, Descrizione, Note, Q.tà) allineata con i dati
- Carrello: logica chiave composita `codice||nota` — stessa nota si somma, note diverse creano righe separate; unione automatica se due righe diventano uguali
- Export CSV: colonne `codart;quantita;descrizione;note`; codice esportato puro (senza nota)
- Normalizzazione codici articolo con virgola: funzione `_fix_codart()` converte `_` → `,` a runtime
- Rimossi messaggi flash ridondanti ("Aggiunto…" / "Articolo già in ordine…")
- Note: max 30 caratteri, sanificate (niente `||`), placeholder rimosso
- Script `normalize_mock_csv.py`: decimali con punto, pack come intero, NULL→vuoto

---

## 10/09/2025 — Scanner EAN e UX generale

- Debug Flask attivo, auto-reload template ON
- Scanner: rimosso titolo e messaggio "Scanner attivo"; messaggi errore auto-puliti
- Lettura EAN: beep opzionale; stop immediato dopo lettura valida; bottone "Riprendi"
- Aggiunta articolo via AJAX su `/api/cart/add`; badge conteggio navbar aggiornato
- Dopo aggiunta: box nascosto e scanner riparte automaticamente
- Warning pack solo quando `pack=0`
- Terminologia: "Carrello" → "Ordine" in tutta l'app
- Dati MOCK: ora presi dal CSV reale ICORIP (vista esportata) anziché dati fittizi

---

## 09/09/2025 — Query articoli — nuovi campi

- Aggiunti alla query della vista: `Prodotto`, `Colore`, `Formato` per ordinamento per formato decrescente
- Aggiunto campo `Gruppo` per macro ricerche rapide (scorciatoie)
- Aggiunto campo `S_Gruppo` per switch categorie: Bianchi (1) / Basi_edi (2) / Convertitori industria (3) / Trasparenti inc (6)
