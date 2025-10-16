<script setup lang="ts">
import { RouterLink, useRoute } from "vue-router"
import { ref, onMounted, onBeforeUnmount } from "vue"
import { useAuth } from "@/composables/useAuth"
import { useHealth } from "@/composables/useHealth"
import { useTheme } from "@/composables/useTheme"
import UserBar from "@/components/UserBar.vue"

const route = useRoute()
const { canManage, dbUser } = useAuth()
const { systems } = useHealth()
const { isDark, toggleTheme } = useTheme()

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
</script>

<template>
  <header
    :class="[
      'dock-header dock-floating fixed top-4 left-1/2 -translate-x-1/2 z-40',
      'w-[94%] max-w-6xl h-[72px] border border-white/10 rounded-2xl backdrop-blur-md transition-all duration-300',
      isScrolled
        ? 'bg-black/30 scale-[0.98] shadow-[0_6px_20px_rgba(0,0,0,0.5),0_0_20px_rgba(255,145,0,0.1)]'
        : 'bg-black/40 shadow-[0_8px_25px_rgba(0,0,0,0.6),0_0_25px_rgba(255,145,0,0.15)]',
    ]"
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
        <!-- 🌗 Theme Toggle -->
        <button
          @click="toggleTheme"
          class="w-9 h-9 rounded-full border border-white/10 bg-[var(--color-accent)]/10 text-[var(--color-accent)] hover:bg-[var(--color-accent)]/20 hover:scale-105 transition"
          :title="isDark ? 'Light Mode' : 'Dark Mode'"
        >
          <span v-if="isDark">☀️</span>
          <span v-else>🌙</span>
        </button>

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
