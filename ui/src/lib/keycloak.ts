import Keycloak from 'keycloak-js'

console.log('🧠 Keycloak-Modul geladen')

// 🧩 Monkey-Patch: Deaktiviere Third-Party-Cookie-Test komplett
;(window as any).Keycloak = Keycloak
if (Keycloak && (Keycloak as any).prototype) {
  ;(Keycloak as any).prototype.check3pCookiesSupported = async function () {
    console.warn('⚙️  3rd-Party-Cookie-Check deaktiviert (Browserkompatibilität)')
    return Promise.resolve(true)
  }
}

// ====== Instanz ======
const keycloak = new Keycloak({
  url: 'https://login.workmate.test',
  realm: 'kit',
  clientId: 'workmate-ui',
})
console.log('🚀 Starte Keycloak init() …')

// ====== Initialisierung ======
export async function initKeycloak(onAuthenticatedCallback: () => void) {
  try {
    const authenticated = await keycloak.init({
      onLoad: 'login-required',
      pkceMethod: 'S256',
      checkLoginIframe: false,
      silentCheckSsoRedirectUri: `${window.location.origin}/silent-check-sso.html`,
      redirectUri: window.location.href,
    })

    if (window.location.hash.includes('state=') || window.location.hash.includes('code=')) {
      history.replaceState(null, '', window.location.pathname)
    }

    if (authenticated) {
      console.log('🟢 Eingeloggt als:', keycloak.tokenParsed?.preferred_username)
      onAuthenticatedCallback()
      scheduleTokenRefresh()
    } else {
      console.warn('🔒 Nicht authentifiziert – leite zu Login um …')
      await keycloak.login({ redirectUri: window.location.href })
    }
  } catch (err) {
    console.error('❌ Keycloak init error:', err)
  }
}

// ====== Token abrufen ======
export function getToken(): string | undefined {
  return keycloak.token
}

// ====== Logout ======
export function logout() {
  keycloak.logout({ redirectUri: window.location.origin })
}

// ====== Token automatisch refreshen ======
function scheduleTokenRefresh() {
  const refreshInterval = 60 * 1000 // alle 60 Sekunden prüfen
  setInterval(async () => {
    try {
      const refreshed = await keycloak.updateToken(70)
      if (refreshed) console.log('🔄 Token automatisch erneuert')
    } catch (err) {
      console.error('⚠️ Token konnte nicht aktualisiert werden:', err)
      // Wenn Token abläuft → erneuter Login
      keycloak.login({ redirectUri: window.location.href })
    }
  }, refreshInterval)
}

export default keycloak
