<script setup lang="ts">
import { ref, onMounted } from "vue"
import { useHrStats } from "@/composables/useHrStats"
import KpiCard from "@/components/KpiCard.vue"
import DonutDepartments from "@/components/charts/DonutDepartments.vue"
import HRDepartmentEmployees from "@/components/HRDepartmentEmployees.vue"

const {
  kpis,
  departmentsData,
  loading,
  error,
  lastUpdated,
  fetchHrOverview,
  fetchHrReport,
} = useHrStats()

const selectedDepartment = ref<string | null>(null)
const exporting = ref(false)

function onDepartmentSelect(label: string) {
  selectedDepartment.value = label
}

async function handleExport(format: "csv" | "json") {
  exporting.value = true
  try {
    await fetchHrReport(format)
  } finally {
    exporting.value = false
  }
}

onMounted(fetchHrOverview)
</script>

<template>
  <div class="hr-dashboard">
    <!-- 🧭 HEADER -->
    <header
      class="p-6 mb-10 rounded-xl bg-white/10 backdrop-blur-md border border-white/20 shadow-lg flex flex-col gap-3"
    >
      <div class="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 class="text-2xl font-semibold text-white tracking-tight flex items-center gap-2">
            <span class="w-2 h-2 bg-[var(--color-accent)] rounded-full"></span>
            HR Dashboard
          </h1>
          <p class="text-white/60">Überblick über Mitarbeiter, Abteilungen und Dokumente</p>
          <p v-if="lastUpdated" class="text-xs text-white/40">
            Stand: {{ new Date(lastUpdated).toLocaleString("de-DE") }}
          </p>
        </div>

        <!-- 📤 Export-Buttons -->
        <div class="flex items-center gap-3">
          <button
            :disabled="exporting"
            @click="handleExport('csv')"
            class="export-btn accent"
          >
            <span v-if="!exporting">📤 CSV Export</span>
            <span v-else>⏳ Exportiere…</span>
          </button>

          <button
            :disabled="exporting"
            @click="handleExport('json')"
            class="export-btn secondary"
          >
            <span v-if="!exporting">🧾 JSON Export</span>
            <span v-else>⏳ Exportiere…</span>
          </button>
        </div>
      </div>
    </header>

    <!-- 📦 Lade- & Fehlerzustände -->
    <div v-if="loading" class="state">📦 Lade HR-Daten…</div>
    <div v-else-if="error" class="state error">{{ error }}</div>

    <!-- 💡 Keine Daten -->
    <div v-else-if="!kpis.length && !departmentsData.length" class="state">
      Keine HR-Daten gefunden.
    </div>

    <template v-else>
      <!-- 📊 KPI-CARDS -->
      <section>
        <div
          class="grid gap-8 mt-10 sm:grid-cols-2 xl:grid-cols-4 grid-cols-[repeat(auto-fit,minmax(260px,1fr))]"
        >
          <KpiCard
            v-for="k in kpis"
            :key="k.label"
            :title="k.label"
            :value="k.value"
          />
        </div>
      </section>

      <!-- 🧩 DEPARTMENTS -->
      <section class="mt-14 space-y-6">
        <h2 class="text-lg font-semibold mb-5 text-white flex items-center gap-2 tracking-tight">
          <span class="w-2 h-2 bg-[var(--color-accent)] rounded-full"></span>
          Abteilungsübersicht
        </h2>

        <div class="card glass">
          <DonutDepartments
            :data="departmentsData"
            @slice-click="onDepartmentSelect"
          />
        </div>

        <transition name="fade" mode="out-in">
          <div
            v-if="selectedDepartment"
            key="dept"
            class="card glass highlight"
          >
            <div class="dept-header">
              <h3>{{ selectedDepartment }}</h3>
              <button @click="selectedDepartment = null">✕</button>
            </div>
            <HRDepartmentEmployees
              :department="selectedDepartment"
              @clear="selectedDepartment = null"
            />
          </div>

          <div
            v-else
            key="hint"
            class="card glass text-center text-white/60 py-10"
          >
            <span class="text-sm"
              >Wähle eine Abteilung, um Mitarbeiter anzuzeigen</span
            >
          </div>
        </transition>
      </section>
    </template>
  </div>
</template>

<style scoped>
.hr-dashboard {
  @apply min-h-screen overflow-y-auto px-8 pb-32 pt-[calc(72px+2rem)] flex flex-col gap-10;
}

/* Lade- & Fehlerzustände */
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

/* Karten */
.card {
  border-radius: 1rem;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(27, 29, 37, 0.85);
  box-shadow:
    0 8px 24px rgba(0, 0, 0, 0.4),
    0 0 30px rgba(255, 145, 0, 0.05);
  transition: transform 0.25s ease, box-shadow 0.25s ease;
  padding: 1.75rem;
}
.card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 18px rgba(255, 145, 0, 0.15);
}
.card.glass {
  backdrop-filter: blur(10px);
}
.card.highlight {
  border-color: rgba(255, 145, 0, 0.5);
  box-shadow: 0 0 20px rgba(255, 145, 0, 0.3);
}

/* Dept Header */
.dept-header {
  @apply flex items-center justify-between mb-4;
}
.dept-header h3 {
  @apply text-lg font-semibold text-white tracking-tight;
}
.dept-header button {
  @apply w-8 h-8 flex items-center justify-center rounded-full bg-white/10 text-white text-lg hover:bg-white/15 transition;
}

/* Export Buttons */
.export-btn {
  @apply px-4 py-2 rounded-lg font-semibold text-sm transition shadow-sm disabled:opacity-50 disabled:cursor-not-allowed;
}
.export-btn.accent {
  @apply bg-[var(--color-accent)] text-black hover:bg-orange-400 shadow-[0_0_15px_rgba(255,145,0,0.3)];
}
.export-btn.secondary {
  @apply bg-white/10 border border-white/20 text-white hover:bg-white/15;
}
</style>
