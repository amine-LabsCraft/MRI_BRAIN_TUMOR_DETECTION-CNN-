"""
═══════════════════════════════════════════════════════════════════════════════
 BrainScan AI — Lanceur automatique
═══════════════════════════════════════════════════════════════════════════════

Démarre :
  • API FastAPI   → http://localhost:8000
  • Interface Web → http://localhost:3000

Puis ouvre automatiquement le navigateur.

Usage :
    python start.py                      # ports par défaut (8000, 3000)
    python start.py --api-port 9000      # API sur un autre port
    python start.py --web-port 3001      # Interface sur un autre port
    python start.py --no-browser         # Ne pas ouvrir le navigateur
    python start.py --no-reload          # Pas de auto-reload sur l'API

Ctrl+C dans ce terminal arrête proprement les deux serveurs.
═══════════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations

import argparse
import os
import platform
import signal
import socket
import subprocess
import sys
import time
import urllib.request
import webbrowser
from pathlib import Path

# ─── Setup ────────────────────────────────────────────────────────────────────
BASE_DIR     = Path(__file__).resolve().parent
INTERFACE_DIR = BASE_DIR / "interface"
PYTHON       = sys.executable                       # currently running interpreter
IS_WIN       = platform.system() == "Windows"

# Petit helper de couleurs ANSI (s'auto-désactive si Windows ancien)
if IS_WIN:
    os.system("")  # active les codes ANSI sur Windows 10+

class C:
    RESET = "\033[0m"
    BOLD  = "\033[1m"
    DIM   = "\033[2m"
    CYAN  = "\033[36m"
    GREEN = "\033[32m"
    YELLOW= "\033[33m"
    RED   = "\033[31m"
    BLUE  = "\033[34m"
    GRAY  = "\033[90m"


# ─── Helpers ──────────────────────────────────────────────────────────────────
def banner():
    print(f"""{C.CYAN}{C.BOLD}
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║   🧠  BrainScan AI — Auto Launcher                               ║
║       ResNet50 · 98.96% Accuracy · FastAPI + Vanilla JS          ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
{C.RESET}""")


def port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.2)
        return s.connect_ex(("127.0.0.1", port)) == 0


def find_free_port(start: int) -> int:
    p = start
    while port_in_use(p):
        p += 1
        if p > start + 50:
            raise RuntimeError(f"No free port found near {start}")
    return p


def wait_for_api(url: str, timeout: float = 60) -> bool:
    """Block until /health responds 200 (or timeout)."""
    print(f"  {C.DIM}Attente de l'API ({url}/health)…{C.RESET}", end="", flush=True)
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(f"{url}/health", timeout=2) as r:
                if r.status == 200:
                    print(f"  {C.GREEN}✓{C.RESET}")
                    return True
        except Exception:
            pass
        print(".", end="", flush=True)
        time.sleep(0.8)
    print(f"  {C.RED}✗ timeout{C.RESET}")
    return False


def spawn(cmd: list[str], cwd: Path, label: str) -> subprocess.Popen:
    """Spawn a subprocess that streams stdout/stderr inline (with a label)."""
    print(f"  {C.GRAY}→ {label}: {' '.join(cmd)}{C.RESET}")
    # On Windows, CREATE_NEW_PROCESS_GROUP lets us send Ctrl+Break later.
    creationflags = subprocess.CREATE_NEW_PROCESS_GROUP if IS_WIN else 0
    return subprocess.Popen(
        cmd,
        cwd=str(cwd),
        creationflags=creationflags,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
    )


def kill(proc: subprocess.Popen | None, label: str) -> None:
    if proc is None or proc.poll() is not None:
        return
    print(f"  {C.YELLOW}↳ Arrêt de {label}…{C.RESET}", end=" ", flush=True)
    try:
        if IS_WIN:
            proc.send_signal(signal.CTRL_BREAK_EVENT)
        else:
            proc.terminate()
        try:
            proc.wait(timeout=4)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=2)
        print(f"{C.GREEN}OK{C.RESET}")
    except Exception as e:
        print(f"{C.RED}échec ({e}){C.RESET}")


# ─── Main ─────────────────────────────────────────────────────────────────────
def main() -> int:
    ap = argparse.ArgumentParser(
        description="Lanceur automatique de BrainScan AI (API + interface).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    ap.add_argument("--api-port",   type=int, default=8000, help="Port pour l'API FastAPI (défaut 8000)")
    ap.add_argument("--web-port",   type=int, default=3000, help="Port pour l'interface (défaut 3000)")
    ap.add_argument("--no-browser", action="store_true", help="Ne pas ouvrir le navigateur")
    ap.add_argument("--no-reload",  action="store_true", help="Désactiver --reload sur l'API")
    args = ap.parse_args()

    banner()

    # ── Vérifs préalables
    if not (BASE_DIR / "api" / "app.py").exists():
        print(f"{C.RED}✗ api/app.py introuvable.{C.RESET}")
        return 1
    if not INTERFACE_DIR.exists():
        print(f"{C.RED}✗ Dossier interface/ introuvable.{C.RESET}")
        return 1

    # ── Résolution des ports
    api_port = args.api_port
    web_port = args.web_port
    if port_in_use(api_port):
        new_port = find_free_port(api_port + 1)
        print(f"  {C.YELLOW}⚠ Port {api_port} déjà occupé → API sur {new_port}{C.RESET}")
        api_port = new_port
    if port_in_use(web_port):
        new_port = find_free_port(web_port + 1)
        print(f"  {C.YELLOW}⚠ Port {web_port} déjà occupé → Interface sur {new_port}{C.RESET}")
        web_port = new_port

    api_url = f"http://localhost:{api_port}"
    web_url = f"http://localhost:{web_port}"

    # ── Si l'interface utilise un port API non standard, prévenir l'utilisateur
    if api_port != 8000:
        print(f"  {C.YELLOW}⚠ L'interface est codée pour http://localhost:8000 par défaut.{C.RESET}")
        print(f"    {C.GRAY}Édite CONFIG.API_BASE dans interface/app.js si besoin.{C.RESET}")

    api_proc = None
    web_proc = None

    try:
        # ── Lancement API
        print(f"\n{C.BOLD}🔵 Démarrage de l'API FastAPI{C.RESET}  ({api_url})")
        api_cmd = [PYTHON, "-m", "uvicorn", "api.app:app",
                   "--host", "0.0.0.0", "--port", str(api_port)]
        if not args.no_reload:
            api_cmd.append("--reload")
        api_proc = spawn(api_cmd, BASE_DIR, "API")

        # ── Lancement Frontend
        print(f"\n{C.BOLD}🟢 Démarrage de l'interface web{C.RESET}  ({web_url})")
        web_cmd = [PYTHON, "-m", "http.server", str(web_port)]
        web_proc = spawn(web_cmd, INTERFACE_DIR, "WEB")

        # ── Attente que l'API soit prête (chargement du modèle ~10-20s)
        print()
        if not wait_for_api(api_url, timeout=90):
            print(f"\n{C.RED}✗ L'API n'a pas répondu dans les 90s. Voir les logs.{C.RESET}")
            return 2

        # ── Ouvrir le navigateur
        print(f"\n{C.GREEN}{C.BOLD}✅ Tout est prêt !{C.RESET}")
        print(f"   {C.CYAN}🌐 Interface  : {C.BOLD}{web_url}{C.RESET}")
        print(f"   {C.CYAN}🔌 API health : {C.BOLD}{api_url}/health{C.RESET}")
        print(f"   {C.CYAN}📚 API docs   : {C.BOLD}{api_url}/docs{C.RESET}  (Swagger)")
        print(f"\n   {C.GRAY}Ctrl+C ici pour arrêter les deux serveurs.{C.RESET}\n")

        if not args.no_browser:
            try:
                webbrowser.open(web_url)
            except Exception:
                pass

        # ── Boucle de monitoring : si un process meurt, on tue l'autre
        while True:
            time.sleep(1)
            if api_proc.poll() is not None:
                print(f"\n{C.RED}✗ L'API s'est arrêtée (code {api_proc.returncode}).{C.RESET}")
                break
            if web_proc.poll() is not None:
                print(f"\n{C.RED}✗ Le serveur web s'est arrêté (code {web_proc.returncode}).{C.RESET}")
                break

    except KeyboardInterrupt:
        print(f"\n\n{C.YELLOW}⏹  Interruption clavier détectée.{C.RESET}")

    finally:
        print(f"\n{C.BOLD}🛑 Arrêt des services…{C.RESET}")
        kill(web_proc, "Interface")
        kill(api_proc, "API")
        print(f"\n{C.GREEN}{C.BOLD}👋 Au revoir.{C.RESET}\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
