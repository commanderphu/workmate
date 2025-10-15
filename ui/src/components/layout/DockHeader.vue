<script setup lang="ts">
import { RouterLink, useRoute } from "vue-router"
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
  { label: "Dashboard", to: "/", roles: ["all"] },
  { label: "HR",        to: "/hr", roles: ["hr", "backoffice", "management"] },
  { label: "Audits",    to: "/admin/audits", roles: ["management", "admin"] },
]
</script>

<template>
  <header class="dock-floating">
    <div class="container-page flex items-center justify-between h-[72px]">
      <!-- ░▒▓ BRAND ▓▒░ -->
      <RouterLink to="/" class="flex items-center gap-2 select-none">
        <img
          :src="isDark ? '/workmate_dark_transparent.png' : '/workmate_white_transparent.png'"
          alt="Workmate Logo"
          class="h-9 w-auto drop-shadow-[0_0_10px_rgba(255,145,0,0.6)]"
        />
        <span class="font-semibold tracking-tight text-white/90">
          <span class="text-[var(--color-accent)]">K.I.T</span> Workmate
        </span>
      </RouterLink>

      <!-- ░▒▓ NAVIGATION ▓▒░ -->
      <nav class="flex items-center gap-6 text-sm">
        <RouterLink
          v-for="i in items.filter(it =>
              it.roles.includes('all') ||
              it.roles.includes(role) ||
              (canManage && it.roles.includes('management'))
            )"
          :key="i.to"
          :to="i.to"
          :class="[
            'transition-all duration-200 font-medium',
            route.path.startsWith(i.to)
              ? 'text-[var(--color-accent)] font-semibold'
              : 'text-white/70 hover:text-white'
          ]"
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

        <!-- ✳️ Health nur für Admin/Management -->
        <div
          v-if="canManage && systems.length"
          class="hidden sm:flex items-center gap-3 text-xs text-white/70"
        >
          <template v-for="s in systems" :key="s.key">
            <span class="inline-flex items-center gap-1">
              <span
                class="inline-block h-2 w-2 rounded-full"
                :class="s.status === 'ok' ? 'bg-emerald-400' : 'bg-red-500'"
              />
              {{ s.label }}
            </span>
          </template>
        </div>

        <!-- 👤 UserBar -->
        <UserBar />
      </div>
    </div>
  </header>
</template>

<style scoped>
/* =======================================================
   🧭 DOCK HEADER — WORKMATE ORIGINAL STYLE
======================================================= */
header.dock-floating {
  position: relative;
  width: 100%;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 1rem;
  box-shadow:
    0 10px 30px rgba(0,0,0,0.6),
    0 0 20px rgba(255,145,0,0.08);
  backdrop-filter: blur(6px);
  transition: box-shadow 0.3s, background 0.3s;
}
header.dock-floating:hover {
  background: var(--color-surface-hover);
  box-shadow:
    0 12px 34px rgba(0,0,0,0.68),
    0 0 28px rgba(255,145,0,0.12);
}

/* 🔹 Links / Hoverfarben */
nav a {
  text-decoration: none;
}
nav a.active {
  color: var(--color-accent);
}

/* Logo-Glow */
header img {
  filter: drop-shadow(0 0 10px rgba(255,145,0,0.6));
  transition: filter 0.3s;
}
header img:hover {
  filter: drop-shadow(0 0 16px rgba(255,145,0,0.8));
}
</style>
