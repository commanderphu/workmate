<script setup lang="ts">
import { ref, onMounted, computed } from "vue"
import { api } from "@/lib/api"
import UploadModal from "@/components/documents/UploadModal.vue"
import EditModal from "@/components/documents/EditModal.vue"
const showUpload = ref(false)


const props = defineProps<{ employeeId: string }>()

const loading = ref(true)
const error = ref<string | null>(null)
const q = ref("")
const items = ref<any[]>([])
const busy = ref<Record<string, boolean>>({})
const uploading = ref(false)
const uploadError = ref<string | null>(null)
const editDoc = ref<any | null>(null)

const filtered = computed(() => {
  const query = q.value.trim().toLowerCase()
  if (!query) return items.value
  return items.value.filter(d =>
    (d.title ?? "").toLowerCase().includes(query) ||
    (d.document_type ?? "").toLowerCase().includes(query) ||
    (d.status ?? "").toLowerCase().includes(query)
  )
})

function fmtDate(d?: string | null) {
  if (!d) return "–"
  try {
    return new Date(d).toLocaleDateString()
  } catch {
    return d
  }
}

function badge(s?: string) {
  switch (s) {
    case "approved":
      return "bg-emerald-600/30 text-emerald-300"
    case "rejected":
      return "bg-red-600/25 text-red-300"
    case "pending":
      return "bg-white/10 text-white/70"
    default:
      return "bg-white/10 text-white/70"
  }
}

async function load() {
  loading.value = true
  error.value = null
  try {
    const data = await api.listDocuments(props.employeeId)
    items.value = [...data].sort((a, b) => {
      if (!a.upload_date || !b.upload_date) return 0
      return b.upload_date.localeCompare(a.upload_date)
    })
  } catch (e: any) {
    error.value = e?.message ?? "Fehler beim Laden der Dokumente."
  } finally {
    loading.value = false
  }
}


// 🗑️ Löschen
async function removeItem(id: string) {
  if (!confirm("Dieses Dokument wirklich löschen?")) return
  busy.value[id] = true
  try {
    await api.deleteDocument(id)
    items.value = items.value.filter(d => d.id !== id)
  } catch (e: any) {
    error.value = e?.message ?? "Löschen fehlgeschlagen."
  } finally {
    delete busy.value[id]
  }
}
const labels: Record<string,string> = {
  bewerbung: "Bewerbung",
  krankenkasse: "Krankenkasse",
  urlaub_bescheinigung: "Urlaubsbescheinigung",
  attest: "Attest",
  urlaubsantrag: "Urlaubsantrag",
  fehlzeit: "Fehlzeit",
  sonstige: "Sonstige"
}

onMounted(load)
</script>

<template>
  <div class="w-full rounded-xl border border-white/5 bg-[#1a1d26] p-5 shadow-lg shadow-black/30 space-y-5">
    <!-- Header -->
    <div class="grid items-center gap-3 grid-cols-1 lg:grid-cols-[1fr_auto]">
      <div class="flex items-center gap-3 min-w-0">
        <h3 class="text-lg font-semibold text-white shrink-0">Dokumente</h3>
        <input
          v-model="q"
          type="text"
          placeholder="Suchen…"
          class="rounded-lg bg-[#0f121a] text-white placeholder-white/40 border border-white/10 px-3 py-2 outline-none focus:border-white/30 w-[150px] sm:w-[360px] md:w-[420px] max-w-full"
        />
      </div>

      <button @click="showUpload = true"
  class="justify-self-start lg:justify-self-end bg-[#ff9100] hover:bg-[#ffae33] text-black font-semibold rounded-lg px-5 py-2 transition">
  + Neues Dokument
      </button>

      <UploadModal
        v-if="showUpload"
        :employee-id="props.employeeId"
        @close="showUpload=false"
        @uploaded="load()"
      />

    </div>

    <!-- Status / Fehler -->
    <div v-if="loading" class="text-white/70">Lade…</div>
    <div v-else-if="error" class="text-rose-400 text-sm whitespace-pre-wrap">{{ error }}</div>
    <div v-else-if="uploadError" class="text-rose-400 text-sm whitespace-pre-wrap">{{ uploadError }}</div>

    <!-- Inhalt -->
    <div v-else>
      <!-- Empty -->
      <div v-if="filtered.length === 0" class="rounded-lg border border-white/10 bg-white/5 p-10 text-center">
        <div class="mx-auto mb-3 h-12 w-12 grid place-content-center rounded-full bg-blue-500/15 text-blue-300 text-xl">📄</div>
        <div class="text-white font-medium mb-1">Noch keine Dokumente</div>
        <p class="text-white/70 text-sm">Lade dein erstes Dokument hoch.</p>
      </div>

      <!-- Tabelle -->
      <div v-else class="overflow-hidden rounded-lg border border-white/10">
        <table class="w-full text-sm">
          <thead class="bg-white/5 text-white/80">
            <tr>
              <th class="text-left px-3 py-2 font-medium">Titel</th>
              <th class="text-left px-3 py-2 font-medium">Typ</th>
              <th class="text-left px-3 py-2 font-medium">Upload</th>
              <th class="text-left px-3 py-2 font-medium">Status</th>
              <th class="text-right px-3 py-2 font-medium">Aktionen</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-white/10">
            <tr v-for="d in filtered" :key="d.id" class="hover:bg-white/5">
              <td class="px-3 py-2 text-white whitespace-nowrap">{{ d.title }}</td>
              <td class="px-3 py-2 text-white/80">{{ d.document_type ?? "–" }}</td>
              <td class="px-3 py-2 text-white/80">{{ fmtDate(d.upload_date) }}</td>
              <td class="px-3 py-2">
                <span :class="['inline-flex items-center gap-1 px-2 py-1 rounded-md text-xs font-medium', badge(d.status)]">
                  <span v-if="d.status === 'approved'">✅</span>
                  <span v-else-if="d.status === 'rejected'">⛔</span>
                  <span v-else>⏳</span>
                  <span class="capitalize">{{ d.status ?? "pending" }}</span>
                </span>
              </td>
              <td class="px-3 py-2">
                <div class="flex items-center justify-end gap-2 md:gap-3 flex-wrap">
                  <button
                  @click="editDoc = d"
                  class="px-3 py-1 rounded-md bg-blue-500/80 hover:bg-blue-500 text-white transition"
                >🖊 Bearbeiten</button>
                <EditModal
                  v-if="editDoc"
                  :doc="editDoc"
                  :user-role="dbUser?.role"
                  @close="editDoc = null"
                  @updated="load()"
                />


                  <a
                    v-if="d.file_url"
                    :href="d.file_url"
                    target="_blank"
                    class="px-3 py-1 rounded-md bg-white/10 hover:bg-white/15 text-white transition"
                    title="Herunterladen"
                  >
                    ⬇️ Download
                  </a>
                  <button
                    class="px-3 py-1 rounded-md bg-red-500/85 hover:bg-red-500 text-white transition disabled:opacity-40"
                    :disabled="busy[d.id]"
                    @click="removeItem(d.id)"
                  >
                    {{ busy[d.id] ? '…' : '🗑 Löschen' }}
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
