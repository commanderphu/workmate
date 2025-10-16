<script setup lang="ts">
import { RouterLink, useRoute } from "vue-router"
import { ref, onMounted, onBeforeUnmount } from "vue"
import { useAuth } from "@/composables/useAuth"
import { useHealth } from "@/composables/useHealth"
import { useTheme } from "@/composables/useTheme"
import UserBar from "@/components/UserBar.vue"
import { API_BASE_URL } from "@/lib/api"

const route = useRoute()
const { canManage, dbUser } = useAuth()
const { systems, register, refreshAll, colorForStatus } = useHealth()

const { isDark, toggleTheme } = useTheme()
const scrollY = ref(0)
const blurLevel = ref(6)
const shadowIntensity = ref(0.6)

onMounted(() => {
  const handleScroll = () => {
    scrollY.value = window.scrollY
    const maxScroll = 200 // nach 200px Scroll maximale „Tiefe“

    // 🌀 Blur verringern leicht beim Scrollen
    blurLevel.value = Math.max(3, 6 - (scrollY.value / maxScroll) * 3)

    // 🪶 Schatten wird sanfter beim Scrollen
    shadowIntensity.value = Math.max(0.3, 0.6 - (scrollY.value / maxScroll) * 0.3)
  }

  window.addEventListener("scroll", handleScroll)
  handleScroll()
  onBeforeUnmount(() => window.removeEventListener("scroll", handleScroll))
})

// 🧩 Rolle bestimmen
const role = (dbUser.value?.department || "employee").toLowerCase()

// 🧭 Navigationseinträge
const items = [
  { label: "Dashboard", to: "/dashboard", roles: ["all"] },
  { label: "HR", to: "/hr", roles: ["hr", "backoffice", "management"] },
  { label: "Audits", to: "/admin/audits", roles: ["management", "admin"] },
]


// 🧮 Sichtbarkeit prüfen
function isVisible(item: any) {
  return (
    item.roles.includes("all") ||
    item.roles.includes(role) ||
    (canManage && item.roles.includes("management"))
  )
}

// 🪄 Scroll-Effekt
const isScrolled = ref(false)
onMounted(() => {
  const onScroll = () => (isScrolled.value = window.scrollY > 10)
  window.addEventListener("scroll", onScroll)
  onScroll()
  onBeforeUnmount(() => window.removeEventListener("scroll", onScroll))
})

// 🧭 Aktiver Tab (mit Subroute-Check)
function isActive(item: any) {
  if (item.to === "/") return route.path === "/"
  return route.path.startsWith(item.to)
}



// 🧠 Health-Systeme initial registrieren
onMounted(() => {
  register([
    {
      key: "api",
      label: "API",
      url: `${API_BASE_URL}/api/health`,
    },
    {
      key: "ui",
      label: "UI",
      url: `${API_BASE_URL}/api/ui`,
    },
    {
      key: "auth",
      label: "Auth",
      url: `${API_BASE_URL}/api/keycloak`,
    },
  ])

  // Optional: gleich beim Start aktualisieren
  refreshAll()
})


</script>

<template>
  <header
  :class="[
    'dock-header dock-floating fixed top-4 left-1/2 -translate-x-1/2 z-40 w-[94%] max-w-6xl h-[72px] border border-white/10 rounded-2xl transition-all duration-300',
    route.path.startsWith('/dashboard') || route.path.startsWith('/hr') || route.path.startsWith('/admin')
      ? 'backdrop-blur-md'
      : '',
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
          :src="
            isDark
              ? '/workmate_dark_transparent.png'
              : '/workmate_white_transparent.png'
          "
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
          <!-- ✳️ System Health (nur für Management/Admin) -->
            <div
              v-if="canManage && systems.length"
              class="hidden lg:flex items-center gap-3 text-xs text-white/70 mr-2"
            >
              <span
                v-for="s in systems"
                :key="s.key"
                class="inline-flex items-center gap-1"
              >
                <span
                  class="inline-block h-2 w-2 rounded-full"
                  :class="colorForStatus(s.status)"
                />
                {{ s.label }}
              </span>
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

/* Hover lift effect */
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
