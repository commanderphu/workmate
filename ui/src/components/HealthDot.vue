<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from "vue"

type Status = "ok" | "degraded" | "down" | "loading"
const status = ref<Status>("loading")
let timer: number | undefined
let controller: AbortController | undefined

async function checkHealth() {
  const base = ("https://api.workmate.test")
  const url = `${base}/api/health`

  controller?.abort()
  controller = new AbortController()

  try {
    const res = await fetch(url, { cache: "no-store", signal: controller.signal, headers: { Accept: "application/json" } })
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const j = await res.json()
    // Mappe „ok/degraded/…“ robust (falls Backend andere Keys liefert)
    const s = (j.status || j.state || "").toString().toLowerCase()
    status.value = s === "ok" ? "ok" : s === "degraded" ? "degraded" : "down"
  } catch (e) {
    status.value = "down"
  }
}

onMounted(() => {
  checkHealth()
  timer = window.setInterval(checkHealth, 15000) // alle 15s
})
onBeforeUnmount(() => {
  if (timer) clearInterval(timer)
  controller?.abort()
})
</script>


<template>
  <div class="flex items-center gap-2">
    <span
      class="inline-block h-3 w-3 rounded-full transition-all duration-300 shadow-[0_0_6px_rgba(0,0,0,0.3)]"
      :class="{
        'bg-green-400 shadow-green-500/40': status === 'ok',
        'bg-yellow-400 shadow-yellow-400/40': status === 'degraded',
        'bg-red-500 shadow-red-500/40': status === 'down',
        'bg-white/30 animate-pulse': status === 'loading',
      }"
    />
    <span
      class="text-xs uppercase tracking-wide font-medium"
      :class="{
        'text-green-300': status === 'ok',
        'text-yellow-300': status === 'degraded',
        'text-red-400': status === 'down',
        'text-white/60': status === 'loading',
      }"
    >
      {{ status }} - Backend | DB Status
    </span>
  </div>
</template>
