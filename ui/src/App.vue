<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useTheme } from '@/composables/useTheme'
import { useHealth } from '@/composables/useHealth'
import { useSystemSettings } from '@/composables/useSystemSettings'
import DockHeader from '@/components/layout/DockHeader.vue'
import SystemBackground from '@/components/SystemBackground.vue'
import SettingsPanel from '@/components/SettingPanel.vue'

const route = useRoute()
const { isDark } = useTheme()
const { register } = useHealth()
const { backgroundPreset } = useSystemSettings()
const showSettings = ref(false)

// 🧭 Titel dynamisch anpassen
watch(
  () => route.meta?.title,
  (title) => {
    document.title = title ? `Workmate | ${title}` : 'Workmate'
  },
  { immediate: true }
)

// 🩺 Health Monitoring
onMounted(() => {
  const apiBase = import.meta.env.VITE_API_URL || window.location.origin
  register([
    { key: 'backend', label: 'Backend', url: `${apiBase}/api/health` },
    { key: 'keycloak', label: 'Keycloak', url: `${apiBase}/api/keycloak` },
    { key: 'ui', label: 'UI', url: `${apiBase}/api/ui` },
  ])
})
</script>

<template>
  <div class="relative h-screen overflow-hidden">
    <!-- 🖥 Hintergrund -->
    <SystemBackground :preset="backgroundPreset" />

    <!-- 🧱 Hauptstruktur -->
    <div
      :class="[isDark ? 'dark' : 'light']"
      class="flex flex-col h-full overflow-hidden relative z-10"
    >
      <DockHeader class="dock-floating shrink-0" />

      <main class="flex-1 overflow-y-auto overflow-x-hidden relative">
        <!-- Wichtig: min-h-full → verhindert unnötiges Scrollen -->
        <div class="container-page w-full max-w-7xl mx-auto px-6 py-10 min-h-full">
          <RouterView />
        </div>
      </main>
    </div>

    <!-- ⚙️ Button -->
    <button
      class="fixed bottom-6 right-6 p-3 rounded-full bg-black/60 backdrop-blur-md border border-white/20 text-white hover:bg-white/10 transition z-50"
      @click="showSettings = !showSettings"
    >
      ⚙️
    </button>

    <!-- ⚙️ Settings Panel -->
    <transition name="fade">
      <SettingsPanel v-if="showSettings" />
    </transition>
  </div>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
