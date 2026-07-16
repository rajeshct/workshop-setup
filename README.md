# Workshop Setup Guide

**Google ADK + Comet OPIK — Engineering Faculty Workshop**

Complete these steps **before** the workshop session. Estimated time: 20–25 minutes.

---

## What You Will Set Up

| Tool | Purpose |
|---|---|
| Git | Clone the workshop repository |
| Python 3.11+ | Run Python code during the workshop |
| VS Code | Code editor for the workshop |
| Ollama | Run a local AI model — **no internet, no rate limits, no API key** (recommended) |
| Google AI Studio account | Free Gemini API key — backup option if Ollama is not possible |
| Comet OPIK account | Free observability platform for monitoring AI calls |
| Project dependencies | `google-adk`, `opik`, `python-dotenv` |

> **Why Ollama?** Gemini's free tier has rate limits (requests per minute). In a classroom with 20–30 people, participants can hit those limits quickly. Ollama runs a model locally on your own machine — no quota, no internet dependency, no API key needed.

---

## Step 1 — Install Git

### macOS

Open **Terminal** (`Cmd + Space` → type `Terminal` → press `Enter`).

```bash
git --version
```

If Git is already installed you will see something like `git version 2.x.x` — skip to Step 2.

If not, macOS will prompt you to install **Xcode Command Line Tools** — click **Install** and wait for it to finish, then re-run the command above to confirm.

### Windows

Open **PowerShell** (`Win + S` → type `PowerShell` → press `Enter`).

```powershell
git --version
```

If Git is already installed you will see `git version 2.x.x.windows.x` — skip to Step 2.

If not, download and run the installer from **[git-scm.com/download/win](https://git-scm.com/download/win)**.
During install, leave all defaults as-is. After install, close and reopen PowerShell, then run `git --version` to confirm.

---

## Step 2 — Install Python 3.11 or Higher

### macOS

```bash
python3 --version
```

If the output is `Python 3.11.x` or higher, skip to Step 3.

If not:

1. Install **Homebrew** if you don't have it yet:
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
2. Install Python:
   ```bash
   brew install python@3.13
   ```
3. Verify:
   ```bash
   python3 --version
   # Expected: Python 3.13.x
   ```

### Windows

Open PowerShell:

```powershell
python --version
```

If the output is `Python 3.11.x` or higher, skip to Step 3.

If not:

1. Go to **[python.org/downloads](https://www.python.org/downloads)**
2. Click **Download Python 3.13.x** (latest stable)
3. Run the installer
4. **Important:** Check the box **"Add python.exe to PATH"** on the first screen
5. Click **Install Now**

Verify (close and reopen PowerShell first):

```powershell
python --version
# Expected: Python 3.13.x
```

---

## Step 3 — Install VS Code

1. Go to **[code.visualstudio.com](https://code.visualstudio.com)**
2. Click **Download for Mac** (macOS) or **Download for Windows** (Windows)
3. Run the installer

### macOS — move to Applications

Open the downloaded `.zip`, drag **Visual Studio Code.app** into your **Applications** folder.

Then add the `code` command to your terminal:

- Open VS Code
- Press `Cmd + Shift + P` to open the Command Palette
- Type `Shell Command: Install 'code' command in PATH` and press `Enter`

Verify:

```bash
code --version
```

### Windows — installer options

During install, check both boxes:
- **Add "Open with Code" action to Windows Explorer file context menu**
- **Add to PATH**

After install, close and reopen PowerShell, then verify:

```powershell
code --version
```

### Recommended VS Code Extensions

1. Open VS Code → click the **Extensions** icon in the left sidebar (or `Ctrl/Cmd + Shift + X`)
2. Search for and install:
   - **Python** (by Microsoft)
   - **Python Debugger** (by Microsoft)

---

## Step 4 — Set Up Your AI Model

You need a model for the workshop. **Choose one option:**

---

### Option A — Ollama (Recommended)

Ollama runs a large language model locally on your machine. No API key, no rate limits, no internet required. Needs ~4 GB of free disk space.

#### Install Ollama

**macOS**

```bash
brew install ollama
```

If you don't have Homebrew yet, install it first (see Step 2). Alternatively, download the macOS app from **[ollama.com/download](https://ollama.com/download)** and drag it to Applications.

**Windows**

Download and run the installer from **[ollama.com/download](https://ollama.com/download)**.
After install, Ollama runs as a background service automatically.

#### Pull a Model (one-time download, ~4 GB)

```bash
ollama pull llama3.2
```

Wait for the download to finish. Verify:

```bash
ollama list
# Should show: llama3.2   ...
```

> Other models that work well: `gemma3`, `mistral`. `llama3.2` is the recommended default.

#### Start Ollama

**macOS** — if you installed via Homebrew:
```bash
ollama serve
```
Leave this terminal window open. Ollama runs at `http://localhost:11434`.

**macOS** — if you installed the app: it starts automatically (look for the llama icon in your menu bar).

**Windows** — starts automatically as a background service after install.

Verify Ollama is running:
```bash
ollama list
# Should respond without error and show your downloaded model
```

#### `.env` settings for Ollama

In Step 8, use these values:

```
GEMINI_MODEL=ollama/llama3.2
```

---

### Option B — Google Gemini (Backup)

Use this if you cannot install Ollama (e.g. restricted machine, low disk space).

> **Rate limit warning:** The free Gemini tier allows ~15 requests/minute per key. Each person must use their **own** key — do not share one key across participants.

1. Go to **[aistudio.google.com](https://aistudio.google.com)**
2. Sign in with your Google account (create one at [accounts.google.com](https://accounts.google.com) if needed)
3. Click **Get API key** → **Create API key in new project**
4. Copy the key — it starts with `AIza...`

#### `.env` settings for Gemini

In Step 8, use these values:

```
GEMINI_API_KEY=AIza...your_key_here...
GEMINI_MODEL=gemini-3.1-flash-lite
GOOGLE_GENAI_USE_VERTEXAI=FALSE
```

---

## Step 5 — Create a Comet OPIK Account

1. Go to **[comet.com/signup](https://www.comet.com/signup)**
2. Sign up with your email (no credit card required)
3. After signing in, go to **Settings → API Keys** (top-right user menu → Settings)
4. Click **Generate API Key** and copy it
5. Note your **workspace name** — shown in the top-left of the dashboard after login

> Keep both the API key and workspace name handy for Step 8.

---

## Step 6 — Clone the Repository

### macOS

```bash
git clone https://github.com/rajeshct/workshop-setup.git
cd workshop-setup
```

### Windows

```powershell
git clone https://github.com/rajeshct/workshop-setup.git
cd workshop-setup
```

Open the project in VS Code:

```bash
code .
```

---

## Step 7 — Create a Virtual Environment and Install Dependencies

A virtual environment keeps this project's packages isolated from the rest of your system.

The `requirements.txt` file installs these packages:

| Package | Minimum Version | Purpose |
|---|---|---|
| `google-adk` | 0.4.0 | Google Agent Development Kit |
| `opik` | 1.7.0 | Comet OPIK observability |
| `python-dotenv` | 1.0.0 | Load `.env` configuration |

### macOS

```bash
# Create the virtual environment
python3 -m venv .venv

# Activate it
source .venv/bin/activate

# You should see (.venv) at the start of your prompt — e.g. (.venv) user@mac %

# Install dependencies
pip install -r requirements.txt
```

### Windows (PowerShell)

```powershell
# Create the virtual environment
python -m venv .venv

# Activate it
.venv\Scripts\Activate.ps1

# You should see (.venv) at the start of your prompt — e.g. (.venv) PS C:\...>

# Install dependencies
pip install -r requirements.txt
```

> **Windows note:** If you see a "running scripts is disabled" error when activating, run this first:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```
> Then run the `Activate.ps1` command again.

### Select the virtual environment in VS Code

1. Open VS Code with the project open
2. Press `Cmd/Ctrl + Shift + P` → type **Python: Select Interpreter**
3. Choose the entry showing `.venv` — e.g. `Python 3.13.x ('.venv': venv)`

### Verify installation

```bash
pip show google-adk opik python-dotenv
```

You should see name and version information for all three packages.

---

## Step 8 — Configure Your API Keys

Copy the example config file:

### macOS

```bash
cp .env.example .env
```

### Windows

```powershell
copy .env.example .env
```

Open `.env` in VS Code (`code .env`) and fill in your values.

#### If you chose Ollama (Option A)

```
GEMINI_MODEL=ollama/llama3.2

OPIK_API_KEY=your_opik_api_key_here
OPIK_WORKSPACE=your_workspace_name_here
OPIK_PROJECT_NAME=engineering-faculty-assistant
```

#### If you chose Gemini (Option B)

```
GEMINI_API_KEY=AIza...your_key_here...
GEMINI_MODEL=gemini-2.0-flash
GOOGLE_GENAI_USE_VERTEXAI=FALSE

OPIK_API_KEY=your_opik_api_key_here
OPIK_WORKSPACE=your_workspace_name_here
OPIK_PROJECT_NAME=engineering-faculty-assistant
```

> Do **not** add quotes around values, and do **not** add spaces around the `=` sign.

---

## Step 9 — Verify Your Setup

Run these checks to confirm everything is in place before the workshop.

### Check Python packages are installed

```bash
pip show google-adk opik python-dotenv
```

All three should show a name and version.

### Check Ollama (if you chose Option A)

```bash
ollama list
```

Should show `llama3.2` in the list without any error.

### Check your `.env` file

Open `.env` in VS Code and confirm:
- `GEMINI_MODEL` is set
- `OPIK_API_KEY` and `OPIK_WORKSPACE` are filled in (not the placeholder text)

If all three checks pass, you are ready for the workshop.

---

## Troubleshooting

**`python3: command not found` (macOS)**
— Python is not installed or not on your PATH. Repeat Step 2.

**`python: command not found` (Windows)**
— Python was installed without the "Add to PATH" option. Reinstall Python and check that box.

**`ModuleNotFoundError: No module named 'google.adk'`**
— The virtual environment is not active. Run `source .venv/bin/activate` (macOS) or `.venv\Scripts\Activate.ps1` (Windows) and try again.

**`Connection refused` or `Failed to connect to localhost:11434` (Ollama)**
— Ollama is not running. On macOS (Homebrew), open a new terminal and run `ollama serve`. On Windows, check that Ollama is running in the system tray.

**`model 'llama3.2' not found` (Ollama)**
— The model was not downloaded. Run `ollama pull llama3.2` and wait for it to finish.

**`429 Resource Exhausted` or `quota exceeded` (Gemini)**
— You have hit the free-tier rate limit. Switch to Ollama (Option A in Step 4) or wait a minute and try again.

**`AuthenticationError` from Gemini**
— Your `GEMINI_API_KEY` is wrong or expired. Go back to [aistudio.google.com](https://aistudio.google.com), generate a new key, and paste it into `.env`.

**`running scripts is disabled` on Windows**
— See the note in Step 7 about `Set-ExecutionPolicy`.

**VS Code shows "No interpreter selected" or can't find packages**
— Open Command Palette (`Cmd/Ctrl + Shift + P`) → **Python: Select Interpreter** → choose the `.venv` entry.

---

## Quick Reference

| Action | macOS | Windows |
|---|---|---|
| Activate virtual env | `source .venv/bin/activate` | `.venv\Scripts\Activate.ps1` |
| Open project in VS Code | `code .` | `code .` |
| Deactivate virtual env | `deactivate` | `deactivate` |

---

## Need Help?

Contact the workshop organiser before the session if you get stuck on any step.
Having your setup complete before the session ensures you can follow along from the start.
