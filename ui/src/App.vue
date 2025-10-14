<script setup lang="ts">
import { useHealth } from "@/composables/useHealth"
import HealthGroup from "@/components/system/HealthGroup.vue"
import UserBar from "@/components/UserBar.vue"
import { useTheme } from "@/composables/useTheme"
import { ref, onMounted } from "vue"

const { isDark, toggleTheme } = useTheme()

// 🧠 origin sicher auslesen (nur im Browser)
const { systems, register } = useHealth()

register([
  { key: "backend", label: "Backend", url: "https://api.workmate.test/api/health" },
  { key: "keycloak", label: "Keycloak", url: "https://api.workmate.test/api/keycloak" },
  { key: "ui", label: "UI", url: "https://api.workmate.test/api/ui" },
])

</script>

<template>
  <div>
    <header
      class="sticky top-0 z-10 backdrop-blur bg-white/80 dark:bg-brand-bg/90 
         border-b border-black/5 dark:border-white/5 
         shadow-[0_0_20px_rgba(255,145,0,0.2)]"
    >
      <div class="container-page flex items-center justify-between py-5">
        <!-- 🔹 Logo -->
        <RouterLink to="/" class="flex items-center gap-3 select-none">
          <img
            :src="isDark ? '/workmate_dark_transparent.png' : '/workmate_white_transparent.png'"
            alt="Workmate Logo"
            class="h-20 w-auto drop-shadow-[0_0_20px_rgba(255,145,0,0.7)] transition-all duration-300 select-none"
          />
        </RouterLink>

        <!-- 🔧 Right Side (Theme + Status + User) -->
        <div class="flex items-center gap-5">
          <!-- 🌗 Theme Toggle -->
          <button
            @click="toggleTheme"
            class="flex items-center justify-center w-9 h-9 rounded-full border border-white/10 bg-brand-accent/10 text-brand-accent hover:bg-brand-accent/20 hover:scale-105 transition-all duration-300"
            :title="isDark ? 'Wechsel zu Light Mode' : 'Wechsel zu Dark Mode'"
          >
            <span v-if="isDark">☀️</span>
            <span v-else>🌙</span>
          </button>

          <!-- 💡 Health Indicator -->
          <HealthGroup v-if="systems.length" :systems="systems" />

          <!-- 👤 User Menu / Logout -->
          <UserBar />
        </div>
      </div>
    </header>

    <main class="container-page">
      <RouterView />
    </main>
  </div>
</template>
