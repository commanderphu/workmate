<script setup lang="ts">
import { ref, onMounted, computed } from "vue"
import { apiFetch } from "@/lib/api"
import { useAuth } from "@/composables/useAuth"

const props = defineProps<{ doc: any; userRole?: string }>()
const emit = defineEmits(["close", "updated"])

const { canApprove, dbUser } = useAuth()

const canEditStatus = computed(() =>
  canApprove.value ||
  ["hr", "management"].includes((props.userRole || "").toLowerCase())
)

const local = ref({
  ...props.doc,
  comment: props.doc.comment || "",
})

const types = ref<string[]>([])
const loading = ref(false)
const error = ref<string | null>(null)

onMounted(async () => {
  try {
    const res = await apiFetch.get("/documents/types")
    types.value = res.data || []
  } catch (err) {
    console.error("⚠️ Fehler beim Laden der Dokumenttypen:", err)
    types.value = ["sonstige"]
  }
})

async function save() {
  loading.value = true
  error.value = null
  try {
    const payload: Record<string, any> = {
      document_type: local.value.document_type?.toLowerCase(),
      notes: local.value.notes,
      is_original_required: local.value.is_original_required,
    }

    if (canEditStatus.value) {
      payload.status = local.value.status
      payload.comment = local.value.comment
    }

    await apiFetch.put(`/documents/${local.value.id}`, payload)
    emit("updated")
    emit("close")
  } catch (err: any) {
    console.error("❌ Fehler beim Speichern:", err)
    error.value = "Fehler beim Speichern – bitte erneut versuchen."
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div
    class="fixed inset-0 bg-black/70 flex items-center justify-center z-50"
    @click.self="$emit('close')"
  >
    <div class="modal">
      <h3 class="title">Dokument bearbeiten</h3>

      <div v-if="error" class="state error mb-2">{{ error }}</div>

      <div>
        <label class="label">Titel</label>
        <input
          v-model="local.title"
          disabled
          class="input disabled"
        />
      </div>

      <div>
        <label class="label">Typ</label>
        <select v-model="local.document_type" class="input">
          <option
            v-for="t in types"
            :key="t"
            :value="t"
          >
            {{ t.charAt(0).toUpperCase() + t.slice(1).replace('_', ' ') }}
          </option>
        </select>
      </div>

      <div>
        <label class="label">Notiz</label>
        <textarea
          v-model="local.notes"
          rows="2"
          class="input resize-none"
        ></textarea>
      </div>

      <label class="flex items-center gap-2 text-white/80">
        <input type="checkbox" v-model="local.is_original_required" />
        <span>Original erforderlich</span>
      </label>

      <!-- 🧾 HR / Management -->
      <template v-if="canEditStatus">
        <div class="divider space-y-2">
          <label class="label">Status</label>
          <select v-model="local.status" class="input">
            <option value="pending">⏳ Ausstehend</option>
            <option value="approved">✅ Genehmigt</option>
            <option value="rejected">⛔ Abgelehnt</option>
          </select>

          <label class="label">Kommentar (optional)</label>
          <textarea
            v-model="local.comment"
            rows="2"
            class="input resize-none"
          ></textarea>
        </div>
      </template>

      <div class="flex justify-end gap-3 pt-3">
        <button @click="$emit('close')" class="btn-cancel">Abbrechen</button>
        <button @click="save" :disabled="loading" class="btn-save">
          {{ loading ? "Speichert…" : "Speichern" }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal {
  @apply bg-[#1b1d25]/95 rounded-xl p-6 w-[420px] text-white space-y-4 border border-white/10 shadow-xl shadow-black/50 backdrop-blur-md;
}
.title {
  @apply text-lg font-semibold mb-1;
}
.label {
  @apply block text-sm text-white/70 mb-1;
}
.input {
  @apply w-full bg-[#0f121a] rounded p-2 border border-white/10 text-white/80 focus:border-white/30 outline-none transition;
}
.input.disabled {
  @apply opacity-60 cursor-not-allowed;
}
.divider {
  @apply border-t border-white/10 pt-3 mt-3;
}
.btn-cancel {
  @apply text-white/70 hover:text-white transition;
}
.btn-save {
  @apply bg-[var(--color-accent)] hover:bg-orange-400 text-black font-semibold rounded px-4 py-2 shadow-[0_0_15px_rgba(255,145,0,0.3)] transition disabled:opacity-50;
}
.state {
  @apply text-sm text-white/70 bg-[#1b1d25] border border-white/10 rounded-md px-4 py-2 text-center;
}
.state.error {
  @apply text-rose-400 border-rose-500/40;
}
</style>
