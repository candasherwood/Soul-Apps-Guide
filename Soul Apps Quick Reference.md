# Soul Apps — Quick reference

Every install and start command on one page, for pinning up next to the machine.
The full walkthrough with explanations is in *Installing the Soul Apps Manually*.

**Python check** — need 3.11–3.13, 3.12 preferred: `py -0p`

**Zana — install** (from `D:\SoulApps\zana-main\zana-main`)

```powershell
cd "D:\SoulApps\zana-main\zana-main"
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

**Zana — start / stop**

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8765
```

Or double-click `start.bat` / `stop.bat`.

**Aspyra v2 — install** (from `D:\SoulApps\Aspyra_v2-main\Aspyra_v2-main`)

```powershell
cd "D:\SoulApps\Aspyra_v2-main\Aspyra_v2-main"
py -3.12 -m venv app\.venv
.\app\.venv\Scripts\python.exe -m pip install -r app\requirements.txt
Copy-Item app\.env.example app\.env
```

**Aspyra v2 — start / stop**

```powershell
cd app
$env:APP_PORT = "7012"
..\app\.venv\Scripts\python.exe -m uvicorn app:app --host 127.0.0.1 --port 7012
```

Or double-click `Start Aspyra v2.bat`; close its window to stop.

**Ollama (needed for chat in both apps)**

```powershell
ollama pull llama3.2:3b
```

**The 22 installers** (no Python needed)

```powershell
cd "D:\SoulApps\SoulInstallers"
.\<Name>_Setup_1.0.0.exe /VERYSILENT /SUPPRESSMSGBOXES /NORESTART
```

**Health checks**

```powershell
(Invoke-WebRequest http://127.0.0.1:8765/api/health).Content
(Invoke-WebRequest http://127.0.0.1:7012/api/health).Content
```

---

*Soul Apps live in `D:\SoulApps`. The full guide (`Installing the Soul Apps Manually.pdf`)
explains each command, the order to run them in, and what to do when something fails.*
