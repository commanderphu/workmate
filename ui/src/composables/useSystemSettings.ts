// src/composables/useSystemSettings.ts
import { ref, watch } from 'vue'

const STORAGE_KEY = 'workmate:system:backgroundPreset'
const backgroundPreset = ref<string>(localStorage.getItem(STORAGE_KEY) || 'default')

// Persistenz
watch(backgroundPreset, (val) => {
  localStorage.setItem(STORAGE_KEY, val)
})

export function useSystemSettings() {
  function setBackgroundPreset(preset: string) {
    backgroundPreset.value = preset
  }

  return {
    backgroundPreset,
    setBackgroundPreset,
  }
}
