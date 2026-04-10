# 📖 filesaver — Complete Tutorial

This tutorial walks you through every command in `filesaver` with real examples. No git knowledge required.

---

## 🗂️ Table of Contents

1. [Setting up a new project](#1-setting-up-a-new-project)
2. [Your daily save routine](#2-your-daily-save-routine)
3. [Viewing your save history](#3-viewing-your-save-history)
4. [Undoing mistakes](#4-undoing-mistakes)
5. [Working with storylines (branches)](#5-working-with-storylines-branches)
6. [Syncing with GitHub](#6-syncing-with-github)
7. [Other useful commands](#7-other-useful-commands)

---

## 1. Setting up a new project

Before you can use `filesaver` in a folder, that folder needs to be tracked. Do this once per project.

```bash
cd your-project-folder
filesaver start tracking this folder
```

That's the equivalent of `git init`. You only ever do this once.

---

## 2. Your daily save routine

This is the command you'll use most. Every time you finish something — a feature, a fix, a small change — save it.

**Let AI write the message for you (recommended):**
```bash
filesaver make a copy
```
`filesaver` reads what you changed and asks Mistral to write a meaningful commit message automatically. You just press enter.

**Write your own message:**
```bash
filesaver make a copy fixed the login bug
filesaver make a copy added dark mode toggle
filesaver make a copy updated homepage layout
```

**Save only one specific file:**
```bash
filesaver save only index.html
filesaver save only src/app.py
```
Useful when you changed multiple files but only want to save one of them.

---

## 3. Viewing your save history

Want to see everything you've saved so far?

```bash
filesaver give me the list of saves
```

You'll see a table like this:

```
┏━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ ID         ┃ Description                                     ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ 5a00ca9    │ fixed login bug                                 │
│ f47ecc5    │ added dark mode toggle                          │
│ 2240309    │ initial commit                                  │
└────────────┴─────────────────────────────────────────────────┘
```

**See what changed since your last save:**
```bash
filesaver what changed
```

**See your current unsaved files:**
```bash
filesaver current state
```

---

## 4. Undoing mistakes

Made a save you regret? Go back to the previous one:

```bash
filesaver go back to last save
```

This undoes the last save but **keeps your changes** — so your files are still there, just unsaved. You can then re-save with a better message.

**Throw away all unsaved changes completely:**
```bash
filesaver discard changes
```

⚠️ This one is permanent — your unsaved changes will be gone.

---

## 5. Working with storylines (branches)

Storylines let you work on something new without touching your main working code. Think of it like a parallel universe for your project.

**Start a new storyline:**
```bash
filesaver make a new storyline called dark-mode
filesaver make a new storyline called fix-login-bug
filesaver make a new storyline called experiment
```

**See all your storylines:**
```bash
filesaver list storylines
```

Output:
```
  → dark-mode        ← you are here
    main
    fix-login-bug
```

**Switch to a different storyline:**
```bash
filesaver switch to main
filesaver switch to dark-mode
```

**Merge a storyline into your current one:**
```bash
# first switch to main
filesaver switch to main

# then bring in the dark-mode changes
filesaver merge dark-mode
```

---

## 6. Syncing with GitHub

**Upload your saves to GitHub:**
```bash
filesaver upload my work
```

**Get the latest saves from GitHub (if someone else pushed or you're on another machine):**
```bash
filesaver get latest saves
```

**Typical daily workflow with GitHub:**
```bash
# start your day — get latest
filesaver get latest saves

# do your work, save as you go
filesaver make a copy
filesaver make a copy fixed the navbar

# end of day — upload everything
filesaver upload my work
```

---

## 7. Other useful commands

**Start tracking a brand new folder:**
```bash
filesaver start tracking this folder
```

**See all available commands:**
```bash
filesaver help
```

---

## 🔁 Complete Example: Building a Feature

Here's a full real-world workflow from start to finish:

```bash
# 1. go to your project
cd ~/projects/my-app

# 2. create a new storyline for the feature
filesaver make a new storyline called user-auth

# 3. do your work... write code...

# 4. save your progress
filesaver make a copy added login form UI

# 5. more work...

# 6. save again
filesaver make a copy connected login form to backend

# 7. done — switch back to main and merge
filesaver switch to main
filesaver merge user-auth

# 8. upload to GitHub
filesaver upload my work
```

---

## ❓ Troubleshooting

**`filesaver make a copy` hangs for a long time**
Mistral is loading into memory on first run — this is normal. Wait up to 60 seconds. Every save after that will be fast.

**`⚠ Ollama not running, using timestamp instead`**
Ollama isn't running in the background. Start it by opening CMD and running `ollama serve`, then try again.

**`fatal: not a git repository`**
You haven't initialized the folder yet. Run `filesaver start tracking this folder` first.

---

Built by [Mohit Sharma](https://github.com/mohit716)
