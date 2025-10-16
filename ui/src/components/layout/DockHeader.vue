<script setup lang="ts">
import { RouterLink, useRoute } from "vue-router"
import { ref, onMounted, onBeforeUnmount } from "vue"
import { useAuth } from "@/composables/useAuth"
import { useHealth } from "@/composables/useHealth"
import { useTheme } from "@/composables/useTheme"
import UserBar from "@/components/UserBar.vue"
import { API_BASE_URL } from "@/lib/api"

const route = useRoute()
const { dbUser } = useAuth()
const { systems, register, refreshAll } = useHealth()
const { isDark, toggleTheme } = useTheme()

// 🧩 Rolle bestimmen
const role = (dbUser.value?.department || "employee").toLowerCase()

// 🧭 Navigationseinträge
const items = [
  { label: "Dashboard", to: "/dashboard" },
  { label: "HR", to: "/hr" },
  { label: "Audits", to: "/admin/audits" },
]

// ✅ Sichtbarkeit anhand Rolle
function isVisible(item: any) {
  const r = role
  if (item.to === "/dashboard") return true
  if (item.to === "/hr" && ["hr", "backoffice", "management"].includes(r)) return true
  if (item.to.startsWith("/admin") && ["management", "admin"].includes(r)) return true
  return false
}

// ✅ Aktiver Tab prüfen
function isActive(item: any) {
  const path = route.path
  if (item.to === "/dashboard")
    return path.startsWith("/dashboard") || path.startsWith("/employee")
  if (item.to === "/hr") return path.startsWith("/hr")
  if (item.to.startsWith("/admin")) return path.startsWith("/admin")
  return false
}

// 🪄 Scroll-Effekte
const blurLevel = ref(6)
const shadowIntensity = ref(0.6)
const isScrolled = ref(false)

onMounted(() => {
  const handleScroll = () => {
    const scrollY = window.scrollY
    const maxScroll = 200
    blurLevel.value = Math.max(3, 6 - (scrollY / maxScroll) * 3)
    shadowIntensity.value = Math.max(0.3, 0.6 - (scrollY / maxScroll) * 0.3)
    isScrolled.value = scrollY > 10
  }
  window.addEventListener("scroll", handleScroll)
  handleScroll()
  onBeforeUnmount(() => window.removeEventListener("scroll", handleScroll))
})

// 🧠 Health-Systeme registrieren
onMounted(() => {
  register([
    { key: "api", label: "API", url: `${API_BASE_URL}/api/health` },
    { key: "ui", label: "UI", url: `${API_BASE_URL}/api/ui` },
    { key: "auth", label: "Auth", url: `${API_BASE_URL}/api/keycloak` },
  ])
  refreshAll()
})
</script>

<template>
  <header
    :class="[
      'dock-header dock-floating fixed top-4 left-1/2 -translate-x-1/2 z-40 w-[94%] max-w-6xl h-[72px] border border-white/10 rounded-2xl transition-all duration-300 backdrop-blur-md',
    ]"
    :style="{
      backdropFilter: `blur(${blurLevel}px)`,
      boxShadow: `0 8px 25px rgba(0,0,0,${shadowIntensity}), 0 0 25px rgba(255,145,0,${shadowIntensity / 3})`,
      backgroundColor: `rgba(0,0,0,${isScrolled ? 0.35 : 0.4})`,
      transform: isScrolled ? 'translate(-50%, 0) scale(0.985)' : 'translate(-50%, 0)',
    }"
  >
    <div class="flex items-center justify-between h-full px-6">
      <!-- ░▒▓ BRAND ▓▒░ -->
      <RouterLink to="/" class="flex items-center select-none">
        <img
          :src="isDark ? '/workmate_dark_transparent.png' : '/workmate_white_transparent.png'"
          alt="Workmate Logo"
          class="h-10 md:h-11 w-auto transition-transform duration-300 hover:scale-[1.05] drop-shadow-[0_0_14px_rgba(255,145,0,0.7)]"
        />
      </RouterLink>

      <!-- ░▒▓ NAVIGATION ▓▒░ -->
      <nav class="hidden md:flex items-center gap-6 text-[15px] font-medium">
        <RouterLink
          v-for="i in items.filter(isVisible)"
          :key="i.to"
          :to="i.to"
          class="relative px-2 py-1 transition-all duration-300"
          :class="{
            'text-[var(--color-accent)] font-semibold active-link': isActive(i),
            'text-white/70 hover:text-white/90': !isActive(i),
          }"
        >
          {{ i.label }}
        </RouterLink>
      </nav>

      <!-- ░▒▓ RECHTS ▓▒░ -->
      <div class="flex items-center gap-4">
        <!-- ✳️ Health nur für Admin/Management -->
        <div
          v-if="['management','admin'].includes(role) && systems.length"
          class="hidden sm:flex items-center gap-4 text-xs text-white/70"
        >
          <div
            v-for="s in systems"
            :key="s.key"
            class="relative group"
          >
            <span class="inline-flex items-center gap-1 cursor-help">
              <span
                class="inline-block h-2 w-2 rounded-full transition-colors duration-300"
                :class="{
                  'bg-emerald-400': s.status === 'ok',
                  'bg-amber-400': s.status === 'degraded',
                  'bg-red-500': s.status === 'down',
                  'bg-white/30 animate-pulse': s.status === 'loading'
                }"
              />
              {{ s.label }}
            </span>

            <!-- 🪶 Tooltip -->
            <div
              class="absolute top-full left-1/2 -translate-x-1/2 mt-2 hidden group-hover:flex flex-col items-center bg-black/90 text-white text-xs rounded-lg px-3 py-2 border border-white/10 shadow-lg backdrop-blur-sm whitespace-nowrap z-50 opacity-0 group-hover:opacity-100 transition-opacity duration-200"
            >
              <div class="font-semibold mb-0.5">
                {{ s.label.toUpperCase() }} —
                <span
                  :class="{
                    'text-emerald-400': s.status === 'ok',
                    'text-amber-400': s.status === 'degraded',
                    'text-red-400': s.status === 'down',
                    'text-white/70': s.status === 'loading'
                  }"
                >
                  {{ s.status.toUpperCase() }}
                </span>
              </div>
              <div class="text-white/70 max-w-[220px] text-center leading-snug">
                {{ s.details || 'Keine Details verfügbar' }}
              </div>
              <div class="text-[10px] text-white/40 mt-1">
                {{ s.lastCheck ? new Date(s.lastCheck).toLocaleTimeString() : '–' }}
              </div>
              <div class="absolute bottom-full left-1/2 -translate-x-1/2 w-2 h-2 bg-black/90 border-r border-b border-white/10 rotate-[225deg] mb-[1px]"></div>
            </div>
          </div>
        </div>

        <!-- 🌗 Theme Toggle -->
        <button
          @click="toggleTheme"
          class="w-9 h-9 rounded-full border border-white/10 bg-[var(--color-accent)]/10 text-[var(--color-accent)] hover:bg-[var(--color-accent)]/20 hover:scale-105 transition"
          :title="isDark ? 'Light Mode' : 'Dark Mode'"
        >
          <span v-if="isDark">☀️</span>
          <span v-else>🌙</span>
        </button>

        <!-- 👤 UserBar -->
        <UserBar />
      </div>
    </div>
  </header>
</template>

<style scoped>
/* =======================================================
   🧭 DOCK HEADER — Floating Refined Edition
======================================================= */
.dock-header {
  box-shadow:
    0 8px 25px rgba(0, 0, 0, 0.5),
    0 0 25px rgba(255, 145, 0, 0.1);
  transition: all 0.3s ease;
}
.dock-header:hover {
  background-color: rgba(0, 0, 0, 0.45);
  box-shadow:
    0 12px 32px rgba(0, 0, 0, 0.55),
    0 0 30px rgba(255, 145, 0, 0.12);
}

/* 🌈 Active Link Styling */
.active-link::after {
  content: "";
  position: absolute;
  left: 50%;
  bottom: -4px;
  transform: translateX(-50%);
  width: 18px;
  height: 2px;
  border-radius: 9999px;
  background: linear-gradient(to right, var(--color-accent), #ffd180);
  box-shadow: 0 0 12px rgba(255, 145, 0, 0.4);
  transition: all 0.4s ease;
}

nav a {
  position: relative;
  transition: color 0.25s ease, transform 0.25s ease;
}
nav a:hover {
  transform: translateY(-1px);
}

/* Intro Animation */
.dock-floating {
  animation: fadeInDock 0.5s ease both;
}
@keyframes fadeInDock {
  from {
    opacity: 0;
    transform: translate(-50%, -10px);
  }
  to {
    opacity: 1;
    transform: translate(-50%, 0);
  }
}
</style>
