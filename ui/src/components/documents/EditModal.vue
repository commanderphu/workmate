<script setup lang="ts">
import { ref, onMounted, computed } from "vue"
import { api, apiFetch } from "@/lib/api"
import { useAuth, } from "@/composables/useAuth"
// Enums / Mappings
const STATUS_LABELS: Record<string, string> = {
  pending: "⏳ Ausstehend",
  approved: "✅ Genehmigt",
  rejected: "⛔ Abgelehnt",
}

type DocumentStatus = keyof typeof STATUS_LABELS

interface DocumentOut {
  id: string
  title: string
  document_type?: string
  notes?: string
  is_original_required: boolean
  status: DocumentStatus
  comment?: string
}
const { canApprove,dbUser } = useAuth()

// Optionaler Fallback falls canApprove nicht verfügbar
const canEditStatus = computed(() => {
  return canApprove.value || props.userRole === "HR" || props.userRole === "Management"
})


const props = defineProps<{ doc: any, userRole?:string}>()
const emit = defineEmits(["close", "updated"])

const local = ref<DocumentOut>({
  ...props.doc,
  comment: props.doc.comment || "",
})
const types = ref<string[]>([])



onMounted(async () => {
  try {
    const res = await apiFetch.get("/documents/types")
    types.value = res.data
  } catch {
    types.value = ["sonstige"]
  }
})

async function save() {
  if (!local.value) return

  const payload: Record<string, any> = {
    document_type: local.value.document_type,
    notes: local.value.notes,
    is_original_required: local.value.is_original_required,
  }

  // Nur Management/HR darf Status/Kommentar ändern
  if (canEditStatus.value) {
    payload.status = local.value.status
    payload.comment = local.value.comment
  }

  console.table(payload) // Debug → zeig dir im Browser den Payload

  try {
    await apiFetch.put(`/documents/${local.value.id}`, payload)
    emit("updated")
    emit("close")
  } catch (err) {
    console.error("❌ Fehler beim Speichern:", err)
  }
}

</script>

<template>
  <div class="fixed inset-0 bg-black/70 flex items-center justify-center z-50"
     @click.self="$emit('close')">

    <div class="bg-[#1a1d26] rounded-xl p-6 w-[420px] text-white space-y-4">
      <h3 class="text-lg font-semibold">Dokument bearbeiten</h3>

      <div>
        <label class="block text-sm text-white/70">Titel</label>
        <input
          v-model="local.title"
          disabled
          class="w-full bg-[#0f121a] rounded p-2 border border-white/10 text-white/80"
        />
      </div>

      <div>
        <label class="block text-sm text-white/70">Typ</label>
        <select
          v-model="local.document_type"
          class="w-full bg-[#0f121a] rounded p-2 border border-white/10"
        >
          <option v-for="t in types" :key="t" :value="t">{{ t }}</option>
        </select>
      </div>

      <div>
        <label class="block text-sm text-white/70">Notiz</label>
        <textarea
          v-model="local.notes"
          rows="2"
          class="w-full bg-[#0f121a] rounded p-2 border border-white/10"
        ></textarea>
      </div>

      <label class="flex items-center gap-2 text-white/80">
        <input type="checkbox" v-model="local.is_original_required" />
        <span>Original erforderlich</span>
      </label>

      <!-- 🧾 Nur für HR & Management -->
      <template v-if="canEditStatus">
        <div class="border-t border-white/10 pt-3 space-y-2">
          <label class="block text-sm text-white/70">Status</label>
          <select
            v-model="local.status"
            class="w-full bg-[#0f121a] rounded p-2 border border-white/10"
            >
                <option
                    v-for="(label, key) in STATUS_LABELS"
                    :key="key"
                    :value="key"
                >
                    {{ label }}
                </option>
            </select>


          <label class="block text-sm text-white/70">Kommentar (optional)</label>
          <textarea
            v-model="local.comment"
            rows="2"
            class="w-full bg-[#0f121a] rounded p-2 border border-white/10"
          ></textarea>
        </div>
      </template>

      <div class="flex justify-end gap-3 pt-2">
        <button @click="$emit('close')" class="text-white/70 hover:text-white">
          Abbrechen
        </button>
        <button
          @click="save"
          class="bg-[#ff9100] hover:bg-[#ffae33] text-black font-semibold rounded px-4 py-2"
        >
          Speichern
        </button>
      </div>
    </div>
  </div>
</template>
