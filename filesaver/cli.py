import subprocess
import sys
import urllib.request
import urllib.error
import json
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich import print as rprint

console = Console()

# ─── helper: run a git command and return output ───────────────────────────────
def run(command: str, capture: bool = False):
    result = subprocess.run(
        command,
        shell=True,
        capture_output=capture,
        text=True
    )
    return result.stdout.strip() if capture else None

# ─── helper: timestamp string for auto-named saves ────────────────────────────
def timestamp():
    now = datetime.now()
    t = now.strftime("%I:%M%p").lstrip("0").lower()
    return f"save @ {t}"

# ─── helper: ask Ollama/Mistral to generate a commit message from the diff ────
def ai_commit_message():
    run("git add .")
    diff = run("git diff --cached", capture=True)
    if not diff:
        return None

    prompt = (
        "Write a single short git commit message (max 10 words, no quotes, no explanation, "
        "no markdown) describing these code changes:\n\n"
        + diff[:3000]
    )

    payload = json.dumps({
        "model": "mistral",
        "prompt": prompt,
        "stream": False
    }).encode("utf-8")

    try:
        req = urllib.request.Request(
            "http://localhost:11434/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=120) as response:
            result = json.loads(response.read().decode("utf-8"))
            message = result.get("response", "").strip().strip('"').strip("'")
            return message if message else None
    except urllib.error.URLError:
        console.print("[yellow]⚠ Ollama not running, using timestamp instead.[/yellow]")
        return None

# ─── parse the sentence the user typed and route to the right action ──────────
def parse_and_run(words: list[str]):

    sentence = " ".join(words).lower().strip()
    # ── save only a specific file ─────────────────────────────────────────────
    if "save only" in sentence or "add only" in sentence:
        for keyword in ["save only", "add only"]:
            if keyword in sentence:
                filename = sentence.split(keyword, 1)[-1].strip()
                break
        run(f"git add {filename}")
        run(f'git commit -m "saved {filename}"')
        console.print(f"[bold green]✔ Saved:[/bold green] {filename}")
        return

    # ── make a copy / save ────────────────────────────────────────────────────
    if any(phrase in sentence for phrase in ["make a copy", "save", "make a save"]) and "list" not in sentence:
        description = None
        for phrase in ["make a copy", "make a save", "save"]:
            if phrase in sentence:
                after = sentence.split(phrase, 1)[-1].strip()
                if after:
                    description = after
                break

        if description:
            label = description
            run("git add .")
            run(f'git commit -m "{label}"')
        else:
            console.print("[dim]Asking Mistral to describe your changes...[/dim]")
            label = ai_commit_message() or timestamp()
            run(f'git commit -m "{label}"')

        console.print(f"[bold green]✔ Saved:[/bold green] {label}")
        return

    # ── make a new storyline ──────────────────────────────────────────────────
    if any(phrase in sentence for phrase in ["new storyline", "new story"]):
        name = None
        for keyword in ["called", "named"]:
            if keyword in sentence:
                name = sentence.split(keyword, 1)[-1].strip().replace(" ", "-")
                break
        if not name:
            name = words[-1].replace(" ", "-")
        run(f"git checkout -b {name}")
        console.print(f"[bold cyan]✔ New storyline started:[/bold cyan] {name}")
        return

    # ── switch storyline ──────────────────────────────────────────────────────
    if any(phrase in sentence for phrase in ["switch to", "go to storyline", "switch storyline"]):
        for keyword in ["switch to", "go to storyline", "switch storyline"]:
            if keyword in sentence:
                name = sentence.split(keyword, 1)[-1].strip().replace(" ", "-")
                break
        run(f"git checkout {name}")
        console.print(f"[bold cyan]✔ Switched to storyline:[/bold cyan] {name}")
        return

    # ── list storylines ───────────────────────────────────────────────────────
    if any(phrase in sentence for phrase in ["list storylines", "show storylines", "my storylines"]):
        output = run("git branch", capture=True)
        console.print("[bold cyan]Your storylines:[/bold cyan]")
        for line in output.splitlines():
            marker = "→" if line.strip().startswith("*") else " "
            name = line.strip().lstrip("* ")
            console.print(f"  {marker} {name}")
        return

    # ── merge storyline ───────────────────────────────────────────────────────
    if any(phrase in sentence for phrase in ["merge", "combine"]):
        for keyword in ["merge", "combine"]:
            if keyword in sentence:
                name = sentence.split(keyword, 1)[-1].strip().replace(" ", "-")
                break
        run(f"git merge {name}")
        console.print(f"[bold green]✔ Merged storyline:[/bold green] {name}")
        return

    # ── list saves / history ──────────────────────────────────────────────────
    if any(phrase in sentence for phrase in ["list of saves", "show saves", "my saves", "list saves", "show history"]):
        output = run("git log --oneline --decorate -15", capture=True)
        if not output:
            console.print("[yellow]No saves yet.[/yellow]")
            return
        table = Table(title="Your Saves", show_header=True, header_style="bold magenta")
        table.add_column("ID", style="dim", width=10)
        table.add_column("Description")
        for line in output.splitlines():
            parts = line.split(" ", 1)
            table.add_row(parts[0], parts[1] if len(parts) > 1 else "")
        console.print(table)
        return

    # ── go back to last save ──────────────────────────────────────────────────
    if any(phrase in sentence for phrase in ["go back", "undo", "last save", "revert"]):
        run("git reset --soft HEAD~1")
        console.print("[bold yellow]↩ Went back to the previous save.[/bold yellow]")
        return

    # ── upload saves / push ───────────────────────────────────────────────────
    if any(phrase in sentence for phrase in ["upload", "push", "send my saves"]):
        run("git push")
        console.print("[bold green]✔ Saves uploaded.[/bold green]")
        return

    # ── get latest saves / pull ───────────────────────────────────────────────
    if any(phrase in sentence for phrase in ["get latest", "download", "get updates", "pull"]):
        run("git pull")
        console.print("[bold green]✔ Got the latest saves.[/bold green]")
        return

    # ── what changed ──────────────────────────────────────────────────────────
    if any(phrase in sentence for phrase in ["what changed", "show changes", "what did i change"]):
        output = run("git diff --stat HEAD", capture=True)
        if output:
            console.print("[bold]Changes since last save:[/bold]")
            console.print(output)
        else:
            console.print("[yellow]Nothing changed since your last save.[/yellow]")
        return

    # ── current state / status ────────────────────────────────────────────────
    if any(phrase in sentence for phrase in ["status", "what's going on", "where am i", "current state"]):
        output = run("git status -s", capture=True)
        branch = run("git branch --show-current", capture=True)
        console.print(f"[bold]Storyline:[/bold] {branch}")
        if output:
            console.print("[bold]Unsaved changes:[/bold]")
            console.print(output)
        else:
            console.print("[green]Everything is saved.[/green]")
        return

    # ── discard changes ───────────────────────────────────────────────────────
    if any(phrase in sentence for phrase in ["discard", "throw away", "reset changes", "start over"]):
        run("git checkout -- .")
        console.print("[bold yellow]✔ All unsaved changes discarded.[/bold yellow]")
        return

    # ── initialize / git init ─────────────────────────────────────────────────
    if any(phrase in sentence for phrase in ["start tracking", "new project", "initialize", "init"]):
        run("git init")
        console.print("[bold green]✔ Started tracking this folder.[/bold green]")
        return

    # ── help    ──────────────────────────────────────────────────────────────────
    if any(phrase in sentence for phrase in ["help", "what can you do", "commands"]):
        show_help()
        return

    # ── unrecognized ──────────────────────────────────────────────────────────
    console.print(f"[red]Hmm, I didn't understand:[/red] \"{' '.join(words)}\"")
    console.print("Try [bold]filesaver help[/bold] to see what you can say.")

# ─── help screen ──────────────────────────────────────────────────────────────
def show_help():
    table = Table(title="filesaver — what you can say", show_header=True, header_style="bold magenta")
    table.add_column("What you type", style="cyan")
    table.add_column("What it does")

    rows = [
        ("filesaver make a copy",                  "AI reads your changes and writes the commit message"),
        ("filesaver make a copy fixed login bug",   "Save with your own description"),
        ("filesaver give me the list of saves",     "Show all your saves"),
        ("filesaver go back to last save",          "Undo the last save"),
        ("filesaver what changed",                  "Show what's different since last save"),
        ("filesaver current state",                 "Show unsaved files + current storyline"),
        ("filesaver discard changes",               "Throw away all unsaved changes"),
        ("filesaver upload my saves",               "Push to remote"),
        ("filesaver get latest saves",              "Pull from remote"),
        ("filesaver make a new storyline called X", "Create a new branch called X"),
        ("filesaver switch to X",                   "Switch to storyline X"),
        ("filesaver list storylines",               "Show all your storylines"),
        ("filesaver merge X",                       "Merge storyline X into current"),
    ]
    for what, does in rows:
        table.add_row(what, does)
    console.print(table)

# ─── entry point ─────────────────────────────────────────────────────────────
def main():
    if len(sys.argv) < 2:
        show_help()
        return
    parse_and_run(sys.argv[1:])

if __name__ == "__main__":
    main()
