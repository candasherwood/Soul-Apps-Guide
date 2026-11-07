# Installing the Soul Apps Manually

A step-by-step guide for installing the Soul App repositories by hand after
downloading their zip files — plus the shortcut route for the stand-alone
utilities that ship as one-click installers.

Everything below is done in **PowerShell** or **Command Prompt** on Windows 10/11
(64-bit). Nothing is sent to a cloud service: both apps run on your own machine.

There are two routes:

* **Option A — one-click installers** (section 3): the 22 stand-alone SOUL
  utilities in `D:\SoulApps\SoulInstallers`. No Python, no setup — just run them.
* **Option B — manual install from a zip** (sections 4–8): Zana and Aspyra v2,
  installed into their own Python environments.

The PDFs and the quick-reference sheet in this folder are generated from this
guide; section 11 explains how to rebuild them after an edit.

---

## Quick reference — commands only {: .newpage .sheet }

Every command in the guide, nothing else. Explanations are in the numbered
sections that follow this page.

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

## 1. What you are installing {: .newpage }

| App | Zip file | What it is | Address | Needs Ollama |
|---|---|---|---|---|
| **Zana** | `zana-main.zip` | Local voice assistant: speak → local LLM answer → optional spoken reply, with voice emotion analysis, mood history and saved transcripts | `http://127.0.0.1:8765` | Yes, for chat |
| **Aspyra v2** | `Aspyra_v2-main.zip` | Private AI workspace: chat, agents, coding agent, notes, calendar, research, documents, memory | `http://127.0.0.1:7012` | Yes, for chat |

The two apps are independent. You can install either one, or both, into the same
parent folder (for example `D:\SoulApps`).

**Neither zip contains LLM weights.** Chat models live in Ollama's own store, and
the speech/emotion models download on first use from Hugging Face. Only the
repositories are in the zip.

The 22 stand-alone programs in `D:\SoulApps\SoulInstallers` are a separate set
entirely — see section 3.

---

## 2. Before you start

### 2.1 Install Python

Both zip apps need **Python 3.11, 3.12 or 3.13**. Use **3.12** if you have the
choice. (This does not apply to the installers in section 3, which need no Python
at all.)

> **Do not use Python 3.14 or newer.** PyTorch (needed by Zana) publishes no
> wheels for those versions yet, so `pip install` fails with
> `No matching distribution found for torch`. Python 3.15 is too new as well.

Check which versions are installed:

```powershell
py -0p
```

If nothing is listed, install Python from <https://www.python.org/downloads/windows/>
and tick **Add python.exe to PATH** during setup. The `py` launcher comes with it.

If several versions exist, pick the right one per command with `py -3.12`.

### 2.2 Free disk space

| Item | Approximate size |
|---|---|
| Zana's Python packages (PyTorch) | ~2.5 GB |
| Aspyra's Python packages | ~1 GB |
| Zana's speech + emotion models (first recording) | ~1–3.5 GB |
| Chat models in Ollama | 1–8 GB each |

Plan for roughly **12 GB** free for a comfortable install of both apps with one
or two chat models.

### 2.3 Optional: Ollama (chat)

Zana and Aspyra are **Ollama clients** — they talk to `http://127.0.0.1:11434`.
Install Ollama from <https://ollama.com/download> if you want chat answers.
Without it, Zana's voice recording and emotion analysis still work; only the
chatting is unavailable (the model picker shows everything as `· offline`).

---

## 3. Option A — the one-click installers in `SoulInstallers`

`D:\SoulApps\SoulInstallers` holds **22 stand-alone Windows installers** published
under the company name *SOUL Ecosystem* — all version 1.0.0 except
`VoiceMind_Setup_2.0.0.exe`. They install separate desktop utilities, not Zana or
Aspyra.

Unlike the zip route, these need **none** of the setup steps in this guide — no
Python, no `venv`, no `pip install`, no `.env` file and no Ollama. Double-click,
follow the wizard, done.

### 3.1 Installing them

1. Double-click the installer for the app you want.
2. If Windows shows **"Windows protected your PC"** (SmartScreen, because the
   builds are unsigned), click **More info → Run anyway**.
3. Follow the wizard. It offers an install folder and, depending on the package,
   a per-user or per-machine location plus an optional desktop shortcut.
4. Uninstall later from **Settings → Apps → Installed apps**.

All 22 are **Inno Setup** packages, so they also install silently — useful for
scripting a whole set at once:

```powershell
cd "D:\SoulApps\SoulInstallers"
.\SOULVault_Setup_1.0.0.exe /VERYSILENT /SUPPRESSMSGBOXES /NORESTART
```

Install them one at a time rather than firing off all 22 at once: some of the
wizards ask for a folder or a shortcut preference.

### 3.2 What each installer installs

| Installer | Size | Program |
|---|---|---|
| `BootMagic_Setup_1.0.0.exe` | 12.2 MB | BootMagic — boot / startup configuration |
| `CPUX_Setup_1.0.0.exe` | 44.8 MB | CPUX — CPU monitoring and tuning |
| `DailyCommandCenter_Setup_1.0.0.exe` | 11.6 MB | Daily Command Center — daily task dashboard |
| `EragonAI_Setup_1.0.0.exe` | 163.1 MB | IT Eragon AI — AI assistant |
| `ObsidianAssistant_Setup_1.0.0.exe` | 47.9 MB | Obsidian Session Assistant — helper for Obsidian note sessions |
| `QuickShots_Setup_1.0.0.exe` | 52.3 MB | QuickShots — screenshot capture |
| `SOULAntivirus_Setup_1.0.0.exe` | 45.0 MB | SOUL Antivirus — malware scanner |
| `SOULClean_Setup_1.0.0.exe` | 44.8 MB | SOULClean — system cleaner |
| `SOULDeck_Setup_1.0.0.exe` | 249.5 MB | SOULDeck — the largest package in the folder |
| `SOULDiskPro_Setup_1.0.0.exe` | 7.9 MB | SOULDiskPro — disk usage and storage |
| `SOULDownloader_Setup_1.0.0.exe` | 160.1 MB | SOUL Downloader — download manager |
| `SOULEnergyManager_Setup_1.0.0.exe` | 44.7 MB | SOUL Energy Manager — power and energy settings |
| `SOULForgeAIStudio_Setup_1.0.0.exe` | 46.2 MB | SOULFORGE AI Studio — AI workspace |
| `SOULVault_Setup_1.0.0.exe` | 25.4 MB | SOUL Vault — private storage |
| `SOULVPNManager_Setup_1.0.0.exe` | 160.1 MB | SOUL VPN Manager — VPN connections |
| `StepsRecorder_Setup_1.0.0.exe` | 51.5 MB | StepsRecorder — records a sequence of actions step by step |
| `TournamentManager_Setup_1.0.0.exe` | 11.6 MB | Tournament Manager — tournaments and brackets |
| `VibeDriverUpdater_Setup_1.0.0.exe` | 165.7 MB | Vibe Driver Updater — driver updates |
| `VideoMagic_Setup_1.0.0.exe` | 11.7 MB | VideoMagic — video work |
| `VoiceMind_Setup_1.0.0.exe` | 50.1 MB | VoiceMind 1.0 — earlier voice assistant |
| `VoiceMind_Setup_2.0.0.exe` | 50.0 MB | VoiceMind 2.0 — newer build of the same app |
| `VoiceMindExtended_Setup_1.0.0.exe` | 50.1 MB | VoiceMind Extended — extended variant |

The installers carry only a product name and a company name in their file
metadata — no feature list — so the "Program" column restates what each product
name describes. The wizard that opens shows the same name.

### 3.3 The three VoiceMind installers

`VoiceMind_Setup_1.0.0.exe`, `VoiceMind_Setup_2.0.0.exe` and
`VoiceMindExtended_Setup_1.0.0.exe` are the older, self-contained VoiceMind
desktop app — the line that **Zana continues**. If you want the current voice
assistant (browser recorder, Whisper transcription, emotion fusion, mood
history, streamed local-model answers), install Zana from `zana-main.zip` with
Step 2 in section 5 below; keep these installers only if you specifically want
the legacy desktop build. Within them, 2.0.0 is the newer of the two plain
builds, and "Extended" is the larger variant.

### 3.4 Which route to use

| You want… | Use |
|---|---|
| The voice assistant, current version | `zana-main.zip` → Step 2, section 5 |
| The AI workspace with the coding agent | `Aspyra_v2-main.zip` → Step 3, section 6 |
| Any of the 22 stand-alone utilities | The matching `*_Setup_*.exe` in `SoulInstallers` |

Everything from here on is the manual zip route.

---

## 4. Step 1 — Extract the zip files

1. Right-click the zip → **Extract All…** → choose the parent folder (for example
   `D:\SoulApps`).
2. Open the extracted folder and find the folder that contains the app files.

Expected layouts after extraction:

```
zana-main\
└── zana-main\            <- the folder you work in
    ├── app\              the FastAPI backend
    ├── static\           the web interface
    ├── requirements.txt
    ├── .env.example
    ├── start.bat
    ├── stop.bat
    └── run.ps1
```

```
Aspyra_v2-main\
└── Aspyra_v2-main\      <- the folder you work in
    ├── app\              the backend + .venv lives here
    │   ├── app.py
    │   ├── requirements.txt
    │   └── .env.example
    ├── setup-v2.ps1
    └── Start Aspyra v2.bat
```

> The zips unpack with **one nested folder of the same name**. That is why the
> path is often `D:\SoulApps\zana-main\zana-main`. Always `cd` into the inner
> folder — the one holding `requirements.txt` (Zana) or `setup-v2.ps1` (Aspyra).

**Tip:** avoid installing into a OneDrive-synced folder. Syncing a multi-gigabyte
virtual environment causes long stalls and file locks.

---

## 5. Step 2 — Install Zana manually

Open PowerShell and go to the Zana folder:

```powershell
cd "D:\SoulApps\zana-main\zana-main"
```

### 5.1 Create the virtual environment

```powershell
py -3.12 -m venv .venv
```

This creates a self-contained `.venv\` folder. If `py -3.12` is not found, use
whichever of `py -3.11` / `py -3.13` you have installed.

### 5.2 Install the dependencies

```powershell
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

This downloads PyTorch and friends and takes several minutes. The install is
finished when pip prints `Successfully installed …` and returns to the prompt.

> **Why the full path `.\.venv\Scripts\python.exe`?** Activating the environment
> (`Activate.ps1`) is blocked by default in PowerShell. Calling the venv's Python
> directly works in every shell without changing any policy.

### 5.3 Create the configuration file

```powershell
Copy-Item .env.example .env
```

`.env` holds local settings only and is ignored by git. The defaults in
`.env.example` are correct for a standard install; the lines worth knowing:

| Setting | Meaning |
|---|---|
| `OLLAMA_BASE=http://127.0.0.1:11434` | where Ollama listens — keep the IP, not `localhost` |
| `ZANA_DEFAULT_MODEL=voicemind:latest` | model preselected in the toolbar |
| `WHISPER_MODEL=openai/whisper-small` | speech-to-text; `openai/whisper-medium` is more accurate but ~3x slower |
| `WHISPER_LANGUAGE=en` | pin the transcription language; leave it set |
| `OLLAMA_EXE=` | full path to `ollama.exe` if it is not on `PATH` |
| `OLLAMA_MODELS=` | Ollama's model store, only used when Zana starts Ollama itself |

Optional: keep everything inside the app folder by pointing the caches at it:

```powershell
setx OLLAMA_MODELS "D:\SoulApps\zana-main\zana-main\models\ollama"
setx HF_HOME      "D:\SoulApps\zana-main\zana-main\models\huggingface"
```

Open a new terminal after `setx`, then move any existing `%USERPROFILE%\.ollama\models`
or `%USERPROFILE%\.cache\huggingface` folder into those locations.

### 5.4 Start the app

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8765
```

Leave this window open — closing it stops the app. Then open
**<http://127.0.0.1:8765>** in your browser.

The convenience launchers do the same thing (and reuse the `.venv` you just
built), so once the manual start works you can simply double-click `start.bat`:

| Command | Effect |
|---|---|
| `start.bat` | start the server, wait for `/api/health`, open the browser |
| `start.bat -NoBrowser` | start without opening a browser |
| `start.bat -Port 9000` | listen on another port |
| `stop.bat` | stop the Python process listening on port 8765 |

### 5.5 First run: models download on demand

* **First voice recording** downloads the emotion models (`superb/wav2vec2-base-superb-er`,
  `cardiffnlp/twitter-roberta-base-emotion`) and the Whisper model into
  `%USERPROFILE%\.cache\huggingface\hub` (or `HF_HOME`). Expect a wait of a minute
  or more on a cold cache; later recordings are local and immediate.
* **The microphone must be allowed.** When the browser asks, click **Allow**. If
  the app shows *"Microphone blocked"*, click the padlock in the address bar →
  Site settings → Microphone → Allow, then reload.
* **Chat models are not included.** The SOUL tags (`voicemind`, `soul-quick`,
  `soul-gemma`, …) are private builds and cannot be pulled from the public
  registry — they appear greyed out as `· not pulled`. Pull any public model and
  select it in the toolbar instead:

  ```powershell
  ollama pull llama3.2:3b
  ```

  Reload the page afterwards: the picker reads the model list on page load.

---

## 6. Step 3 — Install Aspyra v2 manually

Open PowerShell and go to the Aspyra folder:

```powershell
cd "D:\SoulApps\Aspyra_v2-main\Aspyra_v2-main"
```

### 6.1 Create the virtual environment

Aspyra keeps its environment **inside `app\`**, not at the repository root:

```powershell
py -3.12 -m venv app\.venv
```

### 6.2 Install the dependencies

```powershell
.\app\.venv\Scripts\python.exe -m pip install --upgrade pip
.\app\.venv\Scripts\python.exe -m pip install -r app\requirements.txt
```

Aspyra needs Python **3.11+**; 3.12 is what its own setup script uses. The
install is large (it includes local embeddings, a vector-store client and
`faster-whisper` for the microphone). If a single optional package fails, the
core app usually still runs — read the pip output before deciding to stop.

> The same steps are what `setup-v2.ps1` automates. If you prefer the script:
> `powershell -NoProfile -ExecutionPolicy Bypass -File .\setup-v2.ps1`
> It is safe to re-run and reuses an existing `app\.venv`.

### 6.3 Create the configuration file

```powershell
Copy-Item app\.env.example app\.env
```

Aspyra reads its settings from `app\.env`. Most options are also editable inside
the app under **Settings**; use `.env` for deployment-level values:

| Setting | Meaning |
|---|---|
| `APP_PORT` | port to serve on (the launcher uses `7012`) |
| `APP_BIND` | bind address; keep `127.0.0.1` so it stays local |
| `LLM_HOST` | host of the local model server (`localhost` / `127.0.0.1`) |
| `LEGACY_CHAT_URL` | optional legacy chat build, `http://127.0.0.1:7003` |

### 6.4 Start the app

From the `app` folder (that is where the `app:app` module lives):

```powershell
cd app
$env:APP_PORT = "7012"
..\app\.venv\Scripts\python.exe -m uvicorn app:app --host 127.0.0.1 --port 7012
```

Then open **<http://127.0.0.1:7012>**.

The launcher does the same and additionally starts the process in the
background, waits for `/api/health`, and opens the browser:

| Launcher | Opens |
|---|---|
| `Start Aspyra v2.bat` | the full workspace at `/` (port 7012) |
| `Aspyra.bat` | just the agent at `/SKAgent` |
| `setup-v2.ps1` | one-time (or repair) venv + dependency setup |

### 6.5 First run

* The first start **creates the admin account** and prints a temporary password
  in the console. Log in with it, then change it under **Settings**.
* Chat needs a model in Ollama. Pick one under **Settings → AI → Default Chat
  Model**; Aspyra falls back to `127.0.0.1:11434` on its own.
* Models named `soul-*` must be present in your Ollama store. If they were built
  into a different store, import them:

  ```powershell
  python restore-models.py            # import every complete soul-* model
  python restore-models.py --dry-run  # report only
  ```

---

## 7. Step 4 — Ollama, once for both apps

Install Ollama, then confirm it is serving:

```powershell
ollama --version
ollama list
```

If `ollama` is not on `PATH`, start the desktop app from the Start menu, or run
`ollama serve` from its install folder (`%LOCALAPPDATA%\Programs\Ollama` or
`C:\Program Files\Ollama`).

Pull at least one general-purpose model:

```powershell
ollama pull llama3.2:3b        # small and fast, good first choice
ollama pull qwen2.5-coder:7b   # better for code work, ~4.7 GB
```

Both apps read the list live, so reload the page after a pull. Zana's launcher
starts Ollama for you when it is not already running.

---

## 8. Step 5 — Check that the install worked

| Check | Zana | Aspyra |
|---|---|---|
| Health endpoint | `http://127.0.0.1:8765/api/health` | `http://127.0.0.1:7012/api/health` |
| Model list | `http://127.0.0.1:8765/api/models` | in **Settings → AI** |
| Interface loads | card layout with a model picker | sidebar workspace |

A quick command-line test:

```powershell
Invoke-WebRequest http://127.0.0.1:8765/api/health -UseBasicParsing | Select-Object -Expand Content
```

A `{"status":"ok",…}` answer with `"ollama": true` means the server and Ollama
are both reachable.

Then, in Zana, do one real end-to-end pass:

1. Pick a **Model** and a **Mic** in the toolbar.
2. Press **Record**, wait for the level line to move, speak, press **Stop**.
3. The transcript appears in the composer and a `voice: … 3.7/5` chip appears.
4. Press **Send** and watch the answer stream in.

If that works, the whole chain — browser, capture, Whisper, emotion models,
SQLite history, Ollama — is installed correctly.

---

## 9. Everyday use

### 9.1 Start and stop

| App | Start | Stop |
|---|---|---|
| Zana | double-click `start.bat` | double-click `stop.bat` |
| Aspyra | double-click `Start Aspyra v2.bat` | close its console window |

When you start the apps by hand instead, `Ctrl+C` in the terminal stops the
server cleanly.

### 9.2 Ports in use

Both apps stop with a clear message if their port is taken. Options:

```powershell
# Zana on another port
start.bat -Port 9000
# or permanently, in .env
ZANA_PORT=9000
```

```powershell
# Aspyra on another port
.\start-aspyra-v2.ps1 -Port 7013
```

Find and free a port:

```powershell
Get-NetTCPConnection -LocalPort 8765 -State Listen | Select-Object OwningProcess
Get-Process -Id <pid>
```

### 9.3 Where things are stored

| What | Location |
|---|---|
| Zana recordings/analysis history | `<zana folder>\data\zana.db` |
| Zana saved transcripts | `<zana folder>\data\chat-snapshots\` |
| Zana speech + emotion models | `%USERPROFILE%\.cache\huggingface\hub` (or `HF_HOME`) |
| Chat models | Ollama's store, `%USERPROFILE%\.ollama\models` by default |
| Aspyra data and settings | inside `app\` (see `app\.env`) |
| Python environments | `zana-main\.venv\` and `Aspyra_v2-main\app\.venv\` |

Deleting `.venv` only removes the Python packages; the app itself and its data
are untouched, and the install steps rebuild the environment.

---

## 10. Troubleshooting

| Symptom | Cause and fix |
|---|---|
| `No matching distribution found for torch` | Python is 3.14+ — recreate the venv with `py -3.12 -m venv .venv` |
| `py -3.12` not recognised | Python 3.12 is not installed; install it or use an available 3.11/3.13 |
| `Activate.ps1 cannot be loaded because running scripts is disabled` | Do not activate; call `.\.venv\Scripts\python.exe` directly, or run `Set-ExecutionPolicy -Scope Process Bypass` in that window |
| `'uvicorn' is not recognised` | You are outside the venv — use `.\.venv\Scripts\python.exe -m uvicorn …` |
| `Port 8765 is already in use` | `stop.bat`, or start with `-Port 9000` |
| Chat shows `· offline` / model list empty | Ollama is not running: start it, run `ollama list`, reload the page |
| Model listed as `· not pulled` | It is a private SOUL build; pull a public model and select that instead |
| `Microphone blocked` in the app | Address bar padlock → Site settings → Microphone → Allow, then reload |
| Recording transcribes to nothing | Check the mic picker, the Windows input device and the mute key; use the 🎙 **Microphone check** panel in Zana |
| First recording takes a long time | Whisper and the emotion models are downloading; later clips are local |
| The UI does not change after an update | The dev server sends no cache headers: press **Ctrl+F5** |
| Aspyra asks for a login you never set | The temporary admin password is printed in the console on first start; restart the app to see it again |
| `python restore-models.py` finds nothing | The Soul models live in another Ollama store; point `OLLAMA_MODELS` at it first |
| An installer window closes instantly or does nothing | Run it from a normal (non-elevated) window, or use `/VERYSILENT /SUPPRESSMSGBOXES` to see errors surface in the console |
| SmartScreen blocks an installer | Unsigned local build: **More info → Run anyway** |

---

## 11. Keeping the guide and the sheet in step

`Installing the Soul Apps Manually.md` is the master copy. Everything else in
this folder is generated from it, so edit the markdown and rebuild; never edit a
generated file by hand, because the next build overwrites it.

| File | Where it comes from |
|---|---|
| `Installing the Soul Apps Manually.pdf` | this guide, printed by `build_guide_pdf.py` |
| `Soul Apps Quick Reference.md` | the unnumbered Quick reference page, lifted from the guide |
| `Soul Apps Quick Reference.pdf` | the same sheet, printed on one A4 page |
| `Soul Apps Quick Reference.txt` | the same sheet as plain text, for a phone or a chat window |

The commands are copied out of the guide verbatim, so the sheet and the guide
cannot disagree; the sheet only adds its own title and closing note.

**Double-click `Rebuild Quick Reference.bat`** and pick a number:

```
1  Rebuild the guide PDF and the quick-reference sheet
2  Check that everything is still in step
3  Open the quick-reference sheet - PDF
4  Open the plain-text sheet - TXT
5  Open the full guide - PDF
6  Quit
```

Option 1 reprints both PDFs from the markdown, so one click is all an edit
needs. Option 2 only reads and compares, and changes nothing: it is the safe one
to run when you just want to know whether something has drifted.

**Or from a command prompt**, if you prefer:

```
py build_quick_reference.py            # rebuild the sheet - md, pdf and txt
py build_quick_reference.py --check    # exit 1 if the sheet is out of step
py build_quick_reference.py --watch    # rebuild the sheet whenever the guide is saved
py build_guide_pdf.py                  # reprint this guide
py build_guide_pdf.py --check          # exit 1 if this PDF is older than the markdown
py build_guide_pdf.py --open           # reprint it and open it
```

Both scripts need only Python 3 and Google Chrome, which section 2 covers: the
markdown is rendered by the scripts themselves and the PDF is printed by
Chrome's headless mode, so there is nothing to install.

**If you edit the Quick reference page**, rebuild the guide as well - option 1
does both. That page is printed inside this guide too, and skipping the reprint
would leave two different versions of the same commands.

---

## 12. Checklist

- [ ] Decided the route: one-click installers (section 3) and/or the zip apps (sections 4–8)
- [ ] Python 3.11–3.13 installed (`py -0p` lists it) — only for the zip apps
- [ ] Zip extracted; the app folder with `requirements.txt` located
- [ ] `.venv` created with `py -3.12 -m venv …`
- [ ] `pip install -r requirements.txt` finished successfully
- [ ] `.env` / `app\.env` copied from the example file
- [ ] Ollama running and at least one model pulled (for chat)
- [ ] `/api/health` returns `ok` for each app
- [ ] A real voice recording produced a transcript and a mood chip (Zana)
- [ ] Shortcuts to `start.bat` / `Start Aspyra v2.bat` placed where you want them

Installation is complete when both apps answer on their addresses, the interface
renders, and a chat reply (or a finished voice clip) arrives.
