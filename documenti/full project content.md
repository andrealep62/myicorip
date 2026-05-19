# MYICORIP — FULL PROJECT CONTEXT (AI READY)

## Panoramica Progetto

**MyIcorip** è una web-app B2B sviluppata internamente per ICORIP con lo scopo di semplificare e velocizzare:

* inserimento ordini
* ricerca articoli
* scansione barcode
* gestione carrelli multi-device
* futura gestione catalogo e clienti

L’app è pensata principalmente per:

* colorifici
* rivenditori
* agenti
* operatori magazzino
* tablet in negozio

---

# Filosofia del progetto

## Obiettivo UX

Ridurre al minimo:

* digitazione
* click
* errori
* tempi di ricerca

L’esperienza deve essere:

* velocissima
* intuitiva
* utilizzabile anche da personale non tecnico
* ottimizzata per tablet e smartphone

---

# Stack Tecnologico

| Area            | Tecnologia                     |
| --------------- | ------------------------------ |
| Backend         | Python + Flask                 |
| Frontend        | HTML + CSS + JS                |
| Database        | SQL Server                     |
| Fallback dati   | CSV Mock                       |
| Hosting attuale | LAN / ambiente interno         |
| Versionamento   | GitHub                         |
| Ambiente locale | macOS + Windows                |
| Scanner         | Barcode via fotocamera/browser |

---

# Repository

Repository GitHub:

[myicorip GitHub Repository](https://github.com/andrealep62/myicorip?utm_source=chatgpt.com)

---

# Struttura attuale del progetto

## Modalità dati

### MOCK MODE

```env
USE_REAL_DB=0
```

Utilizza:

* CSV reale esportato dal gestionale
* dati realistici
* sviluppo da casa

---

### REAL DB MODE

```env
USE_REAL_DB=1
```

Connessione:

* SQL Server aziendale
* accessibile solo da LAN/DMZ

---

# Architettura generale

## Flow base

```text
Utente
   ↓
Ricerca articolo
   ↓
Aggiunta ordine
   ↓
Carrello persistente
   ↓
Export CSV
   ↓
Import gestionale
```

---

# Funzionalità già operative

## Login utenti

Utenti test:

* Andrea
* Alice
* Marco

Password:

```text
test
```

---

## Ricerca articoli

Funzioni:

* ricerca rapida
* ricerca per codice
* ricerca descrizione
* supporto codici con virgola
* ordinamento avanzato

---

## Scanner Barcode

Funzioni:

* lettura EAN
* stop automatico dopo lettura valida
* restart automatico
* integrazione ordine

---

## Gestione ordine/carrello

Funzioni:

* aggiunta articoli AJAX
* merge quantità
* note per riga
* quantità con pack
* badge “In ordine”
* sincronizzazione multi-device

---

## Persistenza carrello

Attualmente:

```text
exports/carts/*.json
```

Con:

* merge automatico
* TTL configurabile
* sincronizzazione sessioni

---

# Stato attuale UI

## Dashboard

Prevista home principale con:

* ORDINA
* ARCHIVIO
* CATALOGO
* STATISTICHE
* ANAGRAFICA

Approccio:

* pulsanti grandi
* tablet first
* interfaccia “friendly”

---

# Concetti UX importanti

## Tablet-first

L’interfaccia deve essere:

* usabile con mani sporche
* usabile velocemente
* leggibile da distanza
* con controlli grandi

---

## Ridurre digitazione

Per questo esistono:

* scanner
* macro categorie
* gruppi articoli
* quick order

---

# Stato avanzamento sviluppo

## Funzionante

| Funzione             | Stato |
| -------------------- | ----- |
| Login                | OK    |
| Ricerca articoli     | OK    |
| Scanner              | OK    |
| Ordine               | OK    |
| Export CSV           | OK    |
| Multi-device         | OK    |
| Persistenza carrello | OK    |
| Modalità mock        | OK    |
| Modalità DB reale    | OK    |

---

## In sviluppo / da migliorare

| Area              | Stato         |
| ----------------- | ------------- |
| UI mobile         | Da rifinire   |
| Dashboard home    | Da creare     |
| Archivio ordini   | Da creare     |
| Macro categorie   | Da completare |
| Anagrafiche       | Da creare     |
| Statistiche       | Future        |
| Tracking corrieri | Futuro        |
| AI chatbot        | Futuro        |

---

# TODO PRIORITARI

## Breve termine

* migliorare UI tablet
* macro categorie
* archivio ordini
* note ordine generali
* export CSV con status
* dashboard iniziale

---

## Medio termine

* gestione clienti/agenti
* autenticazione avanzata
* storico ordini
* dashboard statistiche

---

## Lungo termine

* tracking corrieri
* AI assistente tecnico
* analisi statistiche
* situazione finanziaria

---

# Problemi architetturali noti

## Persistenza JSON

Attualmente:

```text
JSON filesystem
```

Da migrare verso:

```text
SQL Server
```

Tabelle previste:

* OrdersCart
* OrdersCartItem
* OrdersHistory

---

# Configurazione ambiente

## macOS

```bash
cd /Users/andrea/Progetti/myicorip
source .venv_mac/bin/activate
python myicorip.py
```

---

## Windows

```bash
cd Progetti/myicorip
python myicorip.py
```

---

# Accessi applicazione

## Ambiente ufficio

```text
https://192.168.0.41:5001
```

Utenti:

* Andrea
* Alice

Password:

```text
test
```

---

## Ambiente casa/mock

```text
https://127.0.0.1:5001
```

---

# Query SQL importante

View attuale:

```sql
vw_AND_webappordini_articoli
```

Campi chiave:

* Prodotto
* Colore
* Formato
* Gruppo
* S_Gruppo
* UM

---

# Macro categorie previste

Esempi:

* Bianchi
* Basi edilizia
* Convertitori industria
* Trasparenti

---

# Concetto catalogo

In futuro:

* catalogo visuale
* zoom articolo
* dettagli tecnici
* immagini
* varianti

---

# Concetto AI futuro

Possibile integrazione:

* OpenAI
* chatbot tecnico
* consigli prodotti
* supporto clienti
* ricerca intelligente

---

# Immagini e mockup disponibili

Disponibili screenshot:

* dashboard
* catalogo
* macro categorie
* ordine rapido
* scanner
* acquisti
* UI iPad

---

# Filosofia di sviluppo

Il progetto NON è pensato come ecommerce classico.

È uno strumento operativo rapido per:

* ordini veloci
* operatori reali
* uso pratico quotidiano

La velocità operativa è più importante dell’estetica.

---

# Indicazioni importanti per AI Agent

## Regole fondamentali

Quando modifichi il progetto:

* NON rompere il flusso rapido
* mantenere UX semplice
* evitare popup inutili
* ottimizzare tablet
* ridurre digitazione
* preservare compatibilità mock/DB reale

---

# Priorità assolute

1. velocità operativa
2. semplicità
3. leggibilità tablet
4. affidabilità ordine
5. sincronizzazione multi-device

---

# Stato generale progetto

Il progetto è già in stato:

```text
MVP avanzato / pre-produzione
```

Non è un prototipo iniziale:

* molte logiche core sono già funzionanti
* architettura base definita
* UX già ragionata
* flussi principali già presenti

---

# Suggerimento operativo futuro

Per lavorare bene con AI moderne:

* mantenere documentazione aggiornata
* salvare decisioni architetturali
* documentare TODO
* mantenere changelog evolutivo

---

# File consigliati nel repository

```text
/docs
    README_MAIN.md
    PROJECT_STATUS.md
    ARCHITECTURE.md
    UI_FLOW.md
    ROADMAP.md
    AI_CONTEXT.md
    CHANGELOG.md
```

---

# Conclusione

MyIcorip ha il potenziale per diventare:

* piattaforma ordini B2B completa
* ecosistema rivenditori ICORIP
* dashboard operativa multiutente
* futuro hub AI per assistenza commerciale e tecnica

Il progetto ha già:

* una direzione chiara
* casi d’uso reali
* logica business concreta
* UX pensata per utilizzo quotidiano reale

Questa è la base corretta per evolvere verso:

* SaaS interno
* piattaforma rete vendita
* sistema ordini avanzato
* integrazione AI futura.
