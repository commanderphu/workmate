#!/usr/bin/env bash
# clean_ui.sh — Aufräumen der Vue/Vite-UI (JS→TS)

set -e

cd "$(dirname "$0")/ui"

echo "🧹  Cleaning UI project …"

# 1) Alte JS-Entrypoints & Dubletten löschen
rm -f src/main.js src/App.vue.js src/lib/api.js src/lib/types.js src/router/index.js
find src -type f -name '*.old.*' -delete

# 2) Build- und Cache-Ordner löschen
rm -rf dist node_modules tsconfig.tsbuildinfo

# 3) Optional: überflüssige Lockfiles
rm -f package-lock.json yarn.lock

# 4) Saubere Neuinstallation
if command -v pnpm &>/dev/null; then
  echo "📦 Installing with pnpm…"
  pnpm install
else
  echo "📦 Installing with npm…"
  npm ci
fi

# 5) Kurzer Hinweis
echo
echo "✅ UI cleanup complete."
echo "   - main.js/App.vue.js removed"
echo "   - node_modules reinstalled"
echo "   - ready to run: npm run dev"
