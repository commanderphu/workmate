<script setup lang="ts">
import { ref, onMounted, computed } from "vue"
import { api } from "@/lib/api"
import UploadModal from "@/components/documents/UploadModal.vue"
import EditModal from "@/components/documents/EditModal.vue"

const props = defineProps<{ employeeId: string }>()
const emit = defineEmits<{ (e: "audit", action: string, docId?: string): void }>()

// State
const showUpload = ref(false)
const editDoc = ref<any | null>(null)
const items = ref<any[]>([])
const loading = ref(true)
const error = ref<string | null>(null)
const busy = ref<Record<string, boolean>>({})
const q = ref("")

// Filter
const filtered = computed(() => {
  const query = q.value.trim().toLowerCase()
  if (!query) return items.value
  return items.value.filter((d) =>
    [d.title, d.document_type, d.status].some((f) =>
      (f ?? "").toLowerCase().includes(query)
    )
  )
})

// Helpers
function fmtDate(d?: string | null) {
  if (!d) return "–"
  try {
    return new Date(d).toLocaleDateString("de-DE")
  } catch {
    return d
  }
}

function badge(s?: string) {
  switch (s) {
    case "approved":
      return "bg-emerald-600/30 text-emerald-300 shadow-[0_0_6px_rgba(16,185,129,0.4)]"
    case "rejected":
      return "bg-red-600/25 text-red-300 shadow-[0_0_6px_rgba(239,68,68,0.4)]"
    case "pending":
    default:
      return "bg-white/10 text-white/70"
  }
}

// 📥 Load
async function load() {
  loading.value = true
  error.value = null
  try {
    const data = await api.listDocuments(props.employeeId)
    items.value = [...data].sort((a, b) => b.upload_date?.localeCompare(a.upload_date) ?? 0)
  } catch (e: any) {
    error.value = e?.message ?? "Fehler beim Laden der Dokumente."
  } finally {
    loading.value = false
  }
}

// 🗑️ Delete
async function removeItem(id: string) {
  if (!confirm("Dieses Dokument wirklich löschen?")) return
  busy.value[id] = true
  try {
    await api.deleteDocument(id)
    items.value = items.value.filter((d) => d.id !== id)
    emit("audit", "delete", id)
  } catch (e: any) {
    error.value = e?.message ?? "Löschen fehlgeschlagen."
  } finally {
    delete busy.value[id]
  }
}

onMounted(load)
</script>

<template>
  <div class="doc-card">
    <!-- 🔹 Header -->
    <div class="header">
      <div class="flex items-center gap-3 min-w-0">
        <h3 class="title">Dokumente</h3>
        <input
          v-model="q"
          type="text"
          placeholder="Suchen…"
          class="search"
        />
      </div>

      <button @click="showUpload = true" class="btn-accent">+ Neues Dokument</button>
    </div>

    <!-- 📦 Zustände -->
    <div v-if="loading" class="state">📦 Lade Dokumente…</div>
    <div v-else-if="error" class="state error">{{ error }}</div>

    <!-- 📂 Inhalt -->
    <div v-else>
      <div v-if="filtered.length === 0" class="empty">
        <div class="icon">📄</div>
        <div class="text-white font-medium mb-1">Noch keine Dokumente</div>
        <p class="text-white/70 text-sm">Lade dein erstes Dokument hoch.</p>
      </div>

      <div v-else class="table-wrapper">
        <table class="doc-table">
          <thead>
            <tr>
              <th>Titel</th>
              <th>Typ</th>
              <th>Upload</th>
              <th>Status</th>
              <th class="text-right">Aktionen</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="d in filtered" :key="d.id" class="row">
              <td>{{ d.title }}</td>
              <td class="text-white/80">{{ d.document_type ?? "–" }}</td>
              <td class="text-white/80">{{ fmtDate(d.upload_date) }}</td>
              <td>
                <span :class="['badge', badge(d.status)]">
                  <span v-if="d.status === 'approved'">✅</span>
                  <span v-else-if="d.status === 'rejected'">⛔</span>
                  <span v-else>⏳</span>
                  <span class="capitalize">{{ d.status ?? "pending" }}</span>
                </span>
              </td>
              <td>
                <div class="actions">
                  <button @click="editDoc = d" class="btn-blue">🖊 Bearbeiten</button>

                  <a
                    v-if="d.file_url"
                    :href="d.file_url"
                    target="_blank"
                    class="btn-gray"
                    title="Herunterladen"
                  >
                    ⬇️ Download
                  </a>

                  <button
                    :disabled="busy[d.id]"
                    @click="removeItem(d.id)"
                    class="btn-red"
                  >
                    {{ busy[d.id] ? "…" : "🗑 Löschen" }}
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 📤 Upload & Edit -->
    <UploadModal
      v-if="showUpload"
      :employee-id="props.employeeId"
      @close="showUpload = false"
      @uploaded="() => { showUpload = false; load(); emit('audit', 'upload') }"
    />

    <EditModal
      v-if="editDoc"
      :doc="editDoc"
      @close="editDoc = null"
      @updated="() => { editDoc = null; load(); emit('audit', 'edit', editDoc?.id) }"
    />
  </div>
</template>

<style scoped>
.doc-card {
  @apply w-full rounded-xl border border-white/10 bg-[#1b1d25]/90 p-6 shadow-lg shadow-black/30 space-y-5 backdrop-blur-md;
}

/* Header */
.header {
  @apply grid items-center gap-3 grid-cols-1 lg:grid-cols-[1fr_auto];
}
.title {
  @apply text-lg font-semibold text-white;
}
.search {
  @apply rounded-lg bg-[#0f121a] text-white placeholder-white/40 border border-white/10 px-3 py-2 outline-none focus:border-white/30 w-[160px] sm:w-[360px] md:w-[420px] max-w-full;
}

/* Buttons */
.btn-accent {
  @apply bg-[var(--color-accent)] hover:bg-orange-400 text-black font-semibold rounded-lg px-5 py-2 transition shadow-[0_0_15px_rgba(255,145,0,0.3)];
}
.btn-blue {
  @apply px-3 py-1 rounded-md bg-blue-500/80 hover:bg-blue-500 text-white transition;
}
.btn-red {
  @apply px-3 py-1 rounded-md bg-red-500/85 hover:bg-red-500 text-white transition disabled:opacity-40;
}
.btn-gray {
  @apply px-3 py-1 rounded-md bg-white/10 hover:bg-white/15 text-white transition;
}

/* Table */
.table-wrapper {
  @apply overflow-x-auto rounded-lg border border-white/10;
  max-height: 55vh;
}
.doc-table {
  @apply w-full text-sm border-collapse;
}
.doc-table thead {
  @apply bg-white/5 text-white/80 border-b border-white/10;
}
.doc-table th,
.doc-table td {
  @apply px-3 py-2 text-left align-middle;
}
.row {
  @apply hover:bg-white/5 transition even:bg-white/[0.02];
}
.badge {
  @apply inline-flex items-center gap-1 px-2 py-1 rounded-md text-xs font-medium;
}

/* Empty */
.empty {
  @apply rounded-lg border border-white/10 bg-white/5 p-10 text-center;
}
.icon {
  @apply mx-auto mb-3 h-12 w-12 grid place-content-center rounded-full bg-blue-500/15 text-blue-300 text-xl;
}

/* State */
.state {
  @apply text-white/70 text-sm bg-[#1b1d25] border border-white/10 rounded-xl px-6 py-4 text-center;
  animation: pulse 1.6s infinite ease-in-out;
}
.state.error {
  @apply text-rose-400 border-rose-500/40;
}
@keyframes pulse {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 1; }
}

/* Actions */
.actions {
  @apply flex items-center justify-end gap-2 md:gap-3 flex-wrap;
}
</style>
