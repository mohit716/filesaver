# 🎮 filesaver — Git in Plain English

Stop memorizing git commands. Talk to your project like a human.

```bash
filesaver make a copy
filesaver give me the list of saves
filesaver visit save 5a00ca9
filesaver hide my changes
filesaver make a new storyline called dark-mode
filesaver who changed main.py
```

---

## 💡 The Idea

Git is powerful but verbose. `filesaver` wraps it in plain English using a **game save metaphor** — your commits are saves, your branches are storylines. You describe what you want in natural language and the tool figures out the rest.

No more `git add . && git commit -m "..."`. Just talk.

---

## 🤖 AI-Powered Commit Messages

Can't think of what to write? Just type:

```bash
filesaver make a copy
```

`filesaver` reads your actual code changes and uses a **local Mistral model via Ollama** to automatically generate a meaningful commit message — completely offline, no API key needed.

---

## ⚡ What You Can Say

### Saving & History

| Command | What it does |
|---|---|
| `filesaver make a copy` | AI generates commit message from your diff |
| `filesaver make a copy fixed login bug` | Save with your own description |
| `filesaver save only file.py` | Stage and commit a single file |
| `filesaver give me the list of saves` | Show commit history |
| `filesaver visit save 5a00ca9` | Jump to a specific save (use ID from list) |
| `filesaver go back to last save` | Undo last commit (keeps changes) |

### Viewing Changes

| Command | What it does |
|---|---|
| `filesaver what changed` | Summary of changes since last save |
| `filesaver show full diff` | Line-by-line changes (color-coded) |
| `filesaver current state` | Show unsaved files + current storyline |
| `filesaver who changed main.py` | See who edited each line of a file |

### Stashing

| Command | What it does |
|---|---|
| `filesaver hide my changes` | Stash changes for later |
| `filesaver unhide my changes` | Restore stashed changes |
| `filesaver discard changes` | Throw away all unsaved changes |

### Storylines (Branches)

| Command | What it does |
|---|---|
| `filesaver make a new storyline called X` | Create new branch |
| `filesaver switch to X` | Switch to a storyline |
| `filesaver list storylines` | Show all storylines |
| `filesaver merge X` | Merge storyline X into current |
| `filesaver delete storyline X` | Delete a storyline |

### Syncing & Remote

| Command | What it does |
|---|---|
| `filesaver upload my saves` | Push to remote |
| `filesaver get latest saves` | Pull from remote |
| `filesaver clone <url>` | Download a project from a URL |
| `filesaver connect to <url>` | Link this project to a remote |
| `filesaver show remote` | Show where project is connected |

### Other

| Command | What it does |
|---|---|
| `filesaver bookmark save as v1.0` | Tag / bookmark the current save |
| `filesaver start tracking this folder` | git init |

---

## 🛠️ Tech Stack

- **Python** — CLI logic and git subprocess calls
- **Ollama + Mistral 7B** — local LLM for AI commit messages
- **Rich** — colored terminal output
- **pyproject.toml** — proper Python packaging

---

## 🚀 Installation

**1. Install Ollama and pull Mistral**
```bash
# Download Ollama from https://ollama.com
ollama pull mistral
```

**2. Clone and install filesaver**
```bash
git clone https://github.com/mohit716/filesaver.git
cd filesaver
pip install -e .
```

**3. Use it anywhere**
```bash
cd your-project
filesaver make a copy
```

---

## 📁 Project Structure

```
filesaver/
├── filesaver/
│   ├── cli.py        # all commands and Ollama integration
│   └── __init__.py
└── pyproject.toml    # packaging config
```

---

Built by [Mohit Sharma](https://github.com/mohit716) — MSCS @ Drexel University
