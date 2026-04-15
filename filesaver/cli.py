import subprocess
import sys
import shlex
import urllib.request
import urllib.error
import json
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich import print as rprint

console = Console()


def run(command: str, capture: bool = False):
    result = subprocess.run(
        command,
        shell=True,
        capture_output=capture,
        text=True
    )
    return result.stdout.strip() if capture else None


def timestamp():
    now = datetime.now()
    t = now.strftime("%I:%M%p").lstrip("0").lower()
    return f"save @ {t}"


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
    except (urllib.error.URLError, TimeoutError):
        console.print("[yellow]Ollama not running, using timestamp instead.[/yellow]")
        return None


def parse_and_run(words: list[str]):

    sentence = " ".join(words).lower().strip()

    # ── upload / push
    if any(p in sentence for p in ["upload", "push", "send my"]):
        run("git push")
        console.print("[bold green]Saves uploaded.[/bold green]")
        return

    # ── get latest / pull
    if any(p in sentence for p in ["get latest", "download project", "get updates", "pull"]):
        run("git pull")
        console.print("[bold green]Got the latest saves.[/bold green]")
        return

    # ── clone
    if "clone" in sentence:
        url = sentence.split("clone", 1)[-1].strip()
        if not url:
            console.print("[red]Give a URL, e.g.[/red] [bold]filesaver clone https://github.com/user/repo[/bold]")
            return
        url_part = url.split()[0]
        console.print(f"[dim]Downloading project from {url_part}...[/dim]")
        run(f"git clone {shlex.quote(url_part)}")
        console.print("[bold green]Project downloaded.[/bold green]")
        return

    # ── list saves / history
    if any(p in sentence for p in ["list of saves", "show saves", "my saves", "list saves", "show history"]):
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

    # ── visit a specific save
    if "visit save" in sentence:
        commit_id = None
        for i in range(len(words) - 1):
            if words[i].lower() == "visit" and words[i + 1].lower() == "save":
                tail = words[i + 2:]
                commit_id = tail[0] if tail else None
                break
        if not commit_id:
            console.print("[red]Say which save, e.g.[/red] [bold]filesaver visit save 5a00ca9[/bold]")
            return
        quoted = shlex.quote(commit_id)
        result = subprocess.run(
            f"git switch --detach {quoted}",
            shell=True, capture_output=True, text=True,
        )
        if result.returncode != 0:
            result = subprocess.run(
                f"git checkout {quoted}",
                shell=True, capture_output=True, text=True,
            )
        if result.returncode == 0:
            console.print(
                f"[bold cyan]Visiting save[/bold cyan] {commit_id} "
                "[dim](detached - run filesaver switch to main to leave)[/dim]"
            )
        else:
            err = (result.stderr or result.stdout or "").strip()
            console.print("[red]Couldn't visit that save.[/red]", err or "")
        return

    # ── go back to last save
    if any(p in sentence for p in ["go back", "undo", "last save", "revert"]):
        run("git reset --soft HEAD~1")
        console.print("[bold yellow]Went back to the previous save.[/bold yellow]")
        return

    # ── save only a specific file
    if "save only" in sentence or "add only" in sentence:
        for keyword in ["save only", "add only"]:
            if keyword in sentence:
                filename = sentence.split(keyword, 1)[-1].strip()
                break
        run(f"git add {filename}")
        run(f'git commit -m "saved {filename}"')
        console.print(f"[bold green]Saved:[/bold green] {filename}")
        return

    # ── make a copy / save
    if any(p in sentence for p in ["make a copy", "make a save"]) or sentence.startswith("save"):
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

        console.print(f"[bold green]Saved:[/bold green] {label}")
        return

    # ── delete storyline
    if any(p in sentence for p in ["delete storyline", "remove storyline", "drop storyline"]):
        name = None
        for keyword in ["delete storyline", "remove storyline", "drop storyline"]:
            if keyword in sentence:
                name = sentence.split(keyword, 1)[-1].strip().replace(" ", "-")
                break
        if not name:
            console.print("[red]Which storyline? e.g.[/red] [bold]filesaver delete storyline dark-mode[/bold]")
            return
        current = run("git branch --show-current", capture=True)
        if name == current:
            console.print("[red]You're on that storyline right now. Switch to another one first.[/red]")
            return
        result = subprocess.run(
            f"git branch -d {shlex.quote(name)}",
            shell=True, capture_output=True, text=True,
        )
        if result.returncode == 0:
            console.print(f"[bold yellow]Storyline deleted:[/bold yellow] {name}")
        else:
            err = (result.stderr or result.stdout or "").strip()
            if "not fully merged" in err:
                console.print(f"[yellow]{name} has unmerged saves. Use git branch -D {name} to force-delete.[/yellow]")
            else:
                console.print(f"[red]Couldn't delete storyline:[/red] {err}")
        return

    # ── make a new storyline
    if any(p in sentence for p in ["new storyline", "new story"]):
        name = None
        for keyword in ["called", "named"]:
            if keyword in sentence:
                name = sentence.split(keyword, 1)[-1].strip().replace(" ", "-")
                break
        if not name:
            name = words[-1].replace(" ", "-")
        run(f"git checkout -b {name}")
        console.print(f"[bold cyan]New storyline started:[/bold cyan] {name}")
        return

    # ── switch storyline
    if any(p in sentence for p in ["switch to", "go to storyline", "switch storyline"]):
        for keyword in ["switch to", "go to storyline", "switch storyline"]:
            if keyword in sentence:
                name = sentence.split(keyword, 1)[-1].strip().replace(" ", "-")
                break
        run(f"git checkout {name}")
        console.print(f"[bold cyan]Switched to storyline:[/bold cyan] {name}")
        return

    # ── list storylines
    if any(p in sentence for p in ["list storylines", "show storylines", "my storylines"]):
        output = run("git branch", capture=True)
        console.print("[bold cyan]Your storylines:[/bold cyan]")
        for line in output.splitlines():
            marker = ">" if line.strip().startswith("*") else " "
            name = line.strip().lstrip("* ")
            console.print(f"  {marker} {name}")
        return

    # ── merge storyline
    if any(p in sentence for p in ["merge", "combine"]):
        for keyword in ["merge", "combine"]:
            if keyword in sentence:
                name = sentence.split(keyword, 1)[-1].strip().replace(" ", "-")
                break
        run(f"git merge {name}")
        console.print(f"[bold green]Merged storyline:[/bold green] {name}")
        return

    # ── show full diff (line-by-line)
    if any(p in sentence for p in ["full diff", "full changes", "line by line", "show diff"]):
        output = run("git diff HEAD", capture=True)
        if output:
            console.print("[bold]Full changes since last save:[/bold]")
            for line in output.splitlines():
                if line.startswith("+") and not line.startswith("+++"):
                    console.print(f"[green]{line}[/green]")
                elif line.startswith("-") and not line.startswith("---"):
                    console.print(f"[red]{line}[/red]")
                else:
                    console.print(f"[dim]{line}[/dim]")
        else:
            console.print("[yellow]Nothing changed since your last save.[/yellow]")
        return

    # ── what changed (summary)
    if any(p in sentence for p in ["what changed", "show changes", "what did i change"]):
        output = run("git diff --stat HEAD", capture=True)
        if output:
            console.print("[bold]Changes since last save:[/bold]")
            console.print(output)
        else:
            console.print("[yellow]Nothing changed since your last save.[/yellow]")
        return

    # ── current state / status
    if any(p in sentence for p in ["status", "what's going on", "where am i", "current state"]):
        output = run("git status -s", capture=True)
        branch = run("git branch --show-current", capture=True)
        console.print(f"[bold]Storyline:[/bold] {branch}")
        if output:
            console.print("[bold]Unsaved changes:[/bold]")
            console.print(output)
        else:
            console.print("[green]Everything is saved.[/green]")
        return

    # ── discard changes
    if any(p in sentence for p in ["discard", "throw away", "reset changes", "start over"]):
        run("git checkout -- .")
        console.print("[bold yellow]All unsaved changes discarded.[/bold yellow]")
        return

    # ── unhide / unstash  (BEFORE hide so "unhide" isn't caught by "hide")
    if any(p in sentence for p in ["unhide", "unstash", "unshelve", "get my stuff back"]):
        result = subprocess.run(
            "git stash pop",
            shell=True, capture_output=True, text=True,
        )
        if result.returncode == 0:
            console.print("[bold green]Hidden changes restored.[/bold green]")
        else:
            err = (result.stderr or result.stdout or "").strip()
            if "No stash" in err:
                console.print("[yellow]Nothing hidden to bring back.[/yellow]")
            else:
                console.print(f"[red]Problem restoring hidden changes:[/red] {err}")
        return

    # ── hide / stash
    if any(p in sentence for p in ["hide my changes", "stash", "shelve"]):
        result = subprocess.run(
            "git stash push -u",
            shell=True, capture_output=True, text=True,
        )
        if "No local changes" in (result.stdout + result.stderr):
            console.print("[yellow]Nothing to hide - everything is already saved or clean.[/yellow]")
        else:
            console.print("[bold cyan]Changes hidden. Work on something else, then run:[/bold cyan]")
            console.print("[bold]filesaver unhide my changes[/bold]")
        return

    # ── bookmark / tag
    if any(p in sentence for p in ["bookmark", "tag", "mark save"]):
        tag_name = None
        for keyword in ["bookmark save as", "bookmark this as", "bookmark as",
                         "tag save as", "tag this as", "tag as",
                         "mark save as", "mark this as"]:
            if keyword in sentence:
                tag_name = sentence.split(keyword, 1)[-1].strip().replace(" ", "-")
                break
        if not tag_name:
            after = sentence.split("bookmark", 1)[-1].strip() if "bookmark" in sentence else sentence.split("tag", 1)[-1].strip()
            tag_name = after.replace(" ", "-") if after else None
        if not tag_name:
            console.print("[red]Give it a name, e.g.[/red] [bold]filesaver bookmark save as v1.0[/bold]")
            return
        result = subprocess.run(
            f"git tag {shlex.quote(tag_name)}",
            shell=True, capture_output=True, text=True,
        )
        if result.returncode == 0:
            console.print(f"[bold green]Bookmarked as:[/bold green] {tag_name}")
        else:
            err = (result.stderr or result.stdout or "").strip()
            console.print(f"[red]Couldn't bookmark:[/red] {err}")
        return

    # ── show remote
    if any(p in sentence for p in ["show remote", "where is my project", "remote info"]):
        output = run("git remote -v", capture=True)
        if output:
            console.print("[bold]Your project is connected to:[/bold]")
            for line in output.splitlines():
                console.print(f"  {line}")
        else:
            console.print("[yellow]Not connected to any remote yet. Try:[/yellow]")
            console.print("[bold]filesaver connect to https://github.com/you/repo.git[/bold]")
        return

    # ── connect remote
    if any(p in sentence for p in ["connect to", "link to", "add remote"]):
        url = None
        for keyword in ["connect to", "link to", "add remote"]:
            if keyword in sentence:
                url = sentence.split(keyword, 1)[-1].strip()
                break
        if not url:
            console.print("[red]Give a URL, e.g.[/red] [bold]filesaver connect to https://github.com/you/repo.git[/bold]")
            return
        url_part = url.split()[0]
        run(f"git remote add origin {shlex.quote(url_part)}")
        console.print(f"[bold green]Connected to:[/bold green] {url_part}")
        return

    # ── who changed / blame
    if any(p in sentence for p in ["who changed", "who wrote", "who edited", "blame"]):
        filename = None
        for keyword in ["who changed", "who wrote", "who edited", "blame"]:
            if keyword in sentence:
                filename = sentence.split(keyword, 1)[-1].strip()
                break
        if not filename:
            console.print("[red]Which file? e.g.[/red] [bold]filesaver who changed main.py[/bold]")
            return
        output = run(f"git blame {shlex.quote(filename)}", capture=True)
        if output:
            console.print(f"[bold]Who changed {filename}:[/bold]")
            console.print(output)
        else:
            console.print(f"[yellow]No history found for {filename}.[/yellow]")
        return

    # ── initialize
    if any(p in sentence for p in ["start tracking", "new project", "initialize", "init"]):
        run("git init")
        console.print("[bold green]Started tracking this folder.[/bold green]")
        return

    # ── help
    if any(p in sentence for p in ["help", "what can you do", "commands"]):
        show_help()
        return

    # ── unrecognized
    console.print(f"[red]Hmm, I didn't understand:[/red] \"{' '.join(words)}\"")
    console.print("Try [bold]filesaver help[/bold] to see what you can say.")


def show_help():
    table = Table(title="filesaver - what you can say", show_header=True, header_style="bold magenta")
    table.add_column("What you type", style="cyan")
    table.add_column("What it does")

    rows = [
        ("filesaver make a copy",                   "AI reads your changes and writes the commit message"),
        ("filesaver make a copy fixed login bug",   "Save with your own description"),
        ("filesaver save only main.py",             "Save just one file"),
        ("filesaver give me the list of saves",     "Show all your saves"),
        ("filesaver visit save 5a00ca9",            "Jump to that save (use ID from list)"),
        ("filesaver go back to last save",          "Undo the last save"),
        ("filesaver what changed",                  "Summary of changes since last save"),
        ("filesaver show full diff",                "Line-by-line changes since last save"),
        ("filesaver current state",                 "Show unsaved files + current storyline"),
        ("filesaver discard changes",               "Throw away all unsaved changes"),
        ("filesaver hide my changes",               "Stash changes for later"),
        ("filesaver unhide my changes",             "Restore stashed changes"),
        ("filesaver upload my saves",               "Push to remote"),
        ("filesaver get latest saves",              "Pull from remote"),
        ("filesaver clone <url>",                   "Download a project from a URL"),
        ("filesaver connect to <url>",              "Link this project to a remote"),
        ("filesaver show remote",                   "Show where project is connected"),
        ("filesaver make a new storyline called X", "Create a new branch called X"),
        ("filesaver switch to X",                   "Switch to storyline X"),
        ("filesaver list storylines",               "Show all your storylines"),
        ("filesaver merge X",                       "Merge storyline X into current"),
        ("filesaver delete storyline X",            "Delete a storyline"),
        ("filesaver bookmark save as v1.0",         "Tag / bookmark the current save"),
        ("filesaver who changed main.py",           "See who edited each line of a file"),
    ]
    for what, does in rows:
        table.add_row(what, does)
    console.print(table)


def main():
    if len(sys.argv) < 2:
        show_help()
        return
    parse_and_run(sys.argv[1:])


if __name__ == "__main__":
    main()
