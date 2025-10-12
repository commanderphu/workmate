// src/lib/keycloak.ts
import Keycloak from "keycloak-js";
console.log("🧠 Keycloak-Modul geladen")

// ====== Instanz ======
const keycloak = new Keycloak({
  url: "https://login.workmate.test/",
  realm: "kit",
  clientId: "workmate-ui",
});
console.log("🚀 Starte Keycloak init() …")

// ====== Initialisierung ======
export async function initKeycloak(onAuthenticatedCallback: () => void) {
  try {
    const authenticated = await keycloak.init({
      onLoad: "check-sso", // oder "login-required" wenn du Login erzwingen willst
      pkceMethod: "S256",
      checkLoginIframe: false,
      silentCheckSsoRedirectUri: window.location.origin + "/silent-check-sso.html",
      redirectUri: window.location.origin,
    });

    if (!authenticated) {
      console.log("🟡 Benutzer nicht eingeloggt → leite zur Login-Seite weiter…");
      await keycloak.login();
    } else {
      console.log("🟢 Eingeloggt als:", keycloak.tokenParsed?.preferred_username);
      onAuthenticatedCallback();
      scheduleTokenRefresh();
    }
  } catch (err) {
    console.error("❌ Keycloak init error:", err);
  }
}

// ====== Token abrufen ======
export function getToken(): string | undefined {
  return keycloak.token;
}

// ====== Logout ======
export function logout() {
  keycloak.logout({ redirectUri: window.location.origin });
}

// ====== Token automatisch refreshen ======
function scheduleTokenRefresh() {
  const refreshInterval = 60 * 1000; // alle 60 Sekunden prüfen
  setInterval(async () => {
    try {
      const refreshed = await keycloak.updateToken(70); // 70 Sek. vor Ablauf refresh
      if (refreshed) {
        console.log("🔄 Token automatisch erneuert");
      }
    } catch (err) {
      console.error("⚠️ Token konnte nicht aktualisiert werden:", err);
    }
  }, refreshInterval);
}

export default keycloak;
