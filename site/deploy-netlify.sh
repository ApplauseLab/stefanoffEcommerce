#!/usr/bin/env bash
# Publish the proof of concept to Netlify (served at the domain root, hidden from search engines).
set -euo pipefail
cd "$(dirname "$0")"
SITE="${NETLIFY_SITE:-stefanoff-poc}"
export ASDF_NODEJS_VERSION="${ASDF_NODEJS_VERSION:-20.19.5}"

python3 build.py --noindex
npx -y netlify-cli@latest deploy --prod --no-build --dir=dist --site="$SITE" --message "$(git rev-parse --short HEAD 2>/dev/null || echo local)"
python3 build.py >/dev/null   # back to the normal build for serve.py
