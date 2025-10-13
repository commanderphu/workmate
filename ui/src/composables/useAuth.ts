// ui/src/composables/useAuth.ts
import { ref, computed } from "vue"
import keycloak, { getToken, logout as kcLogout } from "@/lib/keycloak"
import { api, apiFetch } from "@/lib/api"
import router from "@/router"

const user = ref<any>(null)
const token = ref<string | undefined>()
const isReady = ref(false)
const dbUser = ref<any>(null)

export function useAuth() {
  const isAuthenticated = computed(() => !!user.value)
  const isDbLinked = computed(() => !!dbUser.value)

  /**
   * Initialisiert Authentifizierung + lädt den verknüpften DB-Benutzer
   * Wird in main.ts nach Keycloak-Init aufgerufen
   */
  async function initAuth() {
    console.log("🧠 useAuth.initAuth() start")

    // Keycloak-Daten übernehmen
    if (!isReady.value) {
      token.value = getToken()
      user.value = keycloak.tokenParsed || null
      isReady.value = true
      console.log("✅ Keycloak ready:", user.value?.preferred_username)
    }

    // 🧩 Jetzt den DB-Benutzer abrufen
    try {
      const res = await apiFetch.get("/employees/me")
      dbUser.value = res.data
      console.log("👤 Datenbank-Benutzer geladen:", dbUser.value)

      // ------------------------------------------------------------
      // 🔹 Auto-Redirect nur, wenn User wirklich auf "/" ist
      //    (nicht bei Reload einer anderen Seite!)
      // ------------------------------------------------------------
      const currentPath = window.location.pathname
      console.log(currentPath)
      if (currentPath === "/" && dbUser.value?.employee_id) {
        console.log("➡️ Redirect von / auf Dashboard:", dbUser.value.employee_id)
        await router.replace(`/dashboard/employee/${dbUser.value.employee_id}`)
      }
    } catch (err: any) {
      console.warn("⚠️ Kein DB-Benutzer für aktuellen Keycloak-User:", err.response?.status)
      dbUser.value = null
    }

    // ------------------------------------------------------------
    // 🔹 Kein DB-User vorhanden → Setup-Seite
    // ------------------------------------------------------------
    if (!dbUser.value) {
      console.log("➡️ Kein Eintrag in der DB -> Redirect to /setup")
      router.push("/setup")
    }
  }

  /**
   * Login über Keycloak
   */
  async function login() {
    console.log("🔐 Redirecting to Keycloak login…")
    await keycloak.login()
  }

  /**
   * Logout über Keycloak
   */
  async function logout() {
    console.log("👋 Logging out…")
    await kcLogout()
    user.value = null
    dbUser.value = null
    token.value = undefined
  }

  return {
    user,
    dbUser,
    token,
    isReady,
    isAuthenticated,
    isDbLinked,
    initAuth,
    login,
    logout,
  }
}
