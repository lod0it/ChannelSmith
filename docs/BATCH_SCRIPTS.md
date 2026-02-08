# ChannelSmith Batch Scripts (Windows) 🪟

Tre script .bat per lanciare facilmente ChannelSmith su Windows.

---

## 📋 Script Disponibili

### 1. **launch_web_ui.bat** ⭐ (Consigliato)

**Uso:** Double-click per lanciare la web UI con controlli completi

**Cosa fa:**
- ✅ Verifica che Python è installato
- ✅ Crea virtual environment se non esiste
- ✅ Attiva virtual environment
- ✅ Installa dipendenze (Flask, flask-cors, etc.)
- ✅ Verifica che Flask è disponibile
- ✅ Lancia la web UI
- ✅ Apre browser automaticamente
- ✅ Mostra messaggi di errore chiari

**Quando usare:** Per un lancio robusto con tutti i controlli

---

### 2. **launch_simple.bat** ⚡ (Veloce)

**Uso:** Double-click per un lancio veloce e semplice

**Cosa fa:**
- Installa dipendenze (se necessario)
- Lancia la web UI
- Apre browser

**Quando usare:** Quando sai che tutto è già configurato

---

### 3. **run_tests.bat** 🧪 (Testing)

**Uso:** Double-click per eseguire i test con menu interattivo

**Menu Opzioni:**
```
1. Run ALL tests (Core + API)          → 229 tests
2. Run API tests only                  → 22 tests
3. Run Core tests only                 → 207 tests
4. Run with coverage report            → HTML report
5. Run verbose output                  → Detailed results
6. Exit
```

**Quando usare:** Per verificare che tutto funziona

---

## 🚀 Come Usare

### Metodo 1: Double-Click (Più facile)
1. Apri file explorer
2. Naviga a: `C:\...\ChannelSmith\`
3. Double-click su `launch_web_ui.bat`
4. ✅ Browser apre automaticamente

### Metodo 2: Linea di comando
```cmd
# Aprire cmd o PowerShell nella cartella ChannelSmith
cd C:\path\to\ChannelSmith

# Lanciare script
launch_web_ui.bat

# O eseguire test
run_tests.bat
```

### Metodo 3: Crea shortcut
1. Right-click su `launch_web_ui.bat`
2. Seleziona "Send to" → "Desktop (create shortcut)"
3. Double-click lo shortcut dal desktop

---

## 📊 Cosa Aspettarsi

### launch_web_ui.bat

```
╔════════════════════════════════════════════════════════════╗
║            ChannelSmith Web UI Launcher                   ║
╚════════════════════════════════════════════════════════════╝

Checking Python installation...
[OK] Python 3.14.2 found

[OK] Virtual environment found
[OK] Virtual environment activated
[OK] Dependencies installed
[OK] Flask is available

╔════════════════════════════════════════════════════════════╗
║         Launching ChannelSmith Web UI                     ║
╚════════════════════════════════════════════════════════════╝

Opening http://localhost:5000 in your browser...

Press Ctrl+C to stop the server

 * Running on http://127.0.0.1:5000
 * Press CTRL+C to quit
```

→ Browser apre automaticamente

### run_tests.bat

```
╔════════════════════════════════════════════════════════════╗
║              ChannelSmith Test Runner                     ║
╚════════════════════════════════════════════════════════════╝

Available test options:

  1. Run ALL tests (Core + API)
  2. Run API tests only (22 tests)
  3. Run Core tests only (207 tests)
  4. Run with coverage report
  5. Run verbose output
  6. Exit

Select option (1-6): 1

Running ALL tests...

============ 229 passed in 1.95s ============

Press any key to continue...
```

---

## ⚙️ Requisiti

### Python
- ✅ Python 3.8+
- ✅ Deve essere in PATH (check durante installazione)

### Dipendenze Python
- Automaticamente installate dallo script:
  - Flask 3.0+
  - flask-cors 4.0+
  - Pillow, numpy, pytest (già installate)

### Port
- **Default:** 5000
- Se occupato, modificare in `channelsmith/__main__.py` linea ~45

---

## 🐛 Troubleshooting

### "Python is not installed"
**Soluzione:**
1. Installa Python da https://www.python.org/
2. **IMPORTANTE:** Check "Add Python to PATH" durante installazione
3. Riavvia il computer
4. Riprova

### "Failed to install dependencies"
**Soluzione:**
```cmd
# Apri PowerShell e esegui manualmente:
cd C:\path\to\ChannelSmith
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
```

### "Port 5000 already in use"
**Soluzione 1:** Chiudi altre applicazioni che usano porta 5000

**Soluzione 2:** Cambia porta:
1. Apri `channelsmith/__main__.py`
2. Trova: `app.run(host='127.0.0.1', port=5000)`
3. Cambia a: `app.run(host='127.0.0.1', port=5001)`

### "Browser doesn't open"
**Soluzione:**
1. Apri manualmente: http://localhost:5000
2. Oppure check se porta è diversa (vedi sopra)

### "Blank page in browser"
**Soluzione:**
1. Premi F12 (browser dev tools)
2. Vai a "Console" tab
3. Guarda gli errori JavaScript
4. Verifica che Flask è in esecuzione (terminal)

---

## 📝 Personalizzazione

### Cambiar Port
Modifica `channelsmith/__main__.py` linea ~45:
```python
app.run(host='127.0.0.1', port=5001)  # Cambia a 5001 o altra porta
```

### Cambiar Virtual Environment Path
Modifica i .bat:
```batch
REM Default: venv
if exist venv\ (
    call venv\Scripts\activate.bat
)

REM Custom path (es: .venv)
if exist .venv\ (
    call .venv\Scripts\activate.bat
)
```

### Aggiungere Flag Personalizzati
Modifica ultima linea di `launch_web_ui.bat`:
```batch
REM Default:
python -m channelsmith

REM Con flag (es: legacy GUI):
python -m channelsmith --gui

REM Con variabili ambiente:
set FLASK_DEBUG=1
python -m channelsmith
```

---

## 📊 Statistiche Script

| Script | Linee | Dimensione | Tempo |
|--------|-------|-----------|-------|
| launch_web_ui.bat | 100+ | ~3 KB | <5 sec |
| launch_simple.bat | 15 | ~0.5 KB | <5 sec |
| run_tests.bat | 100+ | ~3 KB | <1 min |

---

## 🔄 Workflow Consigliato

### Primo Avvio
```
1. launch_web_ui.bat  → Installa dipendenze, lancia UI
2. Browser apre       → Prova pack/unpack
3. Ctrl+C per fermare
```

### Sviluppo/Testing
```
1. Modifica codice
2. run_tests.bat      → Scegli opzione (es: 1 per tutti i test)
3. Verifica 229 tests passing
4. launch_web_ui.bat  → Test manualmente UI
```

### Daily Usage
```
1. launch_simple.bat  → Lancio veloce
2. Usa la UI
3. Ctrl+C per fermare
```

---

## 🎯 Quick Reference

| Cosa Fare | Script | Comando |
|-----------|--------|---------|
| Lanciare web UI | `launch_web_ui.bat` | Double-click |
| Lancio veloce | `launch_simple.bat` | Double-click |
| Eseguire test | `run_tests.bat` | Double-click, scegli opzione |
| Linea comando | N/A | `python -m channelsmith` |

---

## ✅ Verifica Installazione

Dopo primo avvio, verifica:
- [ ] Browser apre automaticamente
- [ ] URL: http://localhost:5000
- [ ] Dark theme visibile
- [ ] Pack e Unpack tab presenti
- [ ] Puoi uploadare immagini
- [ ] Pack workflow funziona
- [ ] Unpack workflow funziona
- [ ] `run_tests.bat` mostra 229 passing

Se tutto ✅, sei pronto! 🎉

---

## 📞 Support

Se hai problemi:
1. Leggi sezione "Troubleshooting" sopra
2. Vedi `QUICKSTART.md` per setup manuale
3. Vedi `WEB_UI_TESTING.md` per testing avanzato
4. Controlla `REFERENCE.md` per quick lookup

---

## 💡 Tips

**Tip 1:** Crea shortcut sul desktop di `launch_web_ui.bat` per accesso veloce

**Tip 2:** Aggiungi cartella ChannelSmith a PATH per eseguire da qualunque cartella:
```cmd
setx PATH "%PATH%;C:\path\to\ChannelSmith"
```

**Tip 3:** Se usi frequentemente, crea un file `start.cmd` personalizzato:
```batch
@echo off
cd C:\path\to\ChannelSmith
python -m channelsmith
```

**Tip 4:** Monitora lo stato in tempo reale:
```cmd
# Terminal 1: Lanciare web UI
launch_web_ui.bat

# Terminal 2 (mentre UI è in esecuzione): Eseguire test
run_tests.bat
```

---

**Version:** 0.1.0-web-mvp
**Date:** February 8, 2026
**Status:** Ready to Use ✅
