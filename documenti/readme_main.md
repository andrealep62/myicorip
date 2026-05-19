# MYICORIP

Piattaforma B2B interna ICORIP per:
- gestione ordini
- ricerca articoli
- scansione barcode
- catalogo prodotti
- sincronizzazione multi-device

---

# Obiettivo

Ridurre tempi e complessità operative per:
- rivenditori
- colorifici
- agenti
- operatori magazzino

La piattaforma è progettata con approccio:
- tablet-first
- fast-order
- low-click
- user-friendly

---

# Stack Tecnologico

- Python
- Flask
- SQL Server
- HTML/CSS/JS
- CSV fallback
- GitHub

---

# Modalità operative

## MOCK MODE

Uso dati CSV realistici.

```env
USE_REAL_DB=0

Uso dati SQL server

```env
USE_REAL_DB=1

Stato attuale:
MVP avanzato / pre-produzione

Repository
https://github.com/andrealep62/myicorip


---

# PROJECT_STATUS.md

```markdown
# PROJECT STATUS

## Stato generale

Il progetto è operativo in ambiente:
- locale
- mock
- VPS hostinger

---

# Funzioni operative

| Funzione | Stato |
|---|---|
| Login | OK |
| Ricerca | OK |
| Scanner | OK |
| Carrello | OK |
| Export CSV | OK |
| Multi-device | OK |
| Persistenza | OK |

---

# Problemi aperti

## Persistenza JSON

Attualmente:
- filesystem JSON

Da migrare:
- SQL Server

---

# Priorità attuali

1. dashboard home
2. archivio ordini
3. macro categorie
4. UI tablet
5. gestione anagrafiche agenti/clienti

---

# Stato UX

UX già definita:
- tablet-first
- low-click
- fast workflow

---

# Stato backend

Backend stabile per:
- ordini
- ricerca
- sincronizzazione

---

# Stato frontend

Frontend funzionante ma da rifinire:
- responsive
- spacing
- controlli touch

# ARCHITECTURE

# Stack

| Layer | Tecnologia |
|---|---|
| Backend | Flask |
| Frontend | HTML/CSS/JS |
| Database | SQL Server |
| Mock | CSV |
| Versioning | GitHub |

---

# Architettura generale

Utente
↓
Frontend Flask
↓
API Flask
↓
DB SQL / CSV
↓
Export Ordini

---

# Modalità dati

## MOCK

CSV locale.

Vantaggi:
- sviluppo casa
- offline
- test rapido

---

## REAL DB

Connessione SQL Server LAN.

---

# Carrello

Persistenza:
exports/carts/*.json

---

# Flow ordine

Ricerca
↓
Aggiunta ordine
↓
Persistenza
↓
Export CSV
↓
Import gestionale

---

# Scanner

Barcode scanner:
- camera browser
- EAN13
- AJAX add-to-cart

---

# Multi-device

Sync:
- merge carrello
- timestamp update
- refresh sincronizzato

---

# Futuro

Migrazione:
- JSON → SQL Server

Tabelle future:
- OrdersCart
- OrdersCartItem
- OrdersHistory

# AI CONTEXT

# Filosofia progetto

MyIcorip NON è un ecommerce tradizionale.

È uno strumento operativo rapido.

---

# Obiettivi principali

- velocità
- semplicità
- riduzione errori
- riduzione click
- utilizzo tablet

---

# Target utenti

- colorifici
- rivenditori
- magazzino
- agenti
- utenti non tecnici

---

# Regole UX

- evitare popup inutili
- pochi click
- pulsanti grandi
- leggibilità elevata
- ottimizzazione touch

---

# Priorità assolute

1. velocità ordine
2. affidabilità
3. UX semplice
4. supporto tablet

---

# Regole sviluppo AI

Quando modifichi codice:
- NON rompere workflow rapido
- NON complicare UI
- mantenere compatibilità mock/realdb
- preservare scanner
- preservare multi-device

---

# Concetti chiave

Scanner barcode centrale.

Ridurre digitazione.

Massimizzare velocità operativa.

---

# Futuro AI

Possibili integrazioni:
- chatbot tecnico
- suggerimenti prodotto
- ricerca intelligente
- supporto clienti

# ROADMAP

# BREVE TERMINE

- dashboard home
- macro categorie
- archivio ordini
- UI tablet
- note ordine generali
- export CSV status

---

# MEDIO TERMINE

- gestione clienti
- gestione agenti
- storico ordini
- statistiche dashboard
- autenticazione avanzata

---

# LUNGO TERMINE

- tracking corrieri
- AI chatbot
- analytics
- situazione finanziaria
- ecosistema rivenditori

# UI FLOW

# LOGIN

Utente
↓
Autenticazione
↓
Dashboard

---

# DASHBOARD

Sezioni previste:
- ORDINA
- ARCHIVIO
- CATALOGO
- STATISTICHE
- ANAGRAFICA

---

# FLOW ORDINE

Ricerca articolo
↓
Modifica quantità
↓
Aggiunta ordine
↓
Carrello
↓
Invio ordine

---

# FLOW SCANNER

Scanner ON
↓
Lettura barcode
↓
Ricerca automatica
↓
Aggiunta ordine
↓
Scanner restart

---

# FLOW MULTI-DEVICE

Device A modifica ordine
↓
Persistenza JSON
↓
Refresh Device B
↓
Merge automatico

---

# Filosofia UI

- touch-friendly
- grandi controlli
- leggibilità
- velocità

Funzionalità attuali
login utenti
ricerca articoli
scanner barcode
ordine rapido
carrello persistente
sincronizzazione multi-device
export CSV
supporto tablet
Stato progetto

Stato attuale:
MVP avanzato / pre-produzione

Repository

https://github.com/andrealep62/myicorip


cd Progetti/myicorip
python myicorip.py

Accesso mock
https://127.0.0.1:5001

Accesso LAN

https://192.168.0.41:5001

Accesso LAN

https://192.168.0.41:5001


---

# FEATURES.md

```markdown
# FEATURES

# Ricerca articoli

- ricerca veloce
- supporto codici speciali
- ordinamento avanzato

---

# Scanner

- EAN13
- camera browser
- restart automatico

---

# Ordini

- multi-device
- note
- quantità
- merge righe

---

# Export

CSV compatibile gestionale.

---

# Persistenza

Carrelli JSON con TTL.

---

# Compatibilità

- tablet
- smartphone
- desktop

# KNOWN ISSUES

# Persistenza JSON

Limiti:
- non scalabile
- no storico avanzato

---

# UI mobile

Da ottimizzare:
- spacing
- touch controls
- scanner precisione

---

# Sicurezza

Attualmente:
- login minimale
- no ruoli avanzati

---

# Export CSV

Workflow temporaneo.

Da sostituire con integrazione diretta.

# FUTURE IDEAS

- tracking corrieri
- AI assistant
- ricerca AI
- suggerimenti prodotti
- statistiche avanzate
- dashboard commerciale
- situazione finanziaria
- integrazione ERP
- catalogo visuale
- gestione articoli Private Label clienti visibili solo al proprietario

