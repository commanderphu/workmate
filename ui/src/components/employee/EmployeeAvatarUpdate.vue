<script setup lang="ts">
import { ref, computed, watch } from "vue"
import { api } from "@/lib/api"
import md5 from "blueimp-md5"

// Props
const props = defineProps<{
  email?: string
  name: string
  employeeId: string
  avatarUrl?: string
}>()

const emit = defineEmits<{
  (e: "update", file: File): void
  (e: "error", message: string): void
}>()

// State
const uploading = ref(false)
const fileInput = ref<HTMLInputElement | null>(null)
const currentUrl = ref<string | null>(props.avatarUrl || null)
const uploadError = ref<string | null>(null)

// 🌀 Gravatar fallback
const gravatarUrl = computed(() => {
  const base = props.email?.trim().toLowerCase() || props.name || props.employeeId
  const hash = md5(base)
  return `https://www.gravatar.com/avatar/${hash}?d=identicon&s=160`
})

// 🖼️ Anzeigepriorität
const displayUrl = computed(() => currentUrl.value || gravatarUrl.value)

// 🔼 Upload-Handler
async function onFileSelected(e: Event) {
  const target = e.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return

  uploading.value = true
  uploadError.value = null

  try {
    const res = await api.uploadAvatar(props.employeeId, file)
    // Cache umgehen → sofort neues Bild laden
    currentUrl.value = `${res.avatar_url}?t=${Date.now()}`
    emit("update", file)
  } catch (err: any) {
    const message = err.message ?? "Fehler beim Hochladen des Avatars."
    uploadError.value = message
    emit("error", message)
    console.error("Avatar-Upload fehlgeschlagen:", err)
  } finally {
    uploading.value = false
  }
}

// 📁 Klick auf Avatar → Datei-Auswahl öffnen
function triggerUpload() {
  fileInput.value?.click()
}

// 🔄 Prop-Änderung übernehmen
watch(
  () => props.avatarUrl,
  (val) => {
    currentUrl.value = val || null
  }
)
</script>

<template>
  <div class="relative group w-fit">
    <!-- Avatar -->
    <img
      :src="displayUrl"
      alt="Avatar"
      class="w-20 h-20 rounded-full object-cover border border-white/10 shadow-md shadow-black/40 cursor-pointer transition hover:opacity-80"
      @click="triggerUpload"
    />

    <!-- Overlay -->
    <div
      class="absolute inset-0 rounded-full bg-black/50 flex items-center justify-center opacity-0 group-hover:opacity-100 transition"
    >
      <span v-if="uploading" class="text-xs text-[#ff9100] animate-pulse">Lädt…</span>
      <span v-else class="text-xs text-[#ff9100]">Ändern</span>
    </div>

    <!-- Datei-Input -->
    <input
      ref="fileInput"
      type="file"
      accept="image/*"
      class="hidden"
      @change="onFileSelected"
    />

    <!-- Fehleranzeige -->
    <div v-if="uploadError" class="absolute -bottom-5 left-1/2 -translate-x-1/2 text-[11px] text-red-400 whitespace-nowrap">
      {{ uploadError }}
    </div>
  </div>
</template>

<style scoped>
/* Optional smoother transition */
img {
  transition: filter 0.2s ease, opacity 0.2s ease;
}
</style>
