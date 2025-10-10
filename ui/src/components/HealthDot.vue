<script setup lang="ts">
import { ref, onMounted } from "vue"

type Status = "ok" | "degraded" | "down" | "loading"
const status = ref<Status>("loading")

onMounted(async () => {
  try {
    const r = await fetch("/api/health", { cache: "no-store" })
    const j = await r.json()
    if (j.status === "ok") status.value = "ok"
    else status.value = "degraded"
  } catch {
    status.value = "down"
  }
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
      {{ status }}
    </span>
  </div>
</template>
