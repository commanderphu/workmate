<script setup lang="ts">
import { ref, onMounted } from "vue"
import { apiFetch } from "@/lib/api"
import { useAuth } from "@/composables/useAuth"
import AuditLogTable from "@/components/admin/AuditLogTable.vue"

const { canManage } = useAuth()

// 📦 State
const logs = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const perPage = 25
const isLoading = ref(false)

// 🔍 Filter
const filters = ref({
  user_email: "",
  action: "",
  resource: "",
})

// 🔁 Daten laden
async function fetchLogs() {
  isLoading.value = true
  try {
    const res = await apiFetch.get("/admin/audits", {
      params: {
        skip: (page.value - 1) * perPage,
        limit: perPage,
        user_email: filters.value.user_email || undefined,
        action: filters.value.action || undefined,
        resource: filters.value.resource || undefined,
      },
    })

    console.log("📜 Audit Response:", res.data)

    total.value = res.data.total ?? 0
    logs.value = res.data.items ?? []
  } catch (err) {
    console.error("Fehler beim Laden der Audits:", err)
  } finally {
    isLoading.value = false
  }
}

// ⏭ Pagination
function nextPage() {
  if (page.value * perPage < total.value) {
    page.value++
    fetchLogs()
  }
}
function prevPage() {
  if (page.value > 1) {
    page.value--
    fetchLogs()
  }
}

// 📤 Export
function exportCsv() {
  window.open(`${import.meta.env.VITE_API_URL}/admin/audits/export`, "_blank")
}

onMounted(fetchLogs)
</script>

<template>
  <section class="space-y-6 py-8" v-if="canManage">
    <!-- 🔹 Header + Filter -->
    <div class="flex flex-wrap items-center justify-between gap-4">
      <h1 class="text-2xl font-bold text-white">📜 Audit Logs</h1>

      <div class="flex gap-3">
        <input
          v-model="filters.user_email"
          placeholder="E-Mail filtern"
          class="bg-[#0f121a] text-white border border-white/10 rounded px-3 py-2"
        />
        <input
          v-model="filters.action"
          placeholder="Aktion (approve, reject ...)"
          class="bg-[#0f121a] text-white border border-white/10 rounded px-3 py-2"
        />
        <input
          v-model="filters.resource"
          placeholder="Ressource"
          class="bg-[#0f121a] text-white border border-white/10 rounded px-3 py-2"
        />
        <button
          @click="fetchLogs"
          :disabled="isLoading"
          class="bg-[#ff9100] hover:bg-[#ffae33] text-black font-semibold rounded px-4 py-2"
        >
          {{ isLoading ? "Lädt …" : "Filtern" }}
        </button>
      </div>
    </div>

    <!-- 📊 Tabelle -->
    <AuditLogTable :logs="logs" />

    <!-- 🔽 Pagination -->
    <div class="flex justify-between items-center text-white/70 pt-4">
      <button
        @click="prevPage"
        :disabled="page === 1 || isLoading"
        class="px-3 py-2 bg-white/10 rounded-lg hover:bg-white/20 disabled:opacity-50"
      >
        ← Zurück
      </button>

      <span>
        Seite {{ page }} / {{ Math.ceil(total / perPage) || 1 }}
      </span>

      <button
        @click="nextPage"
        :disabled="page * perPage >= total || isLoading"
        class="px-3 py-2 bg-white/10 rounded-lg hover:bg-white/20 disabled:opacity-50"
      >
        Weiter →
      </button>
    </div>
  </section>
</template>
