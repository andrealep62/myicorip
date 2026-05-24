# MyIcorip — Contesto Progetto

## Cos'è

Piattaforma web B2B per **Icorip Web** (40 dipendenti, ~9M€ fatturato).

Nata come sistema di inserimento ordini, deve evolvere in piattaforma completa per:
- Venditori e agenti in mobilità
- Clienti (tracking, consultazione, supporto)
- Gestione interna aziendale
- Espansione futura (analytics, workflow, automazioni)

**Obiettivo finale:** prodotto affidabile, scalabile, manutenibile — qualità software house.

---

## Dimensione commerciale (priorità strategica)

MyIcorip è il **primo prodotto commerciale di SolverStudio Lab** e la seconda fonte di reddito di Andrea.

Il progetto ha una doppia pista parallela:

| Pista | Obiettivo |
|---|---|
| **Sviluppo tecnico** | Costruire un MVP solido e production-ready |
| **Vendita ad Icorip** | Proporre formalmente il prodotto all'azienda come servizio continuativo |

Andrea deve preparare:
- Proposta commerciale per Icorip Web
- Strategia di pricing (licenza? canone mensile? manutenzione?)
- Presentazione del valore: risparmio tempo, errori ordini, mobilità agenti
- Piano di adozione interno

**Nota:** Andrea lavora per EPTAGON che ha Icorip tra i clienti — il rapporto esiste, ma la vendita di MyIcorip è una trattativa separata e personale.

---

## Stack tecnico

| Layer | Tecnologia |
|---|---|
| Backend | Python, Flask |
| Database | SQL Server (LAN), CSV fallback (mock) |
| Frontend | HTML, CSS, JavaScript |
| Deploy | VPS Hostinger |
| Repo | `andrealep62/myicorip` (GitHub, public) |

---

## Stato attuale

**MVP avanzato / pre-produzione.** Operativo in locale, mock e VPS.

Modalità dati (file `.env`):
- `USE_REAL_DB=0` → CSV mock (sviluppo offline / Mac a casa)
- `USE_REAL_DB=1` → SQL Server LAN (ufficio)

Avvio: `python myicorip.py` → `https://127.0.0.1:5001`

---

## Cartelle importanti

| Percorso | Contenuto |
|---|---|
| `documenti/` | Documentazione progetto |
| `exports/carts/*.json` | Persistenza carrelli (runtime, esclusa da git) |
| `exports/` | CSV ordini esportati (esclusa da git) |
| `static/` | CSS, JS, immagini |
| `templates/` | HTML Jinja2 |

---

## Principi di sviluppo

**UX:** tablet-first, low-click, ottimizzata per scanner barcode e uso in mobilità.

**Architettura:** modularità, separazione logica, no spaghetti code, no hardcoding.

**Sicurezza:** OWASP base, GDPR-aware. Attenzione a ogni punto di ingresso dati.

**Semplicità:** nessuna soluzione inutilmente complessa. Mobile-first, responsive.

---

## Roadmap tecnica (prossime priorità)

1. **Archivio utenti** — tre categorie: Clienti, Agenti, Interno. Ogni categoria avrà funzioni e permessi specifici.
2. **Filtri macro categorie** — navigazione/filtro prodotti per categoria principale.
3. **Archivio ordini** — ottimizzazione tablet, con focus prioritario sul miglioramento lettura barcode via fotocamera (attualmente difficoltà su barattoli).

---

## Note operative

- Sviluppato su **due macchine**: PC Windows (ufficio, `USE_REAL_DB=1`) e Mac (casa, `USE_REAL_DB=0`)
- `.claude/` è in `.gitignore` — settings locali restano sulla singola macchina
- `exports/carts/` e `exports/*.csv` escluse da git (dati runtime)
