<script setup lang="ts">
import { onMounted, watch } from "vue"
import { useRoute } from "vue-router"
import { useTheme } from "@/composables/useTheme"
import { useHealth } from "@/composables/useHealth"
import DockHeader from "@/components/layout/DockHeader.vue"

const route = useRoute()
const { isDark } = useTheme()
const { register } = useHealth()

watch(() => route.meta?.title, (title) => {
  document.title = title ? `Workmate | ${title}` : "Workmate"
}, { immediate: true })

onMounted(() => {
  const apiBase = import.meta.env.VITE_API_URL || window.location.origin
  register([
    { key: "backend", label: "Backend", url: `${apiBase}/api/health` },
    { key: "keycloak", label: "Keycloak", url: `${apiBase}/api/keycloak` },
    { key: "ui", label: "UI", url: `${apiBase}/api/ui` },
  ])
})
</script>

<template>
  <div :class="[isDark ? 'dark' : 'light']" class="min-h-screen flex flex-col">
    <!-- Schwebendes Dock, NICHT fixed -->
    <DockHeader class="dock-floating" />

    <!-- Inhalt: exakt eine zentrale Breite -->
    <main>
      <div class="container-page">
        <RouterView />
      </div>
    </main>
  </div>
</template>

<style>
main { transition: opacity .25s ease, transform .25s ease; }
</style>
