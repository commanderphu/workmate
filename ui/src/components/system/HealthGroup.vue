<!-- src/components/system/HealthGroup.vue -->
<script setup lang="ts">
import { ref, onMounted } from "vue"
import axios from "axios"

interface System {
  label: string
  url: string
}

const props = defineProps<{ systems: System[] }>()

const statuses = ref<Record<string, "ok" | "down" | "degraded" | "loading">>({})
const details = ref<Record<string, string>>({})

async function checkSystem(sys: System) {
  statuses.value[sys.label] = "loading"
  try {
    const res = await axios.get(sys.url, { timeout: 4000 })
    const s = res.data?.status?.toLowerCase?.() ?? "down"
    statuses.value[sys.label] = ["ok", "degraded"].includes(s) ? (s as any) : "down"
    details.value[sys.label] = res.data?.reason || res.data?.error || "OK"
  } catch (e: any) {
    statuses.value[sys.label] = "down"
    details.value[sys.label] = e.message ?? "Unbekannter Fehler"
  }
}

onMounted(() => {
  props.systems.forEach(sys => checkSystem(sys))
  // alle 30 Sekunden neu prüfen
  setInterval(() => props.systems.forEach(sys => checkSystem(sys)), 30000)
})
</script>

<template>
  <div class="flex items-center gap-4 select-none">
    <div
      v-for="sys in props.systems"
      :key="sys.label"
      class="flex items-center gap-2 group relative"
    >
      <!-- Statuspunkt -->
      <span
        class="inline-block w-3 h-3 rounded-full shadow-md transition-all duration-300"
        :class="{
          'bg-emerald-400 shadow-emerald-400/40': statuses[sys.label] === 'ok',
          'bg-amber-400 shadow-amber-400/40 animate-pulse': statuses[sys.label] === 'degraded',
          'bg-rose-500 shadow-rose-500/40 animate-pulse': statuses[sys.label] === 'down',
          'bg-white/40 animate-pulse': statuses[sys.label] === 'loading'
        }"
      ></span>

      <!-- Label -->
      <span class="text-xs text-white/70 group-hover:text-[#ff9100] transition">
        {{ sys.label }}
      </span>

      <!-- Tooltip -->
      <div
        class="absolute bottom-full mb-2 left-1/2 -translate-x-1/2 px-2 py-1 rounded-md text-xs text-white bg-black/80 border border-white/10 opacity-0 group-hover:opacity-100 pointer-events-none transition"
      >
        {{ details[sys.label] || statuses[sys.label] }}
      </div>
    </div>
  </div>
</template>

<style scoped>
.group:hover span.w-3 {
  filter: drop-shadow(0 0 6px rgba(255,145,0,0.6));
}
</style>
