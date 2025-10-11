#!/usr/bin/env bash
# ============================================
# 🧩 Workmate Dev Setup Check & Repair Script
# ============================================
# Features:
#   - Rechte & Ownership prüfen
#   - /etc/hosts-Einträge verwalten
#   - Caddy User Mode starten
#   - Docker & Compose prüfen
#   - Optionaler --repair Modus
#   - ASCII Status-Panel für Dienste
# ============================================

set -euo pipefail
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPAIR_MODE="${1:-}"

# Farben
GREEN="\033[0;92m"
RED="\033[0;91m"
YELLOW="\033[0;93m"
BLUE="\033[0;94m"
RESET="\033[0m"

bold() { echo -e "\033[1m$1${RESET}"; }
status_line() {
  local icon="$1"; local name="$2"; local msg="$3"
  printf "  %b %-12s %s\n" "$icon" "$name" "$msg"
}

echo
bold "📦 Workmate Setup gestartet"
echo "   → Projektpfad: $PROJECT_ROOT"
echo

# --- 1️⃣ Rechte & Besitzer korrigieren ---
bold "🔧 Setze Dateiberechtigungen ..."
sudo chown -R "$(id -u):$(id -g)" "$PROJECT_ROOT/backend" "$PROJECT_ROOT/ui" || true
chmod -R u+rwX,go+rX "$PROJECT_ROOT/backend" "$PROJECT_ROOT/ui"
echo -e "   ${GREEN}✅ Berechtigungen gesetzt${RESET}\n"

# --- 2️⃣ /etc/hosts prüfen ---
bold "🌐 Prüfe /etc/hosts ..."
if ! grep -q "ui.workmate.test" /etc/hosts; then
  echo -e "   ${YELLOW}➕ Trage lokale Domains ein...${RESET}"
  echo "127.0.0.1 ui.workmate.test api.workmate.test health.workmate.test" | sudo tee -a /etc/hosts >/dev/null
else
  echo -e "   ${GREEN}✅ Domains bereits vorhanden${RESET}"
fi
echo

# --- 3️⃣ Caddy prüfen ---
bold "🧱 Prüfe Caddy (User Mode) ..."
if ! systemctl --user is-active --quiet caddy; then
  echo -e "   ${YELLOW}➕ Starte Caddy im User-Mode ...${RESET}"
  systemctl --user daemon-reload || true
  systemctl --user enable --now caddy.service || true
else
  echo -e "   ${GREEN}✅ Caddy läuft bereits${RESET}"
fi
echo

# --- 4️⃣ Docker & Compose Check ---
bold "🐳 Prüfe Docker & Compose ..."
if ! docker ps >/dev/null 2>&1; then
  echo -e "   ${RED}❌ Docker-Daemon läuft nicht oder keine Berechtigung!${RESET}"
  echo "   👉 Bitte 'sudo usermod -aG docker $USER' ausführen und neu einloggen."
  exit 1
fi

if ! docker compose version >/dev/null 2>&1; then
  echo -e "   ${RED}❌ Docker Compose fehlt. Bitte das CLI-Plugin installieren!${RESET}"
  exit 1
fi
echo -e "   ${GREEN}✅ Docker & Compose verfügbar${RESET}\n"

# --- 5️⃣ Repair-Modus ---
if [[ "$REPAIR_MODE" == "--repair" ]]; then
  bold "🧹 REPAIR-MODUS aktiviert"
  echo "   → Stoppe und entferne Dev-Container, Images & Volumes..."
  make down || true
  docker system prune -af --volumes >/dev/null
  docker network prune -f >/dev/null
  docker volume prune -f >/dev/null
  echo -e "   ${GREEN}✅ Alles bereinigt${RESET}\n"

  echo "🧱 Baue Container neu auf ..."
  docker compose --profile dev build --no-cache
  echo -e "   ${GREEN}✅ Neuaufbau abgeschlossen${RESET}\n"
fi

# --- 6️⃣ Stack starten ---
bold "🚀 Starte Dev-Stack ..."
cd "$PROJECT_ROOT"
make up || true

echo
bold "🕒 Warte kurz auf Container-Start..."
sleep 6
echo

# --- 7️⃣ Status-Panel ---
bold "──────────────────────────────"
bold "📊 Workmate Service Status"
bold "──────────────────────────────"

SERVICES=("kit_db" "kit_backend" "kit_ui" "kit_adminer")
STATUS_OK=true

for SVC in "${SERVICES[@]}"; do
  STATE=$(docker ps --format '{{.Names}}:{{.Status}}' | grep "$SVC" || true)
  if [[ -n "$STATE" ]]; then
    ICON="${GREEN}✅${RESET}"
    MSG="$(echo "$STATE" | cut -d: -f2)"
    status_line "$ICON" "$SVC" "$MSG"
  else
    ICON="${RED}❌${RESET}"
    status_line "$ICON" "$SVC" "nicht gefunden / gestoppt"
    STATUS_OK=false
  fi
done

# Prüfe Caddy separat
if systemctl --user is-active --quiet caddy; then
  status_line "${GREEN}✅${RESET}" "caddy" "läuft (User-Service)"
else
  status_line "${RED}❌${RESET}" "caddy" "gestoppt"
  STATUS_OK=false
fi

bold "──────────────────────────────"
if [ "$STATUS_OK" = true ]; then
  echo -e "${GREEN}🟢 Alle Dienste laufen stabil!${RESET}"
else
  echo -e "${YELLOW}⚠️  Einige Dienste sind nicht aktiv. Logs prüfen mit:${RESET}"
  echo "   → make be-logs"
  echo "   → docker logs kit_ui -f"
fi
bold "──────────────────────────────"

echo
echo -e "🔗 ${BLUE}UI:${RESET}   https://ui.workmate.test"
echo -e "🔗 ${BLUE}API:${RESET}  https://api.workmate.test/healthz"
echo
if [[ "$REPAIR_MODE" == "--repair" ]]; then
  echo -e "🧩 Hinweis: Reparaturmodus hat alle Container, Volumes & Images neu erstellt."
  echo "   Verwende './dev-setup-check.sh' ohne Parameter für den nächsten Start."
fi
echo
bold "✅ Setup abgeschlossen!"
echo
