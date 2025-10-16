<template>
  <div
    class="fixed bottom-20 right-6 bg-black/60 backdrop-blur-xl border border-white/10 rounded-2xl p-4 w-56 shadow-lg z-50 text-white"
  >
    <h3 class="text-sm font-semibold mb-3 text-center tracking-wide">🖥 Hintergrund</h3>
    <div class="flex flex-col gap-2">
      <button
        v-for="preset in presets"
        :key="preset"
        :class="[
          'px-3 py-2 rounded-lg transition-colors text-left',
          backgroundPreset === preset ? 'bg-white/20 border border-white/40' : 'hover:bg-white/10',
        ]"
        @click="setBackgroundPreset(preset)"
      >
        {{ preset.charAt(0).toUpperCase() + preset.slice(1) }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useSystemSettings } from '@/composables/useSystemSettings'

const presets = ref(['default', 'aurora', 'grid'])
const { backgroundPreset, setBackgroundPreset } = useSystemSettings()
</script>
