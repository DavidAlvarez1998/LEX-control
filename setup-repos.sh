#!/usr/bin/env bash
set -euo pipefail

ORG_URL="${ORG_URL:?Definí ORG_URL, ej: ORG_URL=https://github.com/DavidAlvarez1998 ./setup-repos.sh}"
ROOT="$(cd "$(dirname "$0")" && pwd)"
PROJECTS=(lex-control-api lex-control-admin lex-control-client)

echo "==> 1) Push de los 3 repos de proyecto"
for p in "${PROJECTS[@]}"; do
  echo "   - $p"
  git -C "$ROOT/$p" remote remove origin 2>/dev/null || true
  git -C "$ROOT/$p" remote add origin "$ORG_URL/$p.git"
  git -C "$ROOT/$p" push -u origin main
done

echo "==> 2) Paraguas (lex-control) con submodules, in-place"
cd "$ROOT"
if [ ! -d .git ]; then
  git init -b main
  git config user.email "adjuan123@gmail.com"
  git config user.name "DavidAlvarez1998"
fi

for p in "${PROJECTS[@]}"; do
  if [ ! -f .gitmodules ] || ! grep -q "path = $p" .gitmodules 2>/dev/null; then
    git submodule add "$ORG_URL/$p.git" "$p"
  fi
done

# Agrega solo los archivos que existen
for f in .gitmodules .gitignore README.md CLAUDE.md docker-compose.dev.yml; do
  [ -f "$f" ] && git add "$f"
done
[ -d openspec ] && git add openspec

git commit -q -m "chore: umbrella repo with project submodules"

git remote remove origin 2>/dev/null || true
git remote add origin "$ORG_URL/LEX-control.git"
git push -u origin main

echo ""
echo "==> Listo. Para clonar todo en otra máquina:"
echo "    git clone --recurse-submodules $ORG_URL/LEX-control.git"