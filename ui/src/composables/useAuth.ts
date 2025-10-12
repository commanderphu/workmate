import { ref, computed } from "vue"
import keycloak, { getToken, logout as kcLogout } from "@/lib/keycloak"

const user = ref<any>(null)
const token = ref<string | undefined>()
const isReady = ref(false)

export function useAuth() {
  const isAuthenticated = computed(() => !!user.value)

  async function initAuth() {
    console.log("🧠 useAuth.initAuth() start")
    if (!isReady.value) {
      token.value = getToken()
      user.value = keycloak.tokenParsed || null
      isReady.value = true
      console.log("✅ useAuth ready:", user.value?.preferred_username)
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
    token.value = undefined
  }

  return {
    user,
    token,
    isReady,
    isAuthenticated,
    initAuth,
    login,
    logout,
  }
}
