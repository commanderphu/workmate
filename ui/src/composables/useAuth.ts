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

  async function initAuth() {
    console.log("🧠 useAuth.initAuth() start")

    if (!isReady.value) {
      token.value = getToken()
      user.value = keycloak.tokenParsed || null
      isReady.value = true
      console.log("✅ Keycloak ready:", user.value?.preferred_username)
    }

    // 🧩 jetzt Datenbank-User abrufen
    try {
      const res = await apiFetch.get("/employees/me")
      dbUser.value = res.data
      console.log("👤 Datenbank-Benutzer geladen:", dbUser.value)

      // Optional: Auto-Redirect
      if (router.currentRoute.value.path === "/" && dbUser.value.employee_id) {
        await router.push(`/dashboard/employee/${dbUser.value.employee_id}`)
      }
    } catch (err: any) {
      console.warn("⚠️ Kein DB-Benutzer für aktuellen Keycloak-User:", err.response?.status)
      dbUser.value = null
    }
    if (!dbUser.value){
    console.log("➡️ Kein Eintrag in der DB -> Redirect to /setup")
    router.push("/setup")
    }
  }

  async function login() {
    console.log("🔐 Redirecting to Keycloak login…")
    await keycloak.login()
  }

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
