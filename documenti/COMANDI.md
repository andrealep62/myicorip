# 🚀 MyIcorip: Manuale Operativo Rapido

## 💻 SEZIONE 1: SVILUPPO LOCALE (Sul tuo Mac)
**Terminale:** VS Code o Terminale macOS.

1. **Entra nel progetto:**
   `cd /Users/andrea/Progetti/myicorip`

2. **Attiva l'ambiente virtuale:**
   `source venv/bin/activate`
   *(Verifica che appaia (venv) a inizio riga)*

3. **Avvia l'app:**
   `python3 myicorip.py`

4. **Vedere le modifiche:**
   Salva i file e premi `Cmd + Shift + R` su Chrome.

---

## 📤 SEZIONE 2: INVIO AGGIORNAMENTI (Git/GitHub)
**Terminale:** VS Code (mentre l'app è ferma).

1. **Prepara i file:** `git add .`
2. **Crea il pacchetto:** `git commit -m "Fix carrello, UX e multi-utente"`
3. **Invia a GitHub:** `git push origin main`

---

## ☁️ SEZIONE 3: AGGIORNAMENTO SERVER (VPS Hostinger)
**Terminale:** SSH (Terminal.app o Web Terminal Hostinger).

1. **Entra nel server:** `ssh root@TUO_IP_VPS`
2. **Vai alla cartella:** `cd /home/myicorip/myicorip`
3. **Scarica il nuovo codice:** `git pull origin main`
4. **Attiva il VENV del server:** `source venv/bin/activate`
5. **Riavvia l'app:** `sudo systemctl restart myicorip`

---

## 🧪 SEZIONE 4: UTENTI TEST
- **Utenti:** andrea, roberto, samantha, sinergia, alice, renato.
- **Password:** test (per tutti).