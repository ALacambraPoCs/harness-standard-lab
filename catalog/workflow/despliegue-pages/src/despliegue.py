#!/usr/bin/env python3
"""Pasos del workflow `despliegue-pages` (componente del catálogo; F5.6-A, D-072).

Solo biblioteca estándar. El workflow lo ejecuta con `python3 -I` desde la copia de la rama por defecto,
nunca desde el contenido que se despliega.

  preparar   → objetivo (SHA que se despliega), anterior (SHA que sirve hoy el sitio) y url, para $GITHUB_OUTPUT
  construir  → copia el sitio del objetivo (git archive, sin ejecutar su código) y escribe version.txt
  verificar  → espera a que la URL sirva version.txt == SHA (reintentos: caché de Pages)
  aviso      → cuerpo de la issue cuando se ha revertido o no se ha podido revertir
"""
from __future__ import annotations

import argparse
import io
import re
import shutil
import subprocess
import sys
import tarfile
import time
import urllib.error
import urllib.request
from pathlib import Path

SHA = re.compile(r"^[0-9a-f]{40}$")
VERSION_FILE = "version.txt"


class Error(Exception):
    pass


def git(repo: str, *args: str, binary: bool = False):
    r = subprocess.run(["git", "-C", repo, *args], capture_output=True, check=False, text=not binary)
    if r.returncode != 0:
        raise Error(f"git {' '.join(args)}: {(r.stderr if not binary else r.stderr.decode(errors='replace')).strip()}")
    return r.stdout


def default_url(repo: str) -> str:
    owner, name = repo.split("/", 1)
    host = f"{owner.lower()}.github.io"
    return f"https://{host}/" if name.lower() == host else f"https://{host}/{name}/"


def fetch_version(url: str, timeout: float = 15) -> str | None:
    """SHA publicado en <url>/version.txt, o None. Evita la caché con un parámetro y `no-cache` (NV: F5.7)."""
    full = url.rstrip("/") + f"/{VERSION_FILE}?harness={time.time_ns()}"
    req = urllib.request.Request(full, headers={"Cache-Control": "no-cache", "User-Agent": "harness-despliegue"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:  # noqa: S310 (URL del propio sitio)
            text = r.read(200).decode("utf-8", "replace").strip()
    except (urllib.error.URLError, TimeoutError, OSError):
        return None
    return text if SHA.match(text) else None


def preparar(repo_dir: str, repo: str, sha_manual: str, ref: str, head: str, url: str, rama: str = "main",
             fetch=fetch_version) -> dict:
    if ref != f"refs/heads/{rama}":
        raise Error(f"Solo se despliega desde la rama por defecto (ref actual: {ref}).")
    objetivo = head
    if sha_manual:
        if not SHA.match(sha_manual):
            raise Error("El SHA manual debe ser un SHA completo de 40 caracteres hexadecimales.")
        try:
            git(repo_dir, "merge-base", "--is-ancestor", sha_manual, head)
        except Error as exc:
            raise Error(f"{sha_manual} no está en la historia de la rama por defecto: solo se despliega lo que se fusionó.") from exc
        objetivo = sha_manual
    url = url or default_url(repo)
    anterior = fetch(url) or ""
    if anterior:
        try:
            git(repo_dir, "merge-base", "--is-ancestor", anterior, head)
        except Error:
            anterior = ""            # lo que se sirve no viene de la rama por defecto: no se usa como destino de rollback
    return {"objetivo": objetivo, "anterior": anterior, "url": url}


def construir(repo_dir: str, sha: str, origen: str, out: str) -> int:
    """Extrae `origen/` del commit `sha` en `out/` y añade version.txt. No ejecuta nada del commit."""
    if not SHA.match(sha):
        raise Error(f"SHA no válido: {sha!r}")
    origen = origen.strip("/")
    data = git(repo_dir, "archive", "--format=tar", sha, "--", origen, binary=True)
    dest = Path(out)
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    n = 0
    with tarfile.open(fileobj=io.BytesIO(data)) as tar:
        for m in tar.getmembers():
            rel = Path(m.name).relative_to(origen) if m.name != origen else None
            if rel is None or not (m.isfile() or m.isdir()):
                continue                                   # sin enlaces simbólicos ni dispositivos
            if ".." in rel.parts or rel.is_absolute():
                raise Error(f"Ruta no permitida en el sitio: {m.name}")
            if rel.name == VERSION_FILE and len(rel.parts) == 1:
                raise Error(f"El sitio no puede traer su propio {VERSION_FILE}: lo escribe el despliegue.")
            target = dest / rel
            if m.isdir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(tar.extractfile(m).read())
            n += 1
    if n == 0:
        raise Error(f"`{origen}/` no existe o está vacío en {sha[:12]}.")
    (dest / VERSION_FILE).write_text(sha + "\n", encoding="utf-8")
    return n


def verificar(url: str, sha: str, timeout: float, intervalo: float, fetch=fetch_version, sleep=time.sleep) -> bool:
    fin = time.monotonic() + timeout
    while True:
        visto = fetch(url)
        if visto == sha:
            print(f"OK: {url} sirve {sha[:12]}.")
            return True
        if time.monotonic() >= fin:
            print(f"::error::{url} sirve {visto or 'nada legible'} en lugar de {sha[:12]} tras {int(timeout)} s.")
            return False
        sleep(intervalo)


def aviso(repo: str, run_url: str, objetivo: str, anterior: str, revertido: str) -> str:
    if not anterior:
        estado = "**No había versión anterior verificable: no se ha revertido.** El sitio puede estar sirviendo una versión rota."
    elif revertido == "success":
        estado = f"Se ha **revertido** a `{anterior[:12]}` y se ha verificado que el sitio la sirve."
    else:
        estado = (f"**El rollback a `{anterior[:12]}` no se ha podido completar o verificar** (`{revertido or 'no ejecutado'}`). "
                  "Sigue el runbook de rollback manual.")
    return (f"El despliegue de `{objetivo}` en GitHub Pages no superó la verificación.\n\n{estado}\n\n"
            f"- Run: {run_url}\n- Auditoría: `harness audit {objetivo}`\n"
            f"- Rollback manual: Actions → despliegue-pages → Run workflow (rama por defecto) con el SHA de una versión buena.\n\n"
            "_Issue abierta por el workflow `despliegue-pages` (sin credenciales del modelo)._\n")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="despliegue.py")
    sub = p.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("preparar")
    a.add_argument("--repo-dir", required=True)
    a.add_argument("--repo", required=True)
    a.add_argument("--sha", default="")
    a.add_argument("--ref", required=True)
    a.add_argument("--url", default="")
    a.add_argument("--rama", default="main")
    b = sub.add_parser("construir")
    b.add_argument("--repo-dir", required=True)
    b.add_argument("--sha", required=True)
    b.add_argument("--origen", default="site")
    b.add_argument("--out", default="_site")
    c = sub.add_parser("verificar")
    c.add_argument("--url", required=True)
    c.add_argument("--sha", required=True)
    c.add_argument("--timeout", type=float, default=600)
    c.add_argument("--intervalo", type=float, default=15)
    d = sub.add_parser("aviso")
    for x in ("--repo", "--run-url", "--objetivo"):
        d.add_argument(x, required=True)
    d.add_argument("--anterior", default="")
    d.add_argument("--revertido", default="")
    args = p.parse_args(argv)
    try:
        if args.cmd == "preparar":
            head = git(args.repo_dir, "rev-parse", "HEAD").strip()
            for k, v in preparar(args.repo_dir, args.repo, args.sha, args.ref, head, args.url, args.rama).items():
                print(f"{k}={v}")
            return 0
        if args.cmd == "construir":
            n = construir(args.repo_dir, args.sha, args.origen, args.out)
            print(f"Sitio de {args.sha[:12]}: {n} archivos + {VERSION_FILE}.", file=sys.stderr)
            return 0
        if args.cmd == "verificar":
            return 0 if verificar(args.url, args.sha, args.timeout, args.intervalo) else 1
        print(aviso(args.repo, args.run_url, args.objetivo, args.anterior, args.revertido))
        return 0
    except Error as exc:
        print(f"::error::{exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
