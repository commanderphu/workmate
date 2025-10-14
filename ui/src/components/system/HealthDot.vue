<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from "vue"
import axios from "axios"

type Status = "ok" | "degraded" | "down" | "loading"

const props = defineProps<{
  url: string            // Health-Endpoint, z. B. /healthz oder https://api.meinedomain.de/health
  label?: string         // Anzeigename im UI
  interval?: number      // Prüfintervall in ms (Standard: 15000)
}>()

const status = ref<Status>("loading")
let timer: number | undefined

async function checkHealth() {
  try {
    const res = await axios.get(props.url, { timeout: 4000 })
    const s = (res.data?.status || res.data?.state || "").toString().toLowerCase()
    status.value = s === "ok" ? "ok" : s === "degraded" ? "degraded" : "down"
  } catch {
    status.value = "down"
  }
}

onMounted(() => {
  checkHealth()
  timer = window.setInterval(checkHealth, props.interval ?? 15000)
})
onBeforeUnmount(() => {
  if (timer) clearInterval(timer)
})
</script>

<template>
  <span
    class="inline-flex items-center gap-2"
    :title="`${props.label ?? 'System'}: ${
      status === 'ok'
        ? 'OK'
        : status === 'degraded'
        ? 'Eingeschränkt'
        : status === 'down'
        ? 'Nicht erreichbar'
        : 'Lade…'
    }`"
  >
    <span
      :class="[
        'inline-block h-2.5 w-2.5 rounded-full',
        status === 'ok'
          ? 'bg-emerald-400'
          : status === 'degraded'
          ? 'bg-amber-400'
          : status === 'down'
          ? 'bg-rose-500'
          : 'bg-white/40 animate-pulse'
      ]"
    />
    <span class="text-xs text-white/70 hidden sm:inline">
      {{ props.label ?? "Unbenannt" }}
    </span>
  </span>
</template>
