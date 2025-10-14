<script setup lang="ts">
import { ref, computed, onMounted, watch } from "vue"
import { apiFetch } from "@/lib/api"
import { useAuth } from "@/composables/useAuth"

const { canApprove, canManage } = useAuth()

// 🧾 State
const documents = ref<any[]>([])
const loading = ref(false)
const search = ref("")
const selectedStatus = ref("all")
const selectedType = ref("all")

// 🧮 KPI-Zähler
const stats = ref({
  total: 0,
  pending: 0,
  approved: 0,
  rejected: 0,
})

// 🔁 API-Aufruf
async function fetchDocuments() {
  loading.value = true
  try {
    const res = await apiFetch.get("/documents")
    documents.value = res.data

    // KPI zählen
    stats.value.total = res.data.length
    stats.value.pending = res.data.filter((d: any) => d.status === "pending").length
    stats.value.approved = res.data.filter((d: any) => d.status === "approved").length
    stats.value.rejected = res.data.filter((d: any) => d.status === "rejected").length
  } catch (err) {
    console.error("❌ Fehler beim Laden der Dokumente:", err)
  } finally {
    loading.value = false
  }
}

// 🔍 Filterlogik
const filteredDocuments = computed(() => {
  return documents.value.filter((doc) => {
    const matchesSearch =
      !search.value ||
      doc.title?.toLowerCase().includes(search.value.toLowerCase()) ||
      doc.document_type?.toLowerCase().includes(search.value.toLowerCase())

    const matchesStatus =
      selectedStatus.value === "all" || doc.status === selectedStatus.value

    const matchesType =
      selectedType.value === "all" || doc.document_type === selectedType.value

    return matchesSearch && matchesStatus && matchesType
  })
})

// 🔄 Auto-Reload bei Filteränderung
watch([search, selectedStatus, selectedType], () => {
  // kein separater fetch nötig, da alles clientseitig
}, { deep: true })

onMounted(fetchDocuments)
</script>

<template>
  <section class="space-y-6 py-8">
    <!-- 🧠 KPI Cards -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div
        v-for="(count, key) in stats"
        :key="key"
        class="rounded-xl p-4 bg-[#1a1d26] border border-white/10 shadow-md text-center"
      >
        <p class="text-sm text-white/60 uppercase tracking-wider">
          {{ key }}
        </p>
        <p
          class="text-2xl font-bold"
          :class="{
            'text-yellow-400': key === 'pending',
            'text-green-400': key === 'approved',
            'text-red-400': key === 'rejected',
            'text-white': key === 'total',
          }"
        >
          {{ count }}
        </p>
      </div>
    </div>

    <!-- 🔍 Filter -->
    <div class="flex flex-wrap gap-4 items-center">
      <input
        v-model="search"
        type="text"
        placeholder="Suchen…"
        class="bg-[#0f121a] text-white placeholder-white/40 border border-white/10 rounded-lg px-3 py-2 w-full md:w-64"
      />

      <select
        v-model="selectedStatus"
        class="bg-[#0f121a] text-white border border-white/10 rounded-lg px-3 py-2"
      >
        <option value="all">Status (alle)</option>
        <option value="pending">⏳ Ausstehend</option>
        <option value="approved">✅ Genehmigt</option>
        <option value="rejected">⛔ Abgelehnt</option>
      </select>

      <select
        v-model="selectedType"
        class="bg-[#0f121a] text-white border border-white/10 rounded-lg px-3 py-2"
      >
        <option value="all">Typ (alle)</option>
        <option
          v-for="t in [...new Set(documents.map((d) => d.document_type).filter(Boolean))]"
          :key="t"
          :value="t"
        >
          {{ t }}
        </option>
      </select>

      <button
        @click="fetchDocuments"
        class="bg-[#ff9100] hover:bg-[#ffae33] text-black font-semibold rounded-lg px-4 py-2"
      >
        Neu laden
      </button>
    </div>

    <!-- 📋 Tabelle -->
    <div class="overflow-x-auto rounded-lg border border-white/10 bg-[#1a1d26]">
      <table class="min-w-full text-sm text-white/80">
        <thead class="bg-white/5 text-white/70 uppercase text-xs">
          <tr>
            <th class="px-4 py-2 text-left">Titel</th>
            <th class="px-4 py-2 text-left">Typ</th>
            <th class="px-4 py-2 text-left">Mitarbeiter</th>
            <th class="px-4 py-2 text-left">Upload</th>
            <th class="px-4 py-2 text-left">Status</th>
            <th class="px-4 py-2 text-left">Aktionen</th>
          </tr>
        </thead>

        <tbody>
          <tr
            v-for="doc in filteredDocuments"
            :key="doc.id"
            class="border-t border-white/10 hover:bg-white/5 transition-colors"
          >
            <td class="px-4 py-2 font-medium text-white/90">
              {{ doc.title || "—" }}
            </td>
            <td class="px-4 py-2">{{ doc.document_type || "—" }}</td>
            <td class="px-4 py-2">{{ doc.employee_name || "—" }}</td>
            <td class="px-4 py-2 whitespace-nowrap">
              {{ doc.upload_date ? new Date(doc.upload_date).toLocaleDateString() : "—" }}
            </td>
            <td class="px-4 py-2">
              <span
                class="px-2 py-1 rounded-full text-xs font-semibold"
                :class="{
                  'bg-yellow-500/20 text-yellow-400': doc.status === 'pending',
                  'bg-green-500/20 text-green-400': doc.status === 'approved',
                  'bg-red-500/20 text-red-400': doc.status === 'rejected',
                  'bg-white/10 text-white/60': !doc.status,
                }"
              >
                {{ doc.status || "—" }}
              </span>
            </td>
            <td class="px-4 py-2">
              <a
                v-if="doc.file_url"
                :href="doc.file_url"
                target="_blank"
                class="text-[#ff9100] hover:text-[#ffae33] font-semibold"
              >
                Download
              </a>
            </td>
          </tr>

          <tr v-if="!filteredDocuments.length && !loading">
            <td colspan="6" class="p-6 text-center text-white/50">
              Keine Dokumente gefunden 🤷‍♂️
            </td>
          </tr>

          <tr v-if="loading">
            <td colspan="6" class="p-6 text-center text-white/50">
              Lädt Dokumente…
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>
