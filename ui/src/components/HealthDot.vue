<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from "vue"
import { apiFetch } from "@/lib/api"

type Status = "ok" | "degraded" | "down" | "loading"
const status = ref<Status>("loading")

let timer: number | undefined
let controller: AbortController | undefined

async function checkHealth() {
  // frühere Requests abbrechen
  controller?.abort()
  controller = new AbortController()

  try {
    const res = await apiFetch("/api/health", {
      cache: "no-store",
      signal: controller.signal,
      headers: { Accept: "application/json" },
    })
    // res ist bereits JSON (siehe apiFetch)
    const s = (res?.status || res?.state || "").toString().toLowerCase()
    status.value = s === "ok" ? "ok" : s === "degraded" ? "degraded" : "down"
  } catch {
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
  <span
    :title="status === 'ok' ? 'System OK' : status === 'degraded' ? 'Eingeschränkt' : status === 'down' ? 'Nicht erreichbar' : 'Lade…'"
    class="inline-flex items-center gap-2"
  >
    <span
      :class="[
        'inline-block h-2.5 w-2.5 rounded-full',
        status === 'ok' ? 'bg-emerald-400' :
        status === 'degraded' ? 'bg-amber-400' :
        status === 'down' ? 'bg-rose-500' : 'bg-white/40 animate-pulse'
      ]"
    />
    <span class="text-xs text-white/70 capitalize hidden sm:inline">
      {{ status }}
    </span>
  </span>
</template>
