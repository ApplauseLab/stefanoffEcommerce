#!/usr/bin/env bash
# Publish the staging site to GitHub Pages (gh-pages branch of ApplauseLab/stefanoffEcommerce).
set -euo pipefail
cd "$(dirname "$0")"
REPO="https://github.com/ApplauseLab/stefanoffEcommerce.git"
BASE="/stefanoffEcommerce"

python3 build.py --base="$BASE"
tmp="$(mktemp -d)"
cp -R dist/. "$tmp/"
(
  cd "$tmp"
  git init -q && git checkout -q -b gh-pages
  git add -A
  git commit -q -m "Deploy $(date -u +%Y-%m-%dT%H:%MZ) from $(git -C "$OLDPWD" rev-parse --short HEAD 2>/dev/null || echo local)"
  git -c http.postBuffer=524288000 push -q -f "$REPO" gh-pages
)
rm -rf "$tmp"
python3 build.py >/dev/null   # back to the root-path build for serve.py
echo "Deployed: https://applauselab.github.io${BASE}/"
