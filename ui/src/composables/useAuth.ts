// ui/src/composables/useAuth.ts
import { ref, computed, watchEffect } from 'vue'
import keycloak, { getToken, logout as kcLogout } from '@/lib/keycloak'
import { apiFetch } from '@/lib/api'
import router from '@/router'

const user = ref<any>(null)
const token = ref<string | undefined>()
const isReady = ref(false)
const dbUser = ref<any>(null)

export function useAuth() {
  const isAuthenticated = computed(() => !!user.value)
  const isDbLinked = computed(() => !!dbUser.value)

  // 🔹 Abgeleitete Rollenlogik
  const userRole = computed(() => {
    const dept = dbUser.value?.department?.toLowerCase()
    if (dept === 'management') return 'management'
    if (['hr', 'backoffice'].includes(dept)) return 'backoffice'
    if (['support', 'security'].includes(dept)) return 'admin'
    return 'employee'
  })
  const canApprove = computed(() => ['backoffice', 'management'].includes(userRole.value))
  const canManage = computed(() => ['management', 'admin'].includes(userRole.value))

  watchEffect(() => {
    console.log('🧩 Rolle:', userRole.value, ' | canApprove:', canApprove.value)
    console.log('🧩 Rolle:', userRole.value, ' | canManage:', canManage.value)
  })

  // ======================================================
  // 🧠 INIT AUTH: Keycloak laden + DB-User verknüpfen
  // ======================================================
  async function initAuth() {
    console.log('🧠 useAuth.initAuth() start')

    // --- Keycloak-Infos übernehmen ---
    if (!isReady.value) {
      token.value = getToken()
      user.value = keycloak.tokenParsed || null
      isReady.value = true
      console.log('✅ Keycloak ready:', user.value?.preferred_username)
    }

    // --- DB-Benutzer laden ---
    try {
      const res = await apiFetch.get('/employees/me')
      dbUser.value = res.data
      console.log('👤 Datenbank-Benutzer geladen:', dbUser.value)
    } catch (err: any) {
      console.warn('⚠️ Kein DB-Benutzer für aktuellen Keycloak-User:', err.response?.status)
      dbUser.value = null
    }

    // --- Fallback, falls kein DB-Eintrag existiert ---
    if (!dbUser.value && user.value) {
      dbUser.value = {
        name:
          user.value?.name ||
          `${user.value?.given_name ?? ''} ${user.value?.family_name ?? ''}`.trim() ||
          user.value?.preferred_username ||
          'Benutzer',
        department: 'employee',
        employee_id: 'KIT-0000',
      }
      console.log('🪄 Fallback-User erstellt:', dbUser.value)
    }

    // --- Redirect-Handling ---
    const currentPath = window.location.pathname
    if (currentPath === '/' && dbUser.value?.employee_id) {
      console.log('➡️ Redirect von / auf Dashboard:', dbUser.value.employee_id)
      await router.replace('/dashboard')
    }

    // --- Kein DB-User? Setup-Seite öffnen ---
    if (!dbUser.value?.employee_id || dbUser.value.employee_id === 'KIT-0000') {
      console.log('➡️ Kein vollständiger DB-User -> Setup')
      router.push('/setup')
    }
  }

  // ======================================================
  // 🔐 Login / Logout
  // ======================================================
  async function login() {
    console.log('🔐 Redirecting to Keycloak login…')
    await keycloak.login()
  }

  async function logout() {
    console.log('👋 Logging out…')
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
    userRole,
    canApprove,
    canManage,
  }
}
