<template>
  <div class="fixed inset-0 bg-black/70 flex items-center justify-center z-50"
     @click.self="$emit('close')">

    <div class="bg-[#1a1d26] rounded-xl p-6 w-[400px] space-y-4 text-white">
      <h3 class="text-lg font-semibold">Dokument hochladen</h3>

      <input type="file" @change="e=>file=e.target.files[0]" class="w-full text-white"/>

      <select v-model="docType" class="w-full bg-[#0f121a] border border-white/20 rounded p-2">
        <option value="">– Typ wählen –</option>
        <option v-for="t in types" :key="t" :value="t">{{ labels[t] ?? t }}</option>
      </select>

      <textarea v-model="note" placeholder="Notiz…" class="w-full bg-[#0f121a] border border-white/20 rounded p-2"></textarea>

      <label class="flex items-center gap-2">
        <input type="checkbox" v-model="isOriginal" />
        <span>Original erforderlich</span>
      </label>

      <div class="flex justify-end gap-3 pt-2">
        <button @click="$emit('close')" class="text-white/70 hover:text-white">Abbrechen</button>
        <button @click="upload" :disabled="uploading"
                class="bg-[#ff9100] hover:bg-[#ffae33] text-black font-semibold rounded px-4 py-2">
          {{ uploading ? 'Lädt…' : 'Hochladen' }}
        </button>
      </div>

      <p v-if="error" class="text-red-400 text-sm">{{ error }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref,onMounted } from "vue"
import { api, apiFetch } from "@/lib/api"


const props = defineProps<{ employeeId: string }>()
const emit = defineEmits(["close","uploaded"])

const file = ref<File|null>(null)
const docType = ref("")
const note = ref("")
const isOriginal = ref(false)
const uploading = ref(false)
const error = ref<string|null>(null)
const types = ref<string[]>([])// Platzhalter
const labels: Record<string,string> = {
  bewerbung: "Bewerbung",
  krankenkasse: "Krankenkasse",
  urlaub_bescheinigung: "Urlaubsbescheinigung",
  attest: "Attest",
  urlaubsantrag: "Urlaubsantrag",
  fehlzeit: "Fehlzeit",
  sonstige: "Sonstige"
}


async function upload() {
  if (!file.value) return error.value = "Bitte Datei auswählen."
  if (!docType.value) return error.value = "Bitte Dokumenttyp wählen."

  uploading.value = true
  error.value = null

  try {
    const form = new FormData()
    form.append("file", file.value)
    form.append("document_type", docType.value)
    form.append("notes", note.value || "")
    form.append("is_original_required", isOriginal.value ? "true" : "false")

    const res = await apiFetch.post(`/documents/upload/${props.employeeId}`, form, {
      headers: { "Content-Type": "multipart/form-data" },
    })

    console.log("✅ Upload erfolgreich:", res.data)
    emit("uploaded")
    emit("close")
  } catch (e: any) {
    console.error("❌ Upload fehlgeschlagen:", e)
    error.value = e?.message ?? "Upload fehlgeschlagen."
  } finally {
    uploading.value = false
  }
}


onMounted(async () =>{
    try{
        const res =await apiFetch.get("/documents/types")
        types.value = res.data
    } catch (e){types.value=["sonstige"]}
})
</script>
